# Copyright (c) 2026 Komesu, D.K.
# Licensed under the MIT License.

"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import concurrent.futures
from pathlib import Path
from typing import Annotated

import typer
from quantilica.core.cli import (
    ProgressPool,
    get_console,
    graceful_executor,
    make_batch_progress,
    make_download_progress,
    setup_rich_logging,
)
from rich.console import Group
from rich.live import Live
from rich.rule import Rule
from rich.table import Table

from tesouro_direto_fetcher import downloader
from tesouro_direto_fetcher.constants import (
    DATASET_BUYBACKS,
    DATASET_INVESTORS,
    DATASET_MINT_STOCK,
    DATASET_OPERATIONS,
    DATASET_PRICES_RATES,
    DATASET_SALES,
)
from tesouro_direto_fetcher.storage import DataRepository

app = typer.Typer(help="Dados do Tesouro Direto (preços, taxas, operações).")


_DEFAULT_OUTPUT = Path("/data/tesouro-direto")
console = get_console()

_DATASET_MAP = {
    "prices": DATASET_PRICES_RATES,
    "operations": DATASET_OPERATIONS,
    "investors": DATASET_INVESTORS,
    "stock": DATASET_MINT_STOCK,
    "buybacks": DATASET_BUYBACKS,
    "sales": DATASET_SALES,
}
_DATASET_CHOICES = [*_DATASET_MAP, "all"]


def _resolve_ids(name: str) -> list[str]:
    if name == "all":
        return list(_DATASET_MAP.values())
    return [_DATASET_MAP[name]]


def _print_info(info_list: list[dict]) -> None:
    t = Table(show_header=True, header_style="bold")
    t.add_column("Arquivo", style="cyan")
    t.add_column("Tamanho", justify="right")
    t.add_column("Download?", justify="center")

    for info in info_list:
        size_str = f"{info['size']:,} bytes" if info["size"] else "desconhecido"
        flag = (
            "[green]Sim[/green]"
            if info["would_download"]
            else "[dim]Não (atualizado)[/dim]"
        )
        t.add_row(info["filename"], size_str, flag)

    console.print(f"Encontrados [bold]{len(info_list)}[/bold] recursos:")
    console.print(t)


@app.command("sync")
def cmd_sync(
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
    dataset: Annotated[
        str,
        typer.Option(
            "--dataset",
            help=f"Dataset ({', '.join(_DATASET_CHOICES)})",
        ),
    ] = "all",
    workers: Annotated[
        int, typer.Option("--workers", help="Downloads concorrentes")
    ] = 4,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Listar sem baixar")
    ] = False,
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Sincronizar datasets do Tesouro Direto."""
    setup_rich_logging(verbose, console=console)
    if dataset not in _DATASET_CHOICES:
        console.print(
            f"[red]Erro:[/red] dataset inválido '{dataset}'."
            f" Opções: {', '.join(_DATASET_CHOICES)}"
        )
        raise typer.Exit(1)

    if dry_run:
        if dataset == "all":
            for ds_name, ds_id in _DATASET_MAP.items():
                console.rule(
                    f"[bold cyan]{ds_name}[/bold cyan]",
                    style="cyan dim",
                )
                info_list = downloader.get_download_info(output, dataset_id=ds_id)
                _print_info(info_list)
        else:
            info_list = downloader.get_download_info(
                output, dataset_id=_DATASET_MAP[dataset]
            )
            _print_info(info_list)
        return

    repo = DataRepository(output)
    entries = []

    for dataset_id in _resolve_ids(dataset):
        try:
            resources = downloader.get_dataset_resources(dataset_id)
            remote_res = downloader._to_remote_resources(resources, repo)
            for r in remote_res:
                entries.append((dataset_id, r))
        except Exception as exc:
            console.print(f"[red]Erro obtendo recursos para {dataset_id}: {exc}[/red]")
            continue

    total = len(entries)
    if total == 0:
        console.print("[yellow]Nenhum recurso encontrado.[/yellow]")
        return

    overall = make_batch_progress(console)
    file_prog = make_download_progress(console)
    overall_task = overall.add_task("[cyan]Baixando...[/cyan]", total=total)

    downloaded = 0
    errors: list[tuple[str, str]] = []
    pool = ProgressPool(workers=workers, file_prog=file_prog)

    def _worker(item: tuple[str, downloader.RemoteResource]) -> bool:
        ds_id, res = item
        try:
            with pool.acquire(description=f"[cyan]{res.name}[/cyan]") as cb:
                result = downloader.download_file(res, ds_id, repo, progress=cb)
                return result is not None
        except Exception as exc:
            errors.append((res.name, str(exc)))
            return False

    with graceful_executor(max_workers=workers) as executor:
        try:
            with Live(
                Group(overall, file_prog), console=console, refresh_per_second=10
            ):
                futures = {executor.submit(_worker, item): item for item in entries}
                for future in concurrent.futures.as_completed(futures):
                    overall.update(overall_task, advance=1)
                    if future.result():
                        downloaded += 1
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrompido.[/yellow]")
            raise typer.Exit(130) from None

    console.print(
        f"\n[green]Concluído:[/green] {downloaded}/{total} arquivo(s) baixado(s)."
    )
    if errors:
        console.print(f"[red]{len(errors)} erro(s):[/red]")
        for eid, emsg in errors:
            console.print(f"  {eid}: {emsg}")


@app.command("convert")
def cmd_convert(
    data_dir: Annotated[
        Path,
        typer.Argument(help="Diretório de dados (raiz da árvore <dataset_id>/)"),
    ],
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Converter CSVs mais recentes para Parquet (requer extras de análise)."""
    setup_rich_logging(verbose, console=console)
    _convert_dir(data_dir)


def _convert_dir(data_dir: Path) -> None:
    """Converter os CSVs mais recentes de ``data_dir`` para Parquet."""
    try:
        from tesouro_direto_fetcher import converter
    except ImportError:
        console.print(
            "[red]Erro:[/red] convert requer extras de análise:"
            " pip install tesouro-direto-fetcher[analysis]"
        )
        raise typer.Exit(1) from None

    if not data_dir.is_dir():
        console.print(f"[red]Erro:[/red] diretório '{data_dir}' não existe.")
        raise typer.Exit(1)

    repo = DataRepository(data_dir)
    for dataset_id in repo.list_datasets():
        for fp in repo.get_all_latest_files(dataset_id):
            output_path = converter.convert_to_parquet(fp)
            console.print(f"  [green]✓[/green] {fp.name} → {output_path.name}")


@app.command("pipeline")
def cmd_pipeline(
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
    dataset: Annotated[
        str,
        typer.Option(
            "--dataset",
            help=f"Dataset ({', '.join(_DATASET_CHOICES)})",
        ),
    ] = "all",
    workers: Annotated[
        int, typer.Option("--workers", help="Downloads concorrentes")
    ] = 4,
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Pipeline completo do Tesouro Direto (sync → convert)."""
    setup_rich_logging(verbose, console=console)
    if dataset not in _DATASET_CHOICES:
        console.print(
            f"[red]Erro:[/red] dataset inválido '{dataset}'."
            f" Opções: {', '.join(_DATASET_CHOICES)}"
        )
        raise typer.Exit(1)

    console.print(Rule("[bold]Passo 1/2: Sincronização[/bold]"))

    repo = DataRepository(output)
    entries = []

    for dataset_id in _resolve_ids(dataset):
        try:
            resources = downloader.get_dataset_resources(dataset_id)
            remote_res = downloader._to_remote_resources(resources, repo)
            for r in remote_res:
                entries.append((dataset_id, r))
        except Exception as exc:
            console.print(f"[red]Erro obtendo recursos para {dataset_id}: {exc}[/red]")
            continue

    total = len(entries)
    if total > 0:
        overall = make_batch_progress(console)
        file_prog = make_download_progress(console)
        overall_task = overall.add_task("[cyan]Baixando...[/cyan]", total=total)

        pool = ProgressPool(workers=workers, file_prog=file_prog)

        def _worker(item: tuple[str, downloader.RemoteResource]) -> bool:
            ds_id, res = item
            try:
                with pool.acquire(description=f"[cyan]{res.name}[/cyan]") as cb:
                    result = downloader.download_file(res, ds_id, repo, progress=cb)
                    return result is not None
            except Exception:
                return False

        with graceful_executor(max_workers=workers) as executor:
            try:
                with Live(
                    Group(overall, file_prog), console=console, refresh_per_second=10
                ):
                    futures = {executor.submit(_worker, item): item for item in entries}
                    for _future in concurrent.futures.as_completed(futures):
                        overall.update(overall_task, advance=1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrompido.[/yellow]")
                raise typer.Exit(130) from None

    console.print("[green]✓[/green] Sincronização concluída.")

    console.print(Rule("[bold]Passo 2/2: Conversão[/bold]"))
    _convert_dir(output)
    console.print("[green]✓[/green] Conversão concluída.")

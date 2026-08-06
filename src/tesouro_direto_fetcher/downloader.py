"""Functions to download Tesouro Direto's historical data"""

from pathlib import Path

import quantilica.core.metadata as core_meta
from quantilica.core.exceptions import FetchError
from quantilica.core.fetcher import RemoteResource, download_resources
from quantilica.core.http import BROWSER_HEADERS, AsyncHttpClient
from quantilica.core.logging import log_step
from quantilica.core.progress import batch_progress

try:
    from quantilica.core.cli import get_console

    _RICH_AVAILABLE = True
except (ModuleNotFoundError, ImportError):
    _RICH_AVAILABLE = False

from . import logger
from .constants import CKAN_API_URL
from .storage import DataRepository

SOURCE_ID = "tesouro-direto"
CATALOG_DATASET_ID = "tesouro-direto-venda"

client = AsyncHttpClient(timeout=60.0, headers=BROWSER_HEADERS)


async def get_dataset_resources(dataset_id: str) -> list[dict]:
    """Fetch resources metadata from CKAN dataset asynchronously."""
    params = {"id": dataset_id}
    data = await client.get_json(CKAN_API_URL, params=params)
    if not data["success"]:
        raise FetchError(f"CKAN API failed: {data.get('error')}")
    return data["result"]["resources"]


async def get_download_info(dest_dir: Path, dataset_id: str) -> list[dict]:
    """Describe what ``download(dest_dir, dataset_id)`` would do (no IO)."""
    repo = DataRepository(dest_dir)

    try:
        resources = await get_dataset_resources(dataset_id)
    except Exception as e:
        raise FetchError(f"Error fetching resources for {dataset_id}: {e}") from e

    info_list = []
    for resource in resources:
        if resource.get("format", "").upper() != "CSV":
            continue

        url = resource["url"]
        last_modified_str = resource.get("last_modified") or resource.get("created")
        filename = repo.generate_filename(resource["name"], last_modified_str)
        dest_filepath = repo.file_path(dataset_id, filename)

        slug = filename.partition("@")[0]
        latest_file = repo.get_latest_stamped_file(dataset_id, slug)

        try:
            file_size = int(resource.get("size") or 0)
        except (ValueError, TypeError):
            file_size = 0

        would_download = True
        if latest_file and file_size and latest_file.stat().st_size == file_size:
            would_download = False

        info_list.append(
            {
                "resource_name": resource.get("name", ""),
                "url": url,
                "filename": filename,
                "destination": str(dest_filepath),
                "size": file_size,
                "last_modified": last_modified_str,
                "format": resource.get("format", ""),
                "would_download": would_download,
                "latest_local": str(latest_file) if latest_file else None,
            }
        )

    return info_list


def _to_remote_resources(
    ckan_resources: list[dict], repo: DataRepository
) -> list[RemoteResource]:
    result = []
    for r in ckan_resources:
        if r.get("format", "").upper() != "CSV":
            continue
        last_modified = r.get("last_modified") or r.get("created")
        filename = repo.generate_filename(r["name"], last_modified)
        try:
            size = int(r.get("size") or 0)
        except (ValueError, TypeError):
            size = 0
        result.append(
            RemoteResource(
                name=r["name"],
                url=r["url"],
                filename=filename,
                size=size,
                format="CSV",
            )
        )
    return result


async def download(
    dest_dir: Path,
    dataset_id: str,
    workers: int = 4,
    show_progress: bool = True,
) -> list[dict]:
    """Download data files concurrently."""
    repo = DataRepository(dest_dir)

    try:
        resources = await get_dataset_resources(dataset_id)
    except Exception as e:
        logger.error(f"Error fetching resources for {dataset_id}: {e}")
        return []

    remote = _to_remote_resources(resources, repo)
    if not remote:
        if not show_progress:
            logger.info("No CSV resources found.")
        return []

    if not show_progress:
        with log_step(logger, "download-dataset", dataset_id=dataset_id):
            logger.info(f"Found {len(remote)} files. Starting download...")
            return await download_resources(
                remote,
                repo,
                dataset_id,
                client,
                source_id=SOURCE_ID,
                producer="tesouro-direto-fetcher",
                max_concurrency=workers,
                logger=logger,
            )

    if _RICH_AVAILABLE:
        import asyncio

        from quantilica.core.cli import make_download_progress

        console = get_console()
        sem = asyncio.Semaphore(workers)

        with make_download_progress(console=console) as progress:
            worker_task_ids = [
                progress.add_task("[dim]Inativo[/dim]", total=1) for _ in range(workers)
            ]
            available_tasks = worker_task_ids.copy()

            async def _download_file(res: RemoteResource) -> dict | None:
                dest = repo.dataset_path(dataset_id, res.filename)

                if res.size > 0:
                    slug = res.filename.partition("@")[0]
                    latest = repo.get_latest_stamped_file(dataset_id, slug, "csv")
                    if latest is not None and latest.stat().st_size == res.size:
                        logger.debug(f"Skipping {res.filename}: matching local copy")
                        return None

                task_id = None
                try:
                    async with sem:
                        task_id = available_tasks.pop(0)

                        progress.update(
                            task_id,
                            description=f"[cyan]{res.name}",
                            completed=0,
                            total=res.size or None,
                        )

                        def _on_progress(downloaded: int, total: int) -> None:
                            if downloaded == 0 and total == 0:
                                progress.update(task_id, completed=0)
                                return
                            progress.update(
                                task_id, completed=downloaded, total=total or None
                            )

                        await client.download_with_manifest(
                            res.url,
                            dest,
                            source_id=SOURCE_ID,
                            dataset_id=dataset_id,
                            producer="tesouro-direto-fetcher",
                            progress=_on_progress,
                        )
                    return {
                        "url": res.url,
                        "filename": res.filename,
                        "destination": dest,
                        "file_size": dest.stat().st_size,
                    }
                except Exception as exc:
                    logger.error(f"Failed to download {res.url}: {exc}")
                    if dest.exists():
                        try:
                            dest.unlink()
                        except OSError:
                            pass
                    return None
                finally:
                    if task_id is not None:
                        progress.update(
                            task_id,
                            description="[dim]Inativo[/dim]",
                            completed=0,
                            total=1,
                        )
                        available_tasks.append(task_id)

            tasks = [_download_file(r) for r in remote]
            results = await asyncio.gather(*tasks)
            return [r for r in results if r is not None]

    # Fallback to tqdm if rich is not available
    with batch_progress(dataset_id, total=len(remote)) as pbar:

        def _on_file_done_tqdm(result: dict | None) -> None:
            pbar.update(1)

        return await download_resources(
            remote,
            repo,
            dataset_id,
            client,
            source_id=SOURCE_ID,
            producer="tesouro-direto-fetcher",
            max_concurrency=workers,
            logger=logger,
            on_file_done=_on_file_done_tqdm,
        )


def generate_catalog(
    downloaded_files: list[dict],
) -> core_meta.MetadataCatalog:
    """Build a validated MetadataCatalog from Tesouro Direto downloads."""
    source = core_meta.Source(
        id=SOURCE_ID,
        name="Tesouro Direto",
        homepage_url="https://www.tesourodireto.com.br",
    )
    dataset = core_meta.Dataset(
        id=CATALOG_DATASET_ID,
        source_id=SOURCE_ID,
        name="Dados Históricos do Tesouro Direto",
    )
    resources = [
        core_meta.Resource(
            id=file["filename"].replace(".", "_").replace("@", "_"),
            dataset_id=CATALOG_DATASET_ID,
            name=file["filename"],
            url=file["url"],
            format="csv",
            path=str(file["destination"].absolute()),
            metadata={"size": file["file_size"]},
        )
        for file in downloaded_files
    ]
    return core_meta.build_simple_catalog(source, dataset, resources)

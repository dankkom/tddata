"""Command-line interface for tesouro-direto-fetcher."""

import sys

from quantilica.core.logging import configure_cli_logging

from .plugin import app


def main(argv: list[str] | None = None) -> None:
    # We still configure basic cli logging, but the new UI setup in plugin will handle rich logging.
    configure_cli_logging(verbose=False)
    
    # Typer apps usually read sys.argv by themselves if argv is not provided
    # However, if argv is provided (e.g. in tests), we need to handle it.
    if argv is None:
        argv = sys.argv[1:]
        
    try:
        # typer apps can be called directly
        app(argv)
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()

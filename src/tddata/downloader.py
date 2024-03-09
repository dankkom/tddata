"""Functions to download Tesouro Direto's historical data"""

import datetime as dt
import logging
from pathlib import Path

import httpx
from tqdm import tqdm


logger = logging.getLogger(__name__)
URL = (
    "https://www.tesourotransparente.gov.br"
    "/ckan"
    "/dataset"
    "/df56aa42-484a-4a59-8184-7676580c81e3"
    "/resource"
    "/796d2059-14e9-44e3-80c9-2d9e30b405c1"
    "/download"
    "/PrecoTaxaTesouroDireto.csv"
)


def download(dest_dir: Path) -> dict:
    """Download data file

    Args:
        dest_dir: The directory path to save the file

    Returns:
        dict: metadata for logging and analysis
    """

    url = URL

    dest_dir.mkdir(parents=True, exist_ok=True)

    # Start downloading file
    with httpx.stream("GET", url) as r:
        r.raise_for_status()

        # Get file size from Content-Range: bytes 0-11611172/11611173
        file_size = int(r.headers["Content-Range"].split("/")[1])

        # Get Last-Modified datetime. eg.: Sat, 02 Mar 2024 10:21:12 GMT
        last_modified = r.headers["Last-Modified"]
        last_modified = dt.datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")

        filename = f"tesouro-direto_{last_modified:%Y%m%d%H%M}.csv"
        dest_filepath = dest_dir / filename

        if dest_filepath.exists():
            logger.info("File already exists: %s", dest_filepath)
            return {
                "url": url,
                "filename": filename,
                "destination": dest_filepath,
                "file_size": file_size,
            }

        progressbar = tqdm(total=file_size, unit="B", unit_scale=True)
        with open(dest_filepath, "wb") as f:
            for chunk in r.iter_bytes(1024):
                f.write(chunk)
                progressbar.update(len(chunk))
        progressbar.close()

    return {
        "url": url,
        "filename": filename,
        "destination": dest_filepath,
        "file_size": file_size,
    }

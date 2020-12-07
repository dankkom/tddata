"""Functions to download Tesouro Direto's historical data"""


from functools import lru_cache
import logging
import os
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from .bonds import BONDS


logger = logging.getLogger(__name__)


def download(
        bond_name: str,
        year: int,
        dest_path: str,
        meta_url: str = "default") -> dict:
    """Download data file

    Args:
        bond_name: The name of the bond to download
        year: The year of the data to download
        dest_path: The directory path to save the file
        meta_url (optional): Alternative web page's URL where to get download
            links of data files

    Returns:
        dict: metadata for logging and analysis

    Raises:
        KeyError: If arguments bond_name or year aren't valid or not listed in
            TD's web page
    """
    logger.info(
        f"Starting download:\n  bond_name: {bond_name}\n  year: {year}\n"
        f"  dest_path: {dest_path}\n  meta_url: {meta_url}"
    )
    # Validate parameters
    if bond_name not in BONDS["metadata"]:
        raise KeyError(f"Invalid bond_name '{bond_name}'")
    elif year < BONDS["metadata"][bond_name]["start-year"]:
        raise KeyError(f"Invalid year '{year}'")

    # Get url from TD' web page, if not available raise KeyError
    if meta_url != "default":
        metadata = get_metadata(meta_url)
    else:
        metadata = get_metadata()
    try:
        url = metadata[bond_name][year]
        # Start downloading file
        filename = f"{bond_name}_{year}.xls"
        dest = os.path.join(dest_path, filename)
        file_size = download_file(url=url, dest=dest, create_path=True)
        return {
            "bond_name": bond_name,
            "year": year,
            "url": url,
            "filename": filename,
            "destination": dest,
            "file_size": file_size,
        }
    except KeyError:
        if bond_name not in metadata:
            raise KeyError(
                f"Bond name '{bond_name}' not found in Tesouro Direto's"
                f"web page: '{meta_url}'"
            )
        elif year not in metadata[bond_name]:
            raise KeyError(
                f"Year {year} of bond {bond_name} not found in "
                f"Tesouro Direto's web page: {meta_url}"
            )


def download_file(url: str, dest: str, create_path: bool = True) -> int:
    """Downloads a file and save in the file system

    Args:
        url: The file's URL to download
        dest: Path to save the file
        create_path: True to create the complete destination directory path

    Returns:
        int: Size in bytes of downloaded content
    """
    logger.info(
        f"Downloading file:\n  url: {url}\n  dest: {dest}\n"
        f"  create_path: {create_path}"
    )
    r = requests.get(url)
    file_size = int(r.headers["Content-Length"])
    if create_path:
        dest_path = os.path.dirname(dest)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
    with open(dest, "wb") as f:
        f.write(r.content)
    return file_size


@lru_cache(maxsize=100)
def get_metadata(
        url: str = "http://sisweb.tesouro.gov.br/apex/f?p=2031:2:0:::::"
) -> dict:
    """Returns metadata listing all URLs to download bonds' data files

    It downloads and scrapes TD's web page that lists all URLs links to data
    files, caching the result to prevent new requests in the same session

    Args:
        url: The URL of TD's web page listing all links
            to download data files

    Returns:
        dict: Metadata dictionary, with the first level keys representing bonds'
            names, the second level keys are years (int).
    """
    logger.info(
        f"Getting metadata:\n  url: {url}"
    )
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    b = soup.select_one(".bl-body")
    children = [child for child in b.children]
    year = None
    meta = {}
    for child in children:
        if child.name == "span":
            year = int(child.get_text().strip(" -"))
        if child.name == "a":
            name = child.get_text()
            item_url = urljoin(url, child.attrs["href"])
            if name not in meta:
                meta.update({name: {}})
            meta[name].update({year: item_url})
    return meta

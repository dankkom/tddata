"""Functions to download Tesouro Direto's historical data"""


from functools import lru_cache
import json
import os
from pkg_resources import resource_filename
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


bonds_path = resource_filename(
    "tddata",
    "bonds.json",
)
with open(bonds_path, "r", encoding="utf-8") as f:
    BONDS = json.load(f)


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
    # Validate parameters
    if bond_name.upper() not in BONDS["metadata"]:
        raise KeyError("Invalid bond_name %s", bond_name)
    elif year < BONDS["metadata"][bond_name]["start-year"]:
        raise KeyError("Invalid year %s", year)

    # Get url from TD' web page, if not available raise KeyError
    try:
        if meta_url != "default":
            metadata = get_metadata(meta_url)
        else:
            metadata = get_metadata()
        url = metadata[bond_name][year]
    except KeyError:
        if bond_name not in metadata:
            raise KeyError(
                "Bond name %s not found in Tesouro Direto's web page: %s",
                bond_name,
                meta_url,
            )
        elif year not in metadata[bond_name]:
            raise KeyError(
                "Year %s of bond %s not found in Tesouro Direto's web page: %s",
                year,
                bond_name,
                meta_url,
            )
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


def download_file(url: str, dest: str, create_path: bool = True) -> int:
    """Downloads a file and save in the file system

    Args:
        url: The file's URL to download
        dest: Path to save the file
        create_path: True to create the complete destination directory path

    Returns:
        int: Size in bytes of downloaded content
    """
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
        url: str = "https://sisweb.tesouro.gov.br/apex/f?p=2031:2:0::::"
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
            url = urljoin(url, child.attrs["href"])
            if name not in meta:
                meta.update({name: {}})
            meta[name].update({year: url})
    return meta
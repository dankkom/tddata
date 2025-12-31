# Copyright (C) 2020-2025 Daniel Kiyoyudi Komesu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Functions to download Tesouro Direto's historical data"""

import datetime as dt
import re
import unicodedata
from pathlib import Path
from typing import Dict, List

import httpx
from tqdm import tqdm

from .constants import CKAN_API_URL, HTTP_HEADERS


def slugify(value: str) -> str:
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def get_dataset_resources(dataset_id: str) -> List[Dict]:
    """Fetch resources metadata from CKAN dataset"""
    params = {"id": dataset_id}
    response = httpx.get(CKAN_API_URL, params=params, headers=HTTP_HEADERS)
    response.raise_for_status()
    data = response.json()
    if not data["success"]:
        raise ValueError(f"CKAN API failed: {data.get('error')}")
    return data["result"]["resources"]


def download(dest_dir: Path, dataset_id: str) -> List[Dict]:
    """Download data files

    Args:
        dest_dir: The directory path to save the file
        dataset_id: The CKAN dataset ID or name.

    Returns:
        List[Dict]: metadata for logging and analysis of downloaded files
    """

    dest_dir.mkdir(parents=True, exist_ok=True)

    resources = get_dataset_resources(dataset_id)
    downloaded_files = []

    for resource in resources:
        # Filter for CSV files only
        if resource.get("format", "").upper() != "CSV":
            continue

        url = resource["url"]

        # Determine filename
        # Pattern: <dataset-name>@<modified-timestamp-in-iso-8601-format>.csv
        # We use slugified resource name as <dataset-name> to ensure uniqueness within datasets

        name_slug = slugify(resource["name"])

        last_modified_str = resource.get("last_modified") or resource.get("created")
        if last_modified_str:
            try:
                # CKAN returns ISO format: 2025-12-04T12:59:45.172801
                timestamp = dt.datetime.fromisoformat(last_modified_str)

                # Compact ISO 8601 format: YYYYMMDDTHHMMSS
                timestamp_str = timestamp.strftime("%Y%m%dT%H%M%S")
            except ValueError:
                # Fallback to current time
                timestamp_str = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        else:
            timestamp_str = dt.datetime.now().strftime("%Y%m%dT%H%M%S")

        filename = f"{name_slug}@{timestamp_str}.csv"
        dest_filepath = dest_dir / filename

        # Check if file exists
        if dest_filepath.exists():
            print("File already exists:", dest_filepath)
            downloaded_files.append({
                "url": url,
                "filename": filename,
                "destination": dest_filepath,
                "file_size": resource.get("size"),
            })
            continue

        # Download
        print(f"Downloading {filename}...")
        try:
            with httpx.stream("GET", url, headers=HTTP_HEADERS, timeout=30.0) as r:
                r.raise_for_status()

                # Try to get size from header or resource metadata
                total_size = int(r.headers.get("Content-Length", 0))
                if total_size == 0 and resource.get("size"):
                     total_size = int(resource["size"])

                progressbar = tqdm(total=total_size, unit="B", unit_scale=True)
                with open(dest_filepath, "wb") as f:
                    for chunk in r.iter_bytes(1024):
                        f.write(chunk)
                        progressbar.update(len(chunk))
                progressbar.close()

            downloaded_files.append({
                "url": url,
                "filename": filename,
                "destination": dest_filepath,
                "file_size": total_size,
            })
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            # Clean up partial file
            if dest_filepath.exists():
                dest_filepath.unlink()

    return downloaded_files

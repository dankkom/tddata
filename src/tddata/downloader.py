"""Functions to download Tesouro Direto's historical data"""

import datetime as dt
from pathlib import Path
from typing import List, Dict
import unicodedata
import re

import httpx
from tqdm import tqdm

from .constants import CKAN_API_URL, HTTP_HEADERS


def slugify(value: str) -> str:
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
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
                # Parsing logic
                if "." in last_modified_str:
                     # Truncate microseconds for cleaner filename if desired, or keep them.
                     # User asked for ISO 8601.
                     timestamp = dt.datetime.fromisoformat(last_modified_str)
                else:
                     timestamp = dt.datetime.fromisoformat(last_modified_str)
                
                # Format: YYYY-MM-DDTHH:MM:SS (standard ISO)
                # However, colons might be problematic on some filesystems (Windows), 
                # but valid on Linux. User asked for ISO-8601.
                # We will keep strict ISO format.
                timestamp_str = timestamp.isoformat(timespec="seconds")
            except ValueError:
                # Fallback to current time or keep original string if it looks like a date?
                # If parsing fails, use a safe default
                timestamp_str = dt.datetime.now().isoformat(timespec="seconds")
        else:
             timestamp_str = dt.datetime.now().isoformat(timespec="seconds")

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

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


"""Utilities for file storage and naming conventions"""

import datetime as dt
import re
import unicodedata
from pathlib import Path
from typing import Dict, List


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


def generate_filename(name: str, last_modified: str | None = None) -> str:
    """Generate a standardized filename for a resource.

    Format: <slugified-name>@<timestamp>.csv
    Timestamp format: YYYYMMDDTHHMMSS (Compact ISO 8601)
    """
    name_slug = slugify(name)

    if last_modified:
        try:
            # CKAN returns ISO format: 2025-12-04T12:59:45.172801
            timestamp = dt.datetime.fromisoformat(last_modified)
            timestamp_str = timestamp.strftime("%Y%m%dT%H%M%S")
        except ValueError:
            # Fallback to current time
            timestamp_str = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    else:
        timestamp_str = dt.datetime.now().strftime("%Y%m%dT%H%M%S")

    return f"{name_slug}@{timestamp_str}.csv"


def get_latest_files(directory: Path) -> List[Path]:
    """
    Scan a directory and return only the latest version of each file group.

    Files are grouped by their slug (part before @).
    For files with year patterns (e.g. investors-2024), it keeps the latest
    version of that specific year file.
    """
    if not directory.exists():
        return []

    files_map: Dict[str, Path] = {}

    for file_path in directory.glob("*.csv"):
        name = file_path.name
        if "@" not in name:
            continue

        # Split into slug and timestamp
        parts = name.split("@")
        slug = "@".join(parts[:-1])
        timestamp_part = parts[-1].replace(".csv", "")

        # If we haven't seen this slug or if this file is newer
        if slug not in files_map:
            files_map[slug] = file_path
        else:
            # Compare timestamps
            current_best = files_map[slug]
            current_ts = current_best.name.split("@")[-1].replace(".csv", "")

            if timestamp_part > current_ts:
                files_map[slug] = file_path

    return sorted(list(files_map.values()))


def get_latest_file(data_dir: Path, pattern: str) -> Path:
    files = list(data_dir.glob(pattern))
    if not files:
        return None

    latest_file = None
    latest_ts = ""

    for f in files:
        if "@" not in f.name:
            continue

        parts = f.name.split("@")
        ts = parts[-1].replace(".csv", "")

        if ts > latest_ts:
            latest_ts = ts
            latest_file = f

    return latest_file

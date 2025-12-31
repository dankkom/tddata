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


import argparse
from pathlib import Path

from . import downloader
from .constants import (
    DATASET_BUYBACKS,
    DATASET_INVESTORS,
    DATASET_MINT_STOCK,
    DATASET_OPERATIONS,
    DATASET_PRICES_RATES,
    DATASET_SALES,
)


def set_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        "--data-dir",
        dest="output",
        default=Path("data"),
        type=Path,
    )
    parser.add_argument(
        "--dataset",
        choices=["prices", "operations", "investors", "stock", "buybacks", "sales"],
        default="prices",
        help="Dataset to download: 'prices', 'operations', 'investors', 'stock', 'buybacks' or 'sales'"
    )
    parser.add_argument("--verbose", action="store_true", default=False)
    return parser


def main():
    parser = set_parser()
    args = parser.parse_args()

    dataset_map = {
        "prices": DATASET_PRICES_RATES,
        "operations": DATASET_OPERATIONS,
        "investors": DATASET_INVESTORS,
        "stock": DATASET_MINT_STOCK,
        "buybacks": DATASET_BUYBACKS,
        "sales": DATASET_SALES,
    }

    downloader.download(args.output, dataset_id=dataset_map[args.dataset])

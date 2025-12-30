import argparse
from pathlib import Path

from . import downloader
from .constants import DATASET_PRICES_RATES, DATASET_OPERATIONS, DATASET_INVESTORS, DATASET_MINT_STOCK, DATASET_REDEMPTIONS, DATASET_SALES


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
        choices=["prices", "operations", "investors", "stock", "redemptions", "sales"],
        default="prices",
        help="Dataset to download: 'prices', 'operations', 'investors', 'stock', 'redemptions' or 'sales'"
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
        "redemptions": DATASET_REDEMPTIONS,
        "sales": DATASET_SALES,
    }

    downloader.download(args.output, dataset_id=dataset_map[args.dataset])

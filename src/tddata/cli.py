import argparse
from pathlib import Path

from . import downloader


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
    parser.add_argument("--verbose", action="store_true", default=False)
    return parser


def main():
    parser = set_parser()
    args = parser.parse_args()
    downloader.download(args.output)

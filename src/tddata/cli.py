import argparse
import logging
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


def set_logger(verbose):
    logger = logging.getLogger("tddata")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("tddata.log")
    if verbose:
        fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    if verbose:
        ch.setLevel(logging.DEBUG)
    fmtter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
    )
    fh.setFormatter(fmtter)
    ch.setFormatter(fmtter)
    logger.addHandler(fh)
    logger.addHandler(ch)


def main():
    parser = set_parser()
    args = parser.parse_args()
    set_logger(args.verbose)
    downloader.download(args.output)

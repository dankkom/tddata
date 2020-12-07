import argparse
import logging
import os

from . import download
from .bonds import BONDS


def expand_years(args_years):
    years = []
    for arg in args_years:
        if ":" in arg:
            start, end = arg.split(":")
            start, end = int(start), int(end)
            if start > end:
                years += list(range(start, end - 1, -1))
            else:
                years += list(range(start, end + 1))
        else:
            years.append(int(arg))
    return years


def normalize_bond_name(name):
    return BONDS["aliases"][name.lower()]


def set_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--name",
        dest="name",
        required=True,
    )
    parser.add_argument("years", nargs="+")
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        default=os.path.join(os.path.expanduser("~"), "DATA"),
    )
    parser.add_argument("--verbose", action="store_true", default=False)
    return parser


def set_logger(verbose):
    logger = logging.getLogger("tddata.downloader")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("td-download.log")
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
    bond_name = normalize_bond_name(args.name)
    years = expand_years(args.years)
    set_logger(args.verbose)
    for year in years:
        download(bond_name, year, args.output)

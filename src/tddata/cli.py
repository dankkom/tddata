import argparse
import logging
import os

from . import download


def set_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        default=os.path.join(os.path.expanduser("~"), "DATA"),
    )
    parser.add_argument("--verbose", action="store_true", default=False)
    return parser


def set_logger(verbose):
    logger = logging.getLogger("tddata")
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
    set_logger(args.verbose)
    download(args.output)

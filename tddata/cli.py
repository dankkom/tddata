import argparse
import json
import os
from pkg_resources import resource_filename

from . import download


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
    path = resource_filename("tddata", "bonds.json")
    with open(path, "r") as f:
        bonds = json.load(f)
    return bonds["aliases"][name.lower()]


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
    return parser


def main():
    parser = set_parser()
    args = parser.parse_args()
    bond_name = normalize_bond_name(args.name)
    years = expand_years(args.years)
    for year in years:
        download(bond_name, year, args.output)

"""Functions to read TD's data files, returning convenient, analyst friendly,
Pandas DataFrames

The DataFrame returned by these functions have the following column names and
types:

| Colmn Name   | type              |
| ------------ | ----------------- |
| RefDate      | datetime.datetime |
| BuyYield     | float             |
| SellYield    | float             |
| BuyPrice     | float             |
| SellPrice    | float             |
| BasePrice    | float             |
| MaturityDate | datetime.datetime |
| BondCode     | str               |
| BondName     | str               |
| BondSeries   | str               |
"""


import datetime
import itertools
import os

import pandas as pd
import xlrd

from .bonds import BONDS


def _get_row_data(row: list, datemode: int) -> tuple:
    """Process the data rows of TD's files

    Args:
        row: row returned by xlrd.sheet.Sheet.get_rows(), don't feed with header
            rows
        datemode: the integer of xlrd.book.Book.datemode to convert Microsoft's
            Excel dates to Python datetime.datetime() objects

    Returns:
        tuple: the row with values and dates
    """
    row = tuple(c.value for c in row if c.value != "")
    if isinstance(row[0], float):  # Date cell
        dtr = datetime.datetime(*xlrd.xldate_as_tuple(row[0], datemode))
    else:  # Text cell
        dtr = datetime.datetime.strptime(row[0], "%d/%m/%Y")
    return tuple((dtr, *row[1:]))


def _get_sheet_data(sh: xlrd.sheet.Sheet, datemode: int) -> pd.DataFrame:
    """Process a Microsoft Excel sheet, returning a Pandas DataFrame

    Args:
        sh: the sheet to be processed
        datemode: integer to pass as argument to _get_row_data()

    Returns:
        pd.DataFrame: all data in the given sheet with normalized names and
            types
    """
    maturity = sh.cell_value(0, 1)
    if isinstance(maturity, float):
        maturity = datetime.datetime(*xlrd.xldate_as_tuple(maturity, datemode))
    else:
        maturity = datetime.datetime.strptime(maturity, "%d/%m/%Y")
    bond, series = sh.name.rsplit(" ", maxsplit=1)
    bond = BONDS["aliases"][bond.replace("-", "").lower()]  # Fix bonds names
    header = tuple(c.value for c in sh.row(1) if c.value != "")
    rows = (r for r in itertools.islice(sh.get_rows(), 2, None)
            if r[1].ctype != 0 and r[1].value != "")
    data = (_get_row_data(row, datemode) for row in rows)
    df = pd.DataFrame.from_records(data, columns=header)
    df = df.assign(
        MaturityDate=maturity,
        BondCode=sh.name,
        BondName=bond,
        BondSeries=series,
    )
    return df


def read_file(filepath: str) -> pd.DataFrame:
    """Read a TD file

    Args:
        filepath: path for the data file

    Returns:
        pd.DataFrame
    """
    wb = xlrd.open_workbook(filepath)
    datemode = wb.datemode
    sheets = (wb.sheet_by_index(i) for i in range(wb.nsheets))
    df_tuple = (_get_sheet_data(sh, datemode) for sh in sheets)
    df = pd.concat(df_tuple, ignore_index=True)
    df = df.rename(columns=BONDS["columns-rename"])
    return df


def read_directory(directorypath: str) -> pd.DataFrame:
    """Read a TD data directory

    Args:
        directorypath:

    Returns:
        pd.DataFrame
    """
    files = (file.path for file in os.scandir(directorypath))
    df_tuple = (read_file(fp) for fp in files)
    df = pd.concat(
        df_tuple,
        ignore_index=True
    )
    return df


def read_tree(path: str) -> pd.DataFrame:
    """Read a TD data tree of directories

    Args:
        path:

    Returns:
        pd.DataFrame
    """
    df = pd.concat(
        (read_directory(f.path) for f in os.scandir(path) if f.is_dir()),
        ignore_index=True)
    return df

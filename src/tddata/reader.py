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

from pathlib import Path
import pandas as pd


def read(filepath: Path) -> pd.DataFrame:
    data = (
        pd.read_csv(
            filepath,
            sep=";",
            decimal=",",
            parse_dates=["Data Vencimento", "Data Base"],
            dayfirst=True,
        )
        .rename(
            columns={
                "Data Base": "RefDate",
                "Tipo Titulo": "BondName",
                "Data Vencimento": "MaturityDate",
                "Taxa Compra Manha": "BuyYield",
                "Taxa Venda Manha": "SellYield",
                "PU Compra Manha": "BuyPrice",
                "PU Venda Manha": "SellPrice",
                "PU Base Manha": "BasePrice",
            }
        )
        .assign(MaturityYear=lambda x: x["MaturityDate"].dt.year)
    )
    return data

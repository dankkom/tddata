"""Functions to read TD's data files, returning convenient, analyst friendly,
Pandas DataFrames

The DataFrame returned by these functions have the following column names and
types:

| Colmn Name     | type              |
|----------------|-------------------|
| reference_date | datetime.datetime |
| buy_yield      | float             |
| sell_yield     | float             |
| buy_price      | float             |
| sell_price     | float             |
| base_price     | float             |
| maturity_date  | datetime.datetime |
| bond_type      | str               |

"""

from pathlib import Path
import pandas as pd

from .constants import (
    REFERENCE_DATE_COLUMN,
    BOND_TYPE_COLUMN,
    MATURITY_DATE_COLUMN,
    BUY_YIELD_COLUMN,
    SELL_YIELD_COLUMN,
    BUY_PRICE_COLUMN,
    SELL_PRICE_COLUMN,
    BASE_PRICE_COLUMN,
)


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
                "Data Base": REFERENCE_DATE_COLUMN,
                "Tipo Titulo": BOND_TYPE_COLUMN,
                "Data Vencimento": MATURITY_DATE_COLUMN,
                "Taxa Compra Manha": BUY_YIELD_COLUMN,
                "Taxa Venda Manha": SELL_YIELD_COLUMN,
                "PU Compra Manha": BUY_PRICE_COLUMN,
                "PU Venda Manha": SELL_PRICE_COLUMN,
                "PU Base Manha": BASE_PRICE_COLUMN,
            }
        )
        .assign(MaturityYear=lambda x: x[MATURITY_DATE_COLUMN].dt.year)
    )
    return data

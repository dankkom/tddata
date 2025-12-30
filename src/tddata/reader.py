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

from .constants import Column


def read(filepath: Path) -> pd.DataFrame:
    data = pd.read_csv(
        filepath,
        sep=";",
        decimal=",",
        parse_dates=["Data Vencimento", "Data Base"],
        dayfirst=True,
    )
    data = data.rename(
        columns={
            "Data Base": Column.REFERENCE_DATE.value,
            "Tipo Titulo": Column.BOND_TYPE.value,
            "Data Vencimento": Column.MATURITY_DATE.value,
            "Taxa Compra Manha": Column.BUY_YIELD.value,
            "Taxa Venda Manha": Column.SELL_YIELD.value,
            "PU Compra Manha": Column.BUY_PRICE.value,
            "PU Venda Manha": Column.SELL_PRICE.value,
            "PU Base Manha": Column.BASE_PRICE.value,
        }
    )
    return data

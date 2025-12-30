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


def read_prices(filepath: Path) -> pd.DataFrame:
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


def read_stock(filepath: Path) -> pd.DataFrame:
    # 'Mes Estoque' is in format %m/%Y (e.g. 11/2021)
    # 'Vencimento do Titulo' is in format %d/%m/%Y
    # It's better to read as strings first and convert manually to avoid warnings/ambiguities
    data = pd.read_csv(
        filepath,
        sep=";",
        decimal=",",
    )
    data["Vencimento do Titulo"] = pd.to_datetime(data["Vencimento do Titulo"], dayfirst=True)
    data["Mes Estoque"] = pd.to_datetime(data["Mes Estoque"], format="%m/%Y")
    data = data.rename(
        columns={
            "Tipo Titulo": Column.BOND_TYPE.value,
            "Vencimento do Titulo": Column.MATURITY_DATE.value,
            "Mes Estoque": Column.STOCK_MONTH.value,
            "PU": Column.UNIT_PRICE.value,
            "Quantidade": Column.QUANTITY.value,
            "Valor Estoque": Column.STOCK_VALUE.value,
        }
    )
    return data


def read_investors(filepath: Path) -> pd.DataFrame:
    data = pd.read_csv(
        filepath,
        sep=";",
        parse_dates=["Data de Adesao"],
        dayfirst=True,
    )
    data = data.rename(
        columns={
            "Codigo do Investidor": Column.INVESTOR_ID.value,
            "Data de Adesao": Column.JOIN_DATE.value,
            "Estado Civil": Column.MARITAL_STATUS.value,
            "Genero": Column.GENDER.value,
            "Profissao": Column.PROFESSION.value,
            "Idade": Column.AGE.value,
            "UF do Investidor": Column.STATE.value,
            "Cidade do Investidor": Column.CITY.value,
            "Pais do Investidor": Column.COUNTRY.value,
            "Situacao da Conta": Column.ACCOUNT_STATUS.value,
            "Operou 12 Meses": Column.TRADED_LAST_12_MONTHS.value,
        }
    )
    return data


def read_operations(filepath: Path) -> pd.DataFrame:
    data = pd.read_csv(
        filepath,
        sep=";",
        decimal=",",
        parse_dates=["Data da Operacao", "Vencimento do Titulo"],
        dayfirst=True,
    )
    data = data.rename(
        columns={
            "Codigo do Investidor": Column.INVESTOR_ID.value,
            "Data da Operacao": Column.OPERATION_DATE.value,
            "Tipo Titulo": Column.BOND_TYPE.value,
            "Vencimento do Titulo": Column.MATURITY_DATE.value,
            "Quantidade": Column.QUANTITY.value,
            "Valor do Titulo": Column.BOND_VALUE.value,
            "Valor da Operacao": Column.OPERATION_VALUE.value,
            "Tipo da Operacao": Column.OPERATION_TYPE.value,
            "Canal da Operacao": Column.CHANNEL.value,
        }
    )
    return data


def read_sales(filepath: Path) -> pd.DataFrame:
    data = pd.read_csv(
        filepath,
        sep=";",
        decimal=",",
        parse_dates=["Vencimento do Titulo", "Data Venda"],
        dayfirst=True,
    )
    data = data.rename(
        columns={
            "Tipo Titulo": Column.BOND_TYPE.value,
            "Vencimento do Titulo": Column.MATURITY_DATE.value,
            "Data Venda": Column.SALE_DATE.value,
            "PU": Column.UNIT_PRICE.value,
            "Quantidade": Column.QUANTITY.value,
            "Valor": Column.VALUE.value,
        }
    )
    return data


def read_buybacks(filepath: Path) -> pd.DataFrame:
    data = pd.read_csv(
        filepath,
        sep=";",
        decimal=",",
        parse_dates=["Vencimento do Titulo", "Data Resgate"],
        dayfirst=True,
    )
    data = data.rename(
        columns={
            "Tipo Titulo": Column.BOND_TYPE.value,
            "Vencimento do Titulo": Column.MATURITY_DATE.value,
            "Data Resgate": Column.REDEMPTION_DATE.value,
            "Quantidade": Column.QUANTITY.value,
            "Valor": Column.VALUE.value,
        }
    )
    return data


def read_maturities(filepath: Path) -> pd.DataFrame:
    data = pd.read_csv(
        filepath,
        sep=";",
        decimal=",",
        parse_dates=["Vencimento do Titulo", "Data Resgate"],
        dayfirst=True,
    )
    data = data.rename(
        columns={
            "Tipo Titulo": Column.BOND_TYPE.value,
            "Vencimento do Titulo": Column.MATURITY_DATE.value,
            "Data Resgate": Column.REDEMPTION_DATE.value,
            "PU": Column.UNIT_PRICE.value,
            "Quantidade": Column.QUANTITY.value,
            "Valor": Column.VALUE.value,
        }
    )
    return data


def read_interest_coupons(filepath: Path) -> pd.DataFrame:
    return read_maturities(filepath)

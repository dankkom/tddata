# Copyright (C) 2020-2025 Daniel Kiyoyudi Komesu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Functions to read Tesouro Direto's data files.

This module provides functions to parse raw CSV files downloaded from the
Tesouro Transparente API into clean, analyst-friendly pandas DataFrames.
It handles column renaming (Portuguese to English), type conversion,
and data normalization using the schema defined in `constants.py`.

The DataFrames returned by these functions use standardized column names
defined in the `Column` enum.
"""

from pathlib import Path

import pandas as pd

from .constants import (
    AccountStatus,
    Channel,
    Column,
    Gender,
    TradedLast12Months,
    normalize_bond_type,
)


def read_prices(filepath: Path) -> pd.DataFrame:
    """Read bond prices and rates (Taxas e Preços dos Títulos).

    Parses the daily prices and yields for government bonds.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - reference_date: Date of the record
            - bond_type: Name of the bond (e.g., Tesouro Selic)
            - maturity_date: Maturity date of the bond
            - buy_yield: Yield for buying
            - sell_yield: Yield for selling
            - buy_price: Price for buying
            - sell_price: Price for selling
            - base_price: Base price
    """
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
    data[Column.BOND_TYPE.value] = data[Column.BOND_TYPE.value].apply(
        normalize_bond_type
    )
    return data


def read_stock(filepath: Path) -> pd.DataFrame:
    """Read bond stock (Estoque).

    Parses the monthly stock of government bonds.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - bond_type: Name of the bond
            - maturity_date: Maturity date of the bond
            - stock_month: Month of the stock record
            - unit_price: Unit price of the bond
            - quantity: Quantity of bonds in stock
            - stock_value: Total value of the stock
    """
    # 'Mes Estoque' is in format %m/%Y (e.g. 11/2021)
    # 'Vencimento do Titulo' is in format %d/%m/%Y
    # It's better to read as strings first and convert manually to avoid warnings/ambiguities
    data = pd.read_csv(
        filepath,
        sep=";",
        decimal=",",
    )
    data["Vencimento do Titulo"] = pd.to_datetime(
        data["Vencimento do Titulo"], dayfirst=True
    )
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
    data[Column.BOND_TYPE.value] = data[Column.BOND_TYPE.value].apply(
        normalize_bond_type
    )
    return data


def read_investors(filepath: Path) -> pd.DataFrame:
    """Read investors data (Investidores).

    Parses the list of investors registered in Tesouro Direto.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - investor_id: Unique identifier for the investor
            - join_date: Date the investor joined
            - marital_status: Marital status
            - gender: Gender (mapped to standardized values)
            - profession: Profession
            - age: Age
            - state: State (UF)
            - city: City
            - country: Country
            - account_status: Account status (Active/Deactivated)
            - traded_last_12_months: Whether traded in last 12 months
    """
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

    # Map categorical values to enum values for better semantics
    # Keep original values for MaritalStatus as they're already descriptive

    # Map gender codes to enum values
    gender_map = {e.value: e.value for e in Gender}
    data[Column.GENDER.value] = data[Column.GENDER.value].map(gender_map)

    # Map account status codes to enum values
    status_map = {e.value: e.value for e in AccountStatus}
    data[Column.ACCOUNT_STATUS.value] = data[Column.ACCOUNT_STATUS.value].map(
        status_map
    )

    # Map traded last 12 months codes to enum values
    traded_map = {e.value: e.value for e in TradedLast12Months}
    data[Column.TRADED_LAST_12_MONTHS.value] = data[
        Column.TRADED_LAST_12_MONTHS.value
    ].map(traded_map)

    return data


def read_operations(filepath: Path) -> pd.DataFrame:
    """Read operations data (Operações).

    Parses the history of buy/sell/custody operations.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - investor_id: Investor ID
            - operation_date: Date of the operation
            - bond_type: Bond type
            - maturity_date: Maturity date
            - quantity: Quantity traded
            - bond_value: Unit value of the bond
            - operation_value: Total value of the operation
            - operation_type: Type (Buy, Sell, etc.)
            - channel: Channel used (Site, Homebroker)
    """
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

    # Map channel codes to enum values
    channel_map = {e.value: e.value for e in Channel}
    data[Column.CHANNEL.value] = data[Column.CHANNEL.value].map(channel_map)

    data[Column.BOND_TYPE.value] = data[Column.BOND_TYPE.value].apply(
        normalize_bond_type
    )

    return data


def read_sales(filepath: Path) -> pd.DataFrame:
    """Read sales data (Vendas).

    Parses the history of bond sales (investments).

    Args:
        filepath: Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - bond_type: Bond type
            - maturity_date: Maturity date
            - sale_date: Date of the sale
            - unit_price: Unit price
            - quantity: Quantity sold
            - value: Total value
    """
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
    data[Column.BOND_TYPE.value] = data[Column.BOND_TYPE.value].apply(
        normalize_bond_type
    )
    return data


def read_buybacks(filepath: Path) -> pd.DataFrame:
    """Read buybacks data (Resgates).

    Parses the history of bond buybacks/redemptions.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - bond_type: Bond type
            - maturity_date: Maturity date
            - buyback_date: Date of the buyback
            - quantity: Quantity redeemed
            - value: Total value
    """
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
            "Data Resgate": Column.BUYBACK_DATE.value,
            "Quantidade": Column.QUANTITY.value,
            "Valor": Column.VALUE.value,
        }
    )
    data[Column.BOND_TYPE.value] = data[Column.BOND_TYPE.value].apply(
        normalize_bond_type
    )
    return data


def read_maturities(filepath: Path) -> pd.DataFrame:
    """Read maturities data (Vencimentos).

    Parses the history of bond maturities.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - bond_type: Bond type
            - maturity_date: Maturity date
            - buyback_date: Date of the maturity/redemption
            - unit_price: Unit price
            - quantity: Quantity matured
            - value: Total value
    """
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
            "Data Resgate": Column.BUYBACK_DATE.value,
            "PU": Column.UNIT_PRICE.value,
            "Quantidade": Column.QUANTITY.value,
            "Valor": Column.VALUE.value,
        }
    )
    data[Column.BOND_TYPE.value] = data[Column.BOND_TYPE.value].apply(
        normalize_bond_type
    )
    return data


def read_interest_coupons(filepath: Path) -> pd.DataFrame:
    """Read interest coupons data (Pagamento de Cupom de Juros).

    Parses the history of interest coupon payments.
    This file shares the same structure as the maturities file.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with columns similar to `read_maturities`.
    """
    return read_maturities(filepath)

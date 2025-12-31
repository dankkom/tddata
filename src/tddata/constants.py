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


import enum


# Columns' names are defined in the constants.py file, which is imported by the
# reader.py file. This is a good practice because it makes the code more
# maintainable. If the column names change, we only need to update the
# constants.py file, and the reader.py file will automatically use the new
# column names. This is a good example of the DRY (Don't Repeat Yourself)
# principle.
class Column(enum.Enum):
    """Column names for the Tesouro Direto data."""

    REFERENCE_DATE = "reference_date"
    BOND_TYPE = "bond_type"
    MATURITY_DATE = "maturity_date"
    BUY_YIELD = "buy_yield"
    SELL_YIELD = "sell_yield"
    BUY_PRICE = "buy_price"
    SELL_PRICE = "sell_price"
    BASE_PRICE = "base_price"

    # Stock (Estoque)
    STOCK_MONTH = "stock_month"
    QUANTITY = "quantity"
    STOCK_VALUE = "stock_value"

    # Investors (Investidores)
    INVESTOR_ID = "investor_id"
    JOIN_DATE = "join_date"
    MARITAL_STATUS = "marital_status"
    GENDER = "gender"
    PROFESSION = "profession"
    AGE = "age"
    STATE = "state"
    CITY = "city"
    COUNTRY = "country"
    ACCOUNT_STATUS = "account_status"
    TRADED_LAST_12_MONTHS = "traded_last_12_months"

    # Operations (Operacoes)
    OPERATION_DATE = "operation_date"
    BOND_VALUE = "bond_value"
    OPERATION_VALUE = "operation_value"
    OPERATION_TYPE = "operation_type"
    CHANNEL = "channel"

    # Common / Others
    BUYBACK_DATE = "buyback_date"
    VALUE = "value"
    SALE_DATE = "sale_date"
    UNIT_PRICE = "unit_price"


class BondType(enum.Enum):
    """Bond types for the Tesouro Direto data."""

    # Tesouro Prefixado (LTN)
    PREFIXED = "Tesouro Prefixado"

    # Tesouro Prefixado com Juros Semestrais (NTN-F)
    PREFIXED_WITH_SEMESTRAL_INTEREST = "Prefixado com Juros Semestrais"

    # Tesouro IPCA+ (NTN-B Principal)
    IPCA = "Tesouro IPCA+"

    # Tesouro IPCA+ com Juros Semestrais (NTN-B)
    IPCA_WITH_SEMESTRAL_INTEREST = "Tesouro IPCA+ com Juros Semestrais"

    # Tesouro Selic (LFT)
    SELIC = "Tesouro Selic"

    # Tesouro IGPM+ com Juros Semestrais (NTN-C)
    IGPM_WITH_SEMESTRAL_INTEREST = "Tesouro IGPM+ com Juros Semestrais"

    # Tesouro RendA+
    RENDA = "Tesouro RendA+"

    # Tesouro EducA+
    EDUCA = "Tesouro EducA+"


class OperationType(enum.Enum):
    """Operation types for the Tesouro Direto data."""

    BUY = "C"
    SELL = "V"
    WITHDRAWAL = "R"
    DEPOSIT = "D"

    @classmethod
    def get_labels(cls):
        return {
            cls.BUY.value: "Compra",
            cls.SELL.value: "Venda",
            cls.WITHDRAWAL.value: "Retirada",
            cls.DEPOSIT.value: "Depósito",
        }


class Channel(enum.Enum):
    """Channel types for Tesouro Direto operations."""

    SITE = "S"
    HOMEBROKER = "H"

    @classmethod
    def get_labels(cls):
        return {
            cls.SITE.value: "Site",
            cls.HOMEBROKER.value: "Homebroker",
        }


class MaritalStatus(enum.Enum):
    """Marital status for Tesouro Direto investors."""

    SINGLE = "Solteiro(a)"
    SEPARATED = "Desquitado(a)"
    WIDOWED = "Viúvo(a)"
    DIVORCED = "Divorciado(a)"
    MARRIED_BRAZILIAN_NATIVE = "Casado(a) com brasileiro(a) nato(a)"
    MARRIED_BRAZILIAN_NATURALIZED = "Casado(a) com brasileiro(a) naturalizado(a)"
    MARRIED_FOREIGNER = "Casado(a) com estrangeiro(a)"
    STABLE_UNION = "União estável"
    LEGALLY_SEPARATED = "Separado judic."
    NOT_APPLICABLE = "Não se aplica"


class Gender(enum.Enum):
    """Gender for Tesouro Direto investors."""

    MALE = "M"
    FEMALE = "F"
    NOT_APPLICABLE = "N"

    @classmethod
    def get_labels(cls):
        return {
            cls.MALE.value: "Masculino",
            cls.FEMALE.value: "Feminino",
            cls.NOT_APPLICABLE.value: "Não se aplica",
        }


class AccountStatus(enum.Enum):
    """Account status for Tesouro Direto investors."""

    ACTIVE = "A"
    DEACTIVATED = "D"

    @classmethod
    def get_labels(cls):
        return {
            cls.ACTIVE.value: "Ativo",
            cls.DEACTIVATED.value: "Desativado",
        }


class TradedLast12Months(enum.Enum):
    """Traded in last 12 months for Tesouro Direto investors."""

    YES = "S"
    NO = "N"

    @classmethod
    def get_labels(cls):
        return {
            cls.YES.value: "Sim",
            cls.NO.value: "Não",
        }


CKAN_API_URL = "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show"

DATASET_PRICES_RATES = "taxas-dos-titulos-ofertados-pelo-tesouro-direto"
DATASET_OPERATIONS = "operacoes-do-tesouro-direto"
DATASET_INVESTORS = "investidores-do-tesouro-direto"
DATASET_MINT_STOCK = "estoque-do-tesouro-direto"
DATASET_BUYBACKS = "resgates-do-tesouro-direto"
DATASET_SALES = "vendas-do-tesouro-direto"

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 "
        "Safari/537.3"
    ),
}

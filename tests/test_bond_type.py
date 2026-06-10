"""Tests for bond type normalization and NTN-B1 disambiguation."""

from datetime import date

from tesouro_direto_fetcher.constants import Column as C
from tesouro_direto_fetcher.constants import (
    is_renda_maturity,
    normalize_bond_type,
    resolve_bond_type,
)
from tesouro_direto_fetcher.reader import read_operations

OPERATIONS_HEADER = (
    "Codigo do Investidor;Data da Operacao;Tipo Titulo;Vencimento do Titulo;"
    "Quantidade;Valor do Titulo;Valor da Operacao;Tipo da Operacao;"
    "Canal da Operacao"
)


def test_is_renda_maturity():
    # RendA+ final maturities: Dec 15 of 2049 + 5k
    assert is_renda_maturity(date(2049, 12, 15))
    assert is_renda_maturity(date(2054, 12, 15))
    assert is_renda_maturity(date(2084, 12, 15))
    # EducA+ vintages and off-pattern dates
    assert not is_renda_maturity(date(2034, 12, 15))
    assert not is_renda_maturity(date(2048, 12, 15))
    assert not is_renda_maturity(date(2050, 12, 15))
    assert not is_renda_maturity(date(2049, 12, 14))
    assert not is_renda_maturity(date(2049, 11, 15))


def test_resolve_bond_type_ntnb1():
    assert resolve_bond_type("NTN-B1", date(2049, 12, 15)) == "Tesouro RendA+"
    assert resolve_bond_type("ntn-b1", date(2054, 12, 15)) == "Tesouro RendA+"
    assert resolve_bond_type("NTN-B1", date(2034, 12, 15)) == "Tesouro EducA+"
    assert resolve_bond_type("NTN-B1", None) is None


def test_resolve_bond_type_named_types():
    assert (
        resolve_bond_type("Tesouro Renda+ Aposentadoria Extra", date(2034, 12, 15))
        == "Tesouro RendA+"
    )
    assert resolve_bond_type("Tesouro Educa+", None) == "Tesouro EducA+"
    assert resolve_bond_type("Tesouro Selic", None) == "Tesouro Selic"


def test_normalize_bond_type_no_longer_maps_ntnb1():
    # NTN-B1 cannot be resolved by name alone; it passes through unchanged
    assert normalize_bond_type("NTN-B1") == "NTN-B1"


def test_read_operations_disambiguates_ntnb1(tmp_path):
    rows = [
        OPERATIONS_HEADER,
        "54;10/01/2025;NTN-B1;15/12/2034;1,00;1526,29;1526,29;C;S",
        "54;10/01/2025;NTN-B1;15/12/2054;1,00;1526,29;1526,29;C;S",
        "54;10/01/2025;Tesouro Selic;01/03/2027;1,00;100,00;100,00;C;S",
    ]
    filepath = tmp_path / "operations.csv"
    filepath.write_text("\n".join(rows) + "\n", encoding="utf-8")

    df = read_operations(filepath)

    bond_types = df[C.BOND_TYPE.value].to_list()
    assert bond_types == ["Tesouro EducA+", "Tesouro RendA+", "Tesouro Selic"]

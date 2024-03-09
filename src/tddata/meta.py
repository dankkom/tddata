datasets = {
    "Taxas dos Títulos Ofertados pelo Tesouro Direto": {
        "homepage": "https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1",
        "url": "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv",
    },
}
bonds = {
    "aliases": {
        "tesouro prefixado": "LTN",
        "ltn": "LTN",
        "tesouro prefixado com juros semestrais": "NTN-F",
        "ntn-f": "NTN-F",
        "ntnf": "NTN-F",
        "tesouro ipca+": "NTN-B Principal",
        "ntn-b principal": "NTN-B Principal",
        "ntnbp": "NTN-B Principal",
        "ntnb princ": "NTN-B Principal",
        "ntnb principal": "NTN-B Principal",
        "tesouro ipca+ com juros semestrais": "NTN-B",
        "ntn-b": "NTN-B",
        "ntnb": "NTN-B",
        "tesouro selic": "LFT",
        "lft": "LFT",
        "tesouro igpm+ com juros semestrais": "NTN-C",
        "ntn-c": "NTN-C",
        "ntnc": "NTN-C",
    },
    "metadata": {
        "LFT": {"start-year": 2002},
        "LTN": {"start-year": 2002},
        "NTN-C": {"start-year": 2002},
        "NTN-B": {"start-year": 2003},
        "NTN-B Principal": {"start-year": 2005},
        "NTN-F": {"start-year": 2004},
    },
    "columns-rename": {
        "Dia": "RefDate",
        "Taxa Compra Manhã": "BuyYield",
        "Taxa Compra 9:00": "BuyYield",
        "Taxa Venda Manhã": "SellYield",
        "Taxa Venda 9:00": "SellYield",
        "PU Compra 9:00": "BuyPrice",
        "PU Compra Manhã": "BuyPrice",
        "PU Venda 9:00": "SellPrice",
        "PU Venda Manhã": "SellPrice",
        "PU Base 9:00": "BasePrice",
        "PU Base Manhã": "BasePrice",
        "PU Extrato 9:00": "BasePrice",
    },
    "description": (
        "This JSON provides some metadata about bonds and other helping " "information."
    ),
}

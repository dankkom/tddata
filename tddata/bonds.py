BONDS = {
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
        "ntnc": "NTN-C"
    },
    "metadata": {
        "LFT": {
            "start-year": 2002
        },
        "LTN": {
            "start-year": 2002
        },
        "NTN-C": {
            "start-year": 2002
        },
        "NTN-B": {
            "start-year": 2003
        },
        "NTN-B Principal": {
            "start-year": 2005
        },
        "NTN-F": {
            "start-year": 2004
        }
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
        "PU Extrato 9:00": "BasePrice"
    },
    "description": (
        "This JSON provides some metadata about bonds and other helping "
        "information."),
}

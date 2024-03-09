# Columns' names are defined in the constants.py file, which is imported by the
# reader.py file. This is a good practice because it makes the code more
# maintainable. If the column names change, we only need to update the
# constants.py file, and the reader.py file will automatically use the new
# column names. This is a good example of the DRY (Don't Repeat Yourself)
# principle.

REFERENCE_DATE_COLUMN = "reference_date"
BOND_TYPE_COLUMN = "bond_type"
MATURITY_DATE_COLUMN = "maturity_date"
BUY_YIELD_COLUMN = "buy_yield"
SELL_YIELD_COLUMN = "sell_yield"
BUY_PRICE_COLUMN = "buy_price"
SELL_PRICE_COLUMN = "sell_price"
BASE_PRICE_COLUMN = "base_price"

# CSV file URL to download
CSV_URL = (
    "https://www.tesourotransparente.gov.br"
    "/ckan"
    "/dataset"
    "/df56aa42-484a-4a59-8184-7676580c81e3"
    "/resource"
    "/796d2059-14e9-44e3-80c9-2d9e30b405c1"
    "/download"
    "/PrecoTaxaTesouroDireto.csv"
)

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 "
        "Safari/537.3"
    ),
}

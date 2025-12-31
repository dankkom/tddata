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


from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from tddata import downloader, plot, reader
from tddata.constants import Column

# Set the style of the plot
sns.set_theme(style="ticks")
plt.rcParams["axes.labelsize"] = 8
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["xtick.labelsize"] = 8
plt.rcParams["ytick.labelsize"] = 8
plt.rcParams["legend.fontsize"] = 8

DATA_DIR = Path("/home/dell/data/tddata")
PLOTS_DIR = Path("plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def get_latest_file(pattern: str) -> Path:
    files = list(DATA_DIR.glob(pattern))
    if not files:
        return None
    return sorted(files)[-1]


def save_plot(fig, filename):
    filepath = PLOTS_DIR / filename
    print(f"Saving {filepath}...")
    fig.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close(fig)


def run_prices():
    f = get_latest_file("taxas-dos-titulos-ofertados*.csv")
    if not f:
        print("No prices file found.")
        return

    print(f"Loading prices from {f.name}...")
    data = reader.read_prices(f)

    variables = [
        Column.BUY_PRICE.value,
        Column.BUY_YIELD.value,
        Column.SELL_PRICE.value,
        Column.SELL_YIELD.value,
        Column.BASE_PRICE.value,
    ]

    for bond_type in data[Column.BOND_TYPE.value].unique():
        # Clean filename friendly bond type
        bond_slug = downloader.slugify(bond_type)
        for var in variables:
            print(f"  Plotting {bond_type} - {var}...")
            try:
                fig = plot.plot_prices(data, bond_type, var)
                save_plot(fig, f"prices_{bond_slug}_{var}.png")
            except Exception as e:
                print(f"  Error plotting {bond_type} {var}: {e}")


def run_stock():
    f = get_latest_file("estoque-do-tesouro-direto*.csv")
    if not f:
        print("No stock file found.")
        return

    print(f"Loading stock from {f.name}...")
    data = reader.read_stock(f)

    print("  Plotting stock evolution by bond type...")
    fig = plot.plot_stock(data, by_bond_type=True)
    save_plot(fig, "stock_evolution_by_type.png")

    print("  Plotting total stock evolution...")
    fig = plot.plot_stock(data, by_bond_type=False)
    save_plot(fig, "stock_evolution_total.png")


def run_investors():
    # Load all investors files
    pattern = "investidores-do-tesouro-direto-*.csv"
    files = sorted(list(DATA_DIR.glob(pattern)))
    if not files:
        print("No investors file found.")
        return

    print(f"Loading {len(files)} investors files...")
    # Use the last file for demographics (latest snapshot)
    latest_file = files[-1]
    data_latest = reader.read_investors(latest_file)

    demographics = [
        Column.STATE.value,
        Column.GENDER.value,
        Column.PROFESSION.value,
        Column.MARITAL_STATUS.value,
        Column.AGE.value,
    ]

    for demo in demographics:
        if demo == Column.AGE:
            continue
        print(f"  Plotting demographics: {demo}...")

        kind = "bar"
        if demo == Column.GENDER.value:
            kind = "pie"
        elif demo in [Column.PROFESSION.value, Column.MARITAL_STATUS.value]:
            kind = "barh"

        fig = plot.plot_investors_demographics(
            data_latest, column=demo, chart_type=kind
        )
        save_plot(fig, f"investors_demographics_{demo}.png")

    print("  Aggregating data for investors evolution...")

    all_data = []
    for f in files:
        print(f"    Reading {f.name}...")
        df = reader.read_investors(f)
        all_data.append(df)

    if all_data:
        full_data = pd.concat(all_data, ignore_index=True)
        full_data = full_data.drop_duplicates(
            subset=[Column.INVESTOR_ID.value, Column.JOIN_DATE.value]
        )
        # Drop dates before 2000
        full_data = full_data[full_data[Column.JOIN_DATE.value] >= "2000-01-01"]

        print("  Plotting new investors evolution (all history)...")

        fig = plot.plot_investors_evolution(full_data, freq="ME")
        save_plot(fig, "investors_new_evolution_history.png")


def run_operations():
    pattern = "operacoes-do-tesouro-direto-*.csv"
    files = sorted(list(DATA_DIR.glob(pattern)))
    if not files:
        print("No operations file found.")
        return

    print(f"Loading {len(files)} operations files for evolution...")
    all_data = []
    for f in files:
        print(f"    Reading {f.name}...")
        df = reader.read_operations(f)
        all_data.append(df)

    if all_data:
        full_data = pd.concat(all_data, ignore_index=True)
        print("  Plotting operations by type (all history)...")
        fig = plot.plot_operations(full_data, by_type=True)
        save_plot(fig, "operations_evolution_by_type_history.png")


def run_sales():
    f = get_latest_file("vendas-do-tesouro-direto-*.csv")
    if not f:
        print("No sales file found.")
        return

    print(f"Loading sales from {f.name}...")
    data = reader.read_sales(f)

    print("  Plotting sales by bond type...")
    fig = plot.plot_sales(data, by_bond_type=True)
    save_plot(fig, "sales_evolution_by_type.png")


def run_buybacks():
    f = get_latest_file("recompras-do-tesouro-direto*.csv")
    if not f:
        print("No buybacks file found.")
        return

    print(f"Loading buybacks from {f.name}...")
    data = reader.read_buybacks(f)

    print("  Plotting buybacks by bond type...")
    fig = plot.plot_buybacks(data, by_bond_type=True)
    save_plot(fig, "buybacks_evolution_by_type.png")


def run_maturities():
    f = get_latest_file("vencimentos-do-tesouro-direto*.csv")
    if not f:
        print("No maturities file found.")
        return

    print(f"Loading maturities from {f.name}...")
    data = reader.read_maturities(f)

    print("  Plotting maturities by bond type...")
    fig = plot.plot_maturities(data, by_bond_type=True)
    save_plot(fig, "maturities_evolution_by_type.png")


def run_interest_coupons():
    f = get_latest_file("pagamento-de-cupom-de-juros-do-tesouro-direto*.csv")
    if not f:
        print("No interest coupons file found.")
        return

    print(f"Loading interest coupons from {f.name}...")
    data = reader.read_interest_coupons(f)

    print("  Plotting interest coupons by bond type...")
    fig = plot.plot_interest_coupons(data, by_bond_type=True)
    save_plot(fig, "interest_coupons_evolution_by_type.png")


def main():
    print("Starting plot generation...")
    run_prices()
    run_stock()
    run_investors()
    run_operations()
    run_sales()
    run_buybacks()
    run_maturities()
    run_interest_coupons()
    print("Done!")


if __name__ == "__main__":
    main()

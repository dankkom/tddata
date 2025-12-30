import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .constants import Column


def plot_timeseries(data: pd.DataFrame, bond_type: str, variable: str):
    subset = data[
        (data[Column.BOND_TYPE.value] == bond_type)
        & (data[Column.BUY_PRICE.value] > 0)
        & (data[Column.SELL_PRICE.value] > 0)
    ]
    # Sort the data by maturity date
    subset = subset.sort_values(
        by=[Column.MATURITY_DATE.value, Column.REFERENCE_DATE.value]
    )
    variable_description = ""
    if variable == Column.BUY_YIELD.value:
        variable_description = "Buy Yield (%)"
    elif variable == Column.SELL_YIELD.value:
        variable_description = "Sell Yield (%)"
    elif variable == Column.BUY_PRICE.value:
        variable_description = "Buy Price (R$)"
    elif variable == Column.SELL_PRICE.value:
        variable_description = "Sell Price (R$)"
    elif variable == Column.BASE_PRICE.value:
        variable_description = "Base Price (R$)"
    f, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=subset,
        x=Column.REFERENCE_DATE.value,
        y=variable,
        hue=Column.MATURITY_DATE.value,
        estimator=None,
        ax=ax,
        palette="viridis",
        legend="full",
        linewidth=1,
    )
    ax.set_title(f"Tesouro Direto | {bond_type} | {variable_description}")
    ax.set_xlabel("Date")
    ax.set_ylabel(f"{variable_description}")
    # Legend title and position
    handles, labels = ax.get_legend_handles_labels()
    handles = handles
    # Format the maturity dates in the legend as %b/%Y
    labels = [pd.to_datetime(label).strftime("%b/%Y") for label in labels]

    # If there are more than 10 labels, show only a subset of them
    n_labels = len(labels)
    if n_labels > 10:
        step = n_labels // 10
        labels = labels[::step]
        handles = handles[::step]

    ax.legend(
        handles=handles,
        labels=labels,
        title="Maturity",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )
    # Add text with the data source at the bottom left of the figure
    f.text(
        0.01,
        0.01,
        "Data source: Tesouro Direto",
        horizontalalignment="left",
        fontsize=8,
        color="gray",
    )
    # Grid off
    sns.despine(ax=ax)
    f.tight_layout()
    return f

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns

from .constants import Column


def human_format(num, pos):
    """
    Format large numbers with suffixes (K, M, B, T).
    Use generic logic for both currency and counts.
    """
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # Add more suffixes if you need
    suffixes = ["", "K", "M", "B", "T"]
    if magnitude < len(suffixes):
        return f"{num:.1f}{suffixes[magnitude]}"
    return f"{num:.1f}E{magnitude}"


def plot_prices(data: pd.DataFrame, bond_type: str, variable: str):
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

    # Format Y axis
    if "Yield" not in variable_description:
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(human_format))

    # Legend title and position
    handles, labels = ax.get_legend_handles_labels()

    # Format the maturity dates in the legend as %b/%Y
    # Ensure labels are parsed as datetime if they aren't already string-formatted well
    # But seaborn/matplotlib sometimes return different things in labels depending on version.
    # We will try to be safe.
    new_labels = []
    for label in labels:
        try:
            new_labels.append(pd.to_datetime(label).strftime("%b/%Y"))
        except Exception:
            new_labels.append(str(label))
    labels = new_labels

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
    _add_footer(f)
    # Grid off
    sns.despine(ax=ax)
    f.tight_layout()
    return f


def plot_stock(data: pd.DataFrame, by_bond_type: bool = True):
    """Plot the evolution of the Stock Value."""
    f, ax = plt.subplots(figsize=(10, 6))

    if by_bond_type:
        # Group by month and bond type
        df_grouped = (
            data.groupby([Column.STOCK_MONTH.value, Column.BOND_TYPE.value])[
                Column.STOCK_VALUE.value
            ]
            .sum()
            .reset_index()
        )

        sns.lineplot(
            data=df_grouped,
            x=Column.STOCK_MONTH.value,
            y=Column.STOCK_VALUE.value,
            hue=Column.BOND_TYPE.value,
            ax=ax,
        )
    else:
        df_grouped = (
            data.groupby([Column.STOCK_MONTH.value])[Column.STOCK_VALUE.value]
            .sum()
            .reset_index()
        )
        sns.lineplot(
            data=df_grouped,
            x=Column.STOCK_MONTH.value,
            y=Column.STOCK_VALUE.value,
            ax=ax,
        )

    ax.set_title("Tesouro Direto Stock Value Evolution")
    ax.set_ylabel("Stock Value (R$)")
    ax.set_xlabel("Date")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(human_format))
    _add_footer(f)
    sns.despine(ax=ax)
    f.tight_layout()
    return f


def plot_investors_demographics(
    data: pd.DataFrame,
    column: str = Column.STATE.value,
    top_n: int = 15,
    chart_type: str = "bar",
):
    """Plot distribution of investors by a categorical column (State, Gender, etc)."""
    f, ax = plt.subplots(figsize=(10, 6))

    # Count frequency
    counts = data[column].value_counts().head(top_n)

    human_col = _humanize_label(column)

    if chart_type == "pie":
        ax.pie(
            counts.values,
            labels=counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=sns.color_palette("viridis", len(counts)),
        )
        # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.axis("equal")
    elif chart_type == "barh":
        sns.barplot(
            x=counts.values,
            y=counts.index,
            hue=counts.index,
            palette="viridis",
            legend=False,
            ax=ax,
        )
        ax.set_xlabel("Count")
        ax.set_ylabel(human_col)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(human_format))

        # Wrap long labels
        import textwrap

        max_width = 30
        new_labels = [
            textwrap.fill(str(label), width=max_width) for label in counts.index
        ]
        ax.set_yticklabels(new_labels)

        sns.despine(ax=ax)
    else:
        sns.barplot(
            x=counts.index,
            y=counts.values,
            hue=counts.index,
            palette="viridis",
            legend=False,
            ax=ax,
        )
        ax.set_ylabel("Count")
        ax.set_xlabel(human_col)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(human_format))
        plt.xticks(rotation=45)
        sns.despine(ax=ax)

    ax.set_title(f"Investors Distribution by {human_col}")
    _add_footer(f)
    f.tight_layout()
    return f


def plot_investors_evolution(data: pd.DataFrame, freq: str = "ME"):
    """Plot the number of new investors over time."""
    f, ax = plt.subplots(figsize=(10, 6))

    # Resample by frequency
    # Assuming JOIN_DATE is datetime
    resampled = (
        data.set_index(Column.JOIN_DATE.value)
        .resample(freq)
        .size()
        .reset_index(name="new_investors")
    )

    sns.lineplot(data=resampled, x=Column.JOIN_DATE.value, y="new_investors", ax=ax)

    ax.set_title("New Investors Over Time")
    ax.set_ylabel("Number of New Investors")
    ax.set_xlabel("Date")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(human_format))
    _add_footer(f)
    sns.despine(ax=ax)
    f.tight_layout()
    return f


def plot_operations(data: pd.DataFrame, by_type: bool = True):
    """Plot operations value over time."""
    f, ax = plt.subplots(figsize=(10, 6))

    # Operations can be big, better aggregate by month
    data["month"] = (
        data[Column.OPERATION_DATE.value].dt.to_period("M").dt.to_timestamp()
    )

    if by_type:
        grouped = (
            data.groupby(["month", Column.OPERATION_TYPE.value])[
                Column.OPERATION_VALUE.value
            ]
            .sum()
            .reset_index()
        )
        sns.lineplot(
            data=grouped,
            x="month",
            y=Column.OPERATION_VALUE.value,
            hue=Column.OPERATION_TYPE.value,
            ax=ax,
        )
    else:
        grouped = (
            data.groupby("month")[Column.OPERATION_VALUE.value].sum().reset_index()
        )
        sns.lineplot(data=grouped, x="month", y=Column.OPERATION_VALUE.value, ax=ax)

    ax.set_title("Operations Volume Over Time")
    ax.set_ylabel("Total Value (R$)")
    ax.set_xlabel("Date")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(human_format))
    _add_footer(f)
    sns.despine(ax=ax)
    f.tight_layout()
    return f


def plot_sales(data: pd.DataFrame, by_bond_type: bool = True):
    """Plot sales value over time."""
    return _plot_value_over_time(
        data,
        date_col=Column.SALE_DATE.value,
        value_col=Column.VALUE.value,
        title="Sales Volume Over Time",
        hue_col=Column.BOND_TYPE.value if by_bond_type else None,
    )


def plot_buybacks(data: pd.DataFrame, by_bond_type: bool = True):
    """Plot buybacks (redemptions) value over time."""
    return _plot_value_over_time(
        data,
        date_col=Column.BUYBACK_DATE.value,
        value_col=Column.VALUE.value,
        title="Buybacks Volume Over Time",
        hue_col=Column.BOND_TYPE.value if by_bond_type else None,
    )


def _plot_value_over_time(
    data: pd.DataFrame, date_col: str, value_col: str, title: str, hue_col: str = None
):
    f, ax = plt.subplots(figsize=(10, 6))

    # Aggregate by month to make plot readable
    # Create a copy to avoid SettingWithCopyWarning on the original dataframe
    df = data.copy()
    df["month"] = df[date_col].dt.to_period("M").dt.to_timestamp()

    if hue_col:
        grouped = df.groupby(["month", hue_col])[value_col].sum().reset_index()
        sns.lineplot(data=grouped, x="month", y=value_col, hue=hue_col, ax=ax)
    else:
        grouped = df.groupby("month")[value_col].sum().reset_index()
        sns.lineplot(data=grouped, x="month", y=value_col, ax=ax)

    ax.set_title(title)
    ax.set_ylabel("Value (R$)")
    ax.set_xlabel("Date")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(human_format))
    _add_footer(f)
    sns.despine(ax=ax)
    f.tight_layout()
    return f


def _add_footer(fig):
    fig.text(
        0.01,
        0.01,
        "Data source: Tesouro Direto",
        horizontalalignment="left",
        fontsize=8,
        color="gray",
    )


def _humanize_label(label: str) -> str:
    return label.replace("_", " ").title()

import matplotlib.pyplot as plt
import seaborn as sns

from tddata.reader import read


data = read("data/tesouro-direto_202403021021.csv")
data = data[data["reference_date"] >= "2022-01-01"]
data = data.assign(maturity_year=lambda x: x["maturity_date"].dt.year)
print(data)

sns.set_theme(style="ticks")
plt.rcParams["axes.labelsize"] = 8
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["xtick.labelsize"] = 8
plt.rcParams["ytick.labelsize"] = 8
plt.rcParams["legend.fontsize"] = 8


tipo_titulo = "Tesouro Prefixado"
f, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(
    data=data[data["bond_type"] == tipo_titulo],
    x="reference_date",
    y="sell_yield",
    hue="maturity_year",
    estimator=None,
    ax=ax,
    palette="viridis",
    legend="full",
    linewidth=1.5,
)
ax.set_title(f"Tesouro Direto - {tipo_titulo} - Daily Sell Yield")
ax.set_xlabel("Date")
ax.set_ylabel("Sell Yield (%)")
# Legend position
ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
# Grid off
sns.despine(ax=ax)
f.tight_layout()
# Add text with the data source at the bottom left of the figure
plt.figtext(
    0.01,
    0.01,
    "Data source: Tesouro Direto",
    horizontalalignment="left",
    fontsize=8,
    color="gray",
)
plt.savefig(f"plots/plot1.png", dpi=300)
plt.close()

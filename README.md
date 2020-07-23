# tddata - easly download & read brazilian Tesouro Direto's data

![GitHub](https://img.shields.io/github/license/dkkomesu/tddata?style=flat-square) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/dkkomesu/tddata/tests?style=flat-square) ![Coveralls github](https://img.shields.io/coveralls/github/dkkomesu/tddata?style=flat-square)

tddata is a simple Python package to download and read Brazil's bonds data from Tesouro Direto program.

## 1. Install

Clone this repository and pip install.

As simple as that! :)

```shell
git clone https://github.com/dkkomesu/tddata
cd tddata
pip install tddata
```

## 2. Usage

### 2.1 The `td-download` CLI utility

This package comes with a Command - Line Interface(CLI) that makes downloading Tesouro Direto's data easier.

The syntax is as follows:

```
td-download {bond_name} {year} [-o|--output OUTPUT/DIRECTORY/PATH]
```

### 2.2 The `tddata` Python package

Import the package with:

```python
import tddata
```

Before you start to work the data, you need to download it to your local machine.

```python
# Download LFT bond data from years 2002-2020 and save at ~/DATA/TD/LFT
# The file is saved with the following name pattern: {bond_name}_{year}.xls
for year in range(2002, 2021):
    tddata.download(bond_name="LFT", year=year, dest_path="~/DATA/TD/LFT")
```

Now you can read the data. Because the data in these downloaded files aren't in a data scientist aware format, `tddata` provides functions to read it correctly.

The most basic is `read_file()` that reads only one file at a time:

```python
# Read data file of LFT bond from year 2019
lft2019 = tddata.read_file("~/DATA/TD/LFT/LFT_2019.xls")
```

The functions `read_directory()` and `read_tree` reads an entire directory and an entire tree of directories respectively, returning all data in one Pandas DataFrame.

```python
# Read data directory
lft = tddata.read_directory("~/DATA/TD/LFT")

# Read data tree directory recursively
td = tdtddata.read_tree("~/DATA/TD")
```

## 3. Examples

In the example below we plot the daily yields of LTN bonds from 2016-01-01 to 2020-05-05

```python
import matplotlib.pyplot as plt
import seaborn as sns

import tddata


ltn = tddata.read_directory("/DATA/TD/LTN")

# Filter data by date and create a new column with the bond's year of maturity
ltn = ltn[ltn["RefDate"] >= "2016-01-01"]
ltn = ltn.assign(
	MaturityYear=ltn["RefDate"].dt.year,
)

# Now plot the data with matplotlib and seaborn
# With the hue argument we plot each year of maturity by a diferent lines and colors
f, ax = plt.subplots()
f.set_size_inches(16, 8)
sns.lineplot(
	x="RefDate",
	y="YieldSell",
	hue="MaturityYear",
	ax=ax,
	data=ltn,
	palette="viridis",
    legend="full",
)
ax.set_title("LTN Daily Yield")
ax.set_xlabel("Date")
ax.set_ylabel("Yield")
plt.tight_layout()
plt.show()
```

![Chart showing LTN daily rates](plots/plot1.png)

## 4. License

This project is licensed under the MIT License.

See LICENSE to see the full text.

---

Data Source: all data are downloaded from [STN]("https://sisweb.tesouro.gov.br/apex/f?p=2031:2:0::::").

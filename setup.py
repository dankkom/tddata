import setuptools

import tddata


description = "Easy Python data downloader & reader of brazilian Tesouro Direto"

with open("README.md", "r") as f:
    long_description = f.read()

url = "https://github.com/dkkomesu/tddata"

package_data = {
    "tddata": [
        "bonds.json"
    ],
}

classifiers = [
    "Programming Language :: Python",
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
]

entry_points = {
    "console_scripts": ["td-download=tddata.cli:main"],
}

setuptools.setup(
    name="tddata",
    version=tddata.__version__,
    url=url,
    license="MIT",
    author=tddata.__author__,
    author_email=tddata.__author_email__,
    description=description,
    long_description=long_description,
    packages=setuptools.find_packages(),
    package_data=package_data,
    classifiers=classifiers,
    entry_points=entry_points,
)

import codecs
import os
import setuptools


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


version = get_version("tddata/__init__.py")

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

install_requires = [
    "beautifulsoup4>=4.9.0",
    "lxml>=4.5.0",
    "pandas>=1.0.3",
    "xlrd>=1.2.0",
    "requests",
]

setuptools.setup(
    name="tddata",
    version=version,
    url=url,
    license="MIT",
    author="Daniel Komesu",
    author_email="contact@dkko.me",
    description=description,
    long_description=long_description,
    packages=setuptools.find_packages(),
    package_data=package_data,
    install_requires=install_requires,
    classifiers=classifiers,
    entry_points=entry_points,
)

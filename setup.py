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

url = "https://github.com/dankkom/tddata"

classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
]

entry_points = {
    "console_scripts": ["td-download=tddata.cli:main"],
}

install_requires = [
    "beautifulsoup4",
    "lxml",
    "pandas",
    "xlrd",
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
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=classifiers,
    entry_points=entry_points,
)

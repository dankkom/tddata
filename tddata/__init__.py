"""
tddata - easy brazilian bonds daily prices data from Tesouro Direto


"""


__author__ = "Daniel Komesu"
__author_email__ = "danielkomesu@gmail.com"
__version__ = "0.1.0"

__all__ = [
    "download",
    "read_file",
    "read_directory",
    "read_tree",
]


from .downloader import download
from .reader import read_file, read_directory, read_tree

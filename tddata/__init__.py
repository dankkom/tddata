"""
tddata - easy brazilian bonds daily prices data from Tesouro Direto


"""


__version__ = "0.1.1"

__all__ = [
    "download",
    "read_file",
    "read_directory",
    "read_tree",
]


from .downloader import download
from .reader import read_file, read_directory, read_tree

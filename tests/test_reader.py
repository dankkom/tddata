import unittest
from unittest import mock

from tddata import reader


class TestReader(unittest.TestCase):

    def test_get_row_data(self):
        row = [mock.MagicMock() for _ in range(6)]
        row[0].value = "01/01/2010"
        reader._get_row_data(row, 1)
        row = [mock.MagicMock() for _ in range(6)]
        row[0].value = 1234.5
        reader._get_row_data(row, 1)


if __name__ == "__main__":
    unittest.main()

import os
import unittest
from unittest import mock

from tddata import cli


class TestFunctions(unittest.TestCase):

    def test_expand_years(self):
        self.assertListEqual(
            cli.expand_years(["2010", "2019"]),
            [2010, 2019]
        )
        self.assertListEqual(
            cli.expand_years(["2010:2019"]),
            list(range(2010, 2019+1))
        )
        self.assertListEqual(
            cli.expand_years(["2020:2015"]),
            list(range(2020, 2015-1, -1))
        )
        self.assertListEqual(
            cli.expand_years(["2020:2015", "2001", "2003:2009"]),
            list(range(2020, 2015-1, -1)) + [2001] + list(range(2003, 2009+1))
        )

    def test_normalize_bond_name(self):
        self.assertEqual(
            cli.normalize_bond_name("lft"),
            "LFT",
        )
        self.assertEqual(
            cli.normalize_bond_name("ntnb"),
            "NTN-B",
        )
        self.assertEqual(
            cli.normalize_bond_name("ntnb principal"),
            "NTN-B Principal",
        )
        self.assertEqual(
            cli.normalize_bond_name("ntnf"),
            "NTN-F",
        )

    def test_set_parser(self):
        parser = cli.set_parser()
        args = parser.parse_args("-n lft 2010".split())
        self.assertEqual(args.name, "lft")
        self.assertListEqual(args.years, ["2010"])
        args = parser.parse_args("-n ntnb 2010:2015 2020".split())
        self.assertEqual(args.name, "ntnb")
        self.assertListEqual(args.years, ["2010:2015", "2020"])
        args = parser.parse_args("2010:2015 2020 -n lft".split())
        self.assertEqual(args.name, "lft")
        self.assertListEqual(args.years, ["2010:2015", "2020"])
        args = parser.parse_args("-o ./DATA 2010:2015 2020 -n lft".split())
        self.assertEqual(args.name, "lft")
        self.assertEqual(args.output, "./DATA")
        self.assertListEqual(args.years, ["2010:2015", "2020"])

    @mock.patch("tddata.cli.download")
    @mock.patch("tddata.cli.set_parser")
    def test_main(self, mock_set_parser, mock_download):
        parser = mock_set_parser.return_value
        args = mock.MagicMock()
        parser.parse_args.return_value = args
        args.name = "lft"
        args.years = ["2019"]
        args.output = "./DATA"
        cli.main()
        mock_set_parser.assert_called()
        mock_download.assert_called_with("LFT", 2019, "./DATA")


if __name__ == "__main__":
    unittest.main()

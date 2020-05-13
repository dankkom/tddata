import unittest
from unittest import mock

from tddata import downloader


class TestDownloader(unittest.TestCase):

    def test_get_metadata(self):
        meta = downloader.get_metadata()
        self.assertIsInstance(meta, dict)
        self.assertGreater(len(meta), 0)
        self.assertGreater(len(meta), 0)
        self.assertIn("LFT", meta.keys())
        self.assertGreater(len(meta["LFT"]), 0)
        self.assertIn("NTN-B", meta.keys())
        self.assertGreater(len(meta["NTN-B"]), 0)
        self.assertIn("NTN-B Principal", meta.keys())
        self.assertGreater(len(meta["NTN-B Principal"]), 0)
        self.assertIn("NTN-C", meta.keys())
        self.assertGreater(len(meta["NTN-C"]), 0)
        self.assertIn("NTN-F", meta.keys())
        self.assertGreater(len(meta["NTN-F"]), 0)
        self.assertIn("LTN", meta.keys())
        self.assertGreater(len(meta["LTN"]), 0)

    @mock.mock_open()
    @mock.patch("tddatapy.downloader.os")
    @mock.patch("tddatapy.downloader.requests.get")
    @mock.patch("tddatapy.downloader.get_metadata")
    def test_download(
            self,
            mock_get_metadata,
            mock_requests_get,
            mock_os,
            mock_open):
        mock_get_metadata.return_value = {
            "LFT": {
                "2020": "https://example.com/lft",
            },
        }
        r = mock.MagicMock()
        r.headers = {"Content-Length": "1000"}
        mock_requests_get.return_value = r
        mock_os.path.exists.return_value = True
        downloader.download("LFT", 2020, "./DATA")
        mock_get_metadata.asset_called()


if __name__ == "__main__":
    unittest.main()

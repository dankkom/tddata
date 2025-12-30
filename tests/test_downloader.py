
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from tddata import downloader


class TestDownloader(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_slugify(self):
        self.assertEqual(downloader.slugify("Tesouro Selic"), "tesouro-selic")
        self.assertEqual(downloader.slugify("Ação & Reação"), "acao-reacao")
        self.assertEqual(downloader.slugify("  Spaces  "), "spaces")
        self.assertEqual(downloader.slugify("Mixed_CASE"), "mixed_case")

    @patch("tddata.downloader.httpx.get")
    def test_get_dataset_resources(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "resources": [
                    {"name": "Resource 1", "format": "CSV"},
                    {"name": "Resource 2", "format": "PDF"}
                ]
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        resources = downloader.get_dataset_resources("fake-id")
        self.assertEqual(len(resources), 2)
        self.assertEqual(resources[0]["name"], "Resource 1")

    @patch("tddata.downloader.httpx.get")
    def test_get_dataset_resources_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "error": "Dataset not found"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            downloader.get_dataset_resources("bad-id")

    @patch("tddata.downloader.get_dataset_resources")
    @patch("tddata.downloader.httpx.stream")
    def test_download_success(self, mock_stream, mock_get_resources):
        # Mock resources
        mock_get_resources.return_value = [
            {
                "name": "Resource 1",
                "format": "CSV",
                "url": "http://example.com/file1.csv",
                "last_modified": "2024-01-01T12:00:00.000000",
                "size": 100
            },
            {
                "name": "Resource 2",
                "format": "PDF", # Should be skipped
                "url": "http://example.com/file2.pdf",
            }
        ]

        # Mock stream context manager
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Length": "10"}
        mock_response.iter_bytes.return_value = [b"chunk1", b"chunk2"]
        
        mock_stream.return_value.__enter__.return_value = mock_response

        # Execute download
        results = downloader.download(self.test_dir, "fake-dataset")

        # Verify
        expected_filename = "resource-1@2024-01-01T12:00:00.csv"
        expected_path = self.test_dir / expected_filename
        
        self.assertTrue(expected_path.exists())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["filename"], expected_filename)
        
        with open(expected_path, "rb") as f:
            content = f.read()
        self.assertEqual(content, b"chunk1chunk2")

    @patch("tddata.downloader.get_dataset_resources")
    def test_download_skip_existing(self, mock_get_resources):
        # Set up an existing file
        filename = "resource-1@2024-01-01T12:00:00.csv"
        filepath = self.test_dir / filename
        with open(filepath, "w") as f:
            f.write("existing content")
            
        mock_get_resources.return_value = [
            {
                "name": "Resource 1",
                "format": "CSV",
                "url": "http://example.com/file1.csv",
                "last_modified": "2024-01-01T12:00:00.000000",
                "size": 100
            }
        ]

        # Execute download (should skip)
        results = downloader.download(self.test_dir, "fake-dataset")

        # Verify no download call was made (implied by no mock_stream needed)
        self.assertEqual(len(results), 1)
        # Check that content is unchanged
        with open(filepath, "r") as f:
            self.assertEqual(f.read(), "existing content")

if __name__ == '__main__':
    unittest.main()

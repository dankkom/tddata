"""Tests for optional dependency handling.

This test verifies that tesouro-direto-fetcher can be imported and used correctly
both with and without the optional analysis extras.
"""

import unittest


class TestOptionalDependencies(unittest.TestCase):
    """Test that the package handles optional dependencies correctly."""

    def test_core_imports_always_available(self):
        """Core imports should always be available."""
        import tesouro_direto_fetcher

        # Core components should always be available
        self.assertIsNotNone(tesouro_direto_fetcher.downloader)
        self.assertIn("downloader", tesouro_direto_fetcher.__all__)

        # Constants should always be available
        self.assertIn("Column", tesouro_direto_fetcher.__all__)
        self.assertIn("BondType", tesouro_direto_fetcher.__all__)
        self.assertIn("OperationType", tesouro_direto_fetcher.__all__)

    def test_analysis_extras_detection(self):
        """Test that _HAS_ANALYSIS flag is set correctly."""
        import tesouro_direto_fetcher

        # _HAS_ANALYSIS should be a boolean
        self.assertIsInstance(tesouro_direto_fetcher._HAS_ANALYSIS, bool)

        # If analysis is available, plot and reader should be in __all__
        if tesouro_direto_fetcher._HAS_ANALYSIS:
            self.assertIn("plot", tesouro_direto_fetcher.__all__)
            self.assertIn("reader", tesouro_direto_fetcher.__all__)
            self.assertIsNotNone(tesouro_direto_fetcher.plot)
            self.assertIsNotNone(tesouro_direto_fetcher.reader)
        else:
            # Without analysis extras, these should not be in __all__
            self.assertNotIn("plot", tesouro_direto_fetcher.__all__)
            self.assertNotIn("reader", tesouro_direto_fetcher.__all__)

    def test_downloader_functions_available(self):
        """Test that downloader module has expected functions."""
        import tesouro_direto_fetcher

        # These functions should be available without extras
        self.assertTrue(hasattr(tesouro_direto_fetcher.downloader, "download"))
        self.assertTrue(
            hasattr(tesouro_direto_fetcher.downloader, "get_dataset_resources")
        )
        self.assertTrue(hasattr(tesouro_direto_fetcher.downloader, "get_download_info"))


if __name__ == "__main__":
    unittest.main()

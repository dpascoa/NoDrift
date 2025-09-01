import unittest
from crawler.logger import CrawlerLogger
import os

class TestCrawlerLogger(unittest.TestCase):
    def setUp(self):
        self.log_file = "test_log.log"
        self.logger = CrawlerLogger(self.log_file)

    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    # Test case 1:
    def test_log_message(self):
        """
        Checks that a message is logged and appears in the log file.
        """
        # Log a message and check file contents
        # Use an existing logger method to log a message
        self.logger.log_page_crawled("Test message", [], 200)
        with open(self.logger.log_filename, "r") as f:
            content = f.read()
        self.assertIn("Test message", content)

    # Test case 2:
    def test_log_file_error(self):
        """
        Checks that logger handles file errors gracefully when writing to log.
        """
        # Change file permissions and test error handling
        # Ensure log file exists before changing permissions
        with open(self.logger.log_filename, "w") as f:
            f.write("")
        os.chmod(self.logger.log_filename, 0o444)
        try:
            self.logger.log_page_crawled("Should fail gracefully", [], 200)
        except Exception:
            self.fail("Logger did not handle file error gracefully.")
        finally:
            os.chmod(self.logger.log_filename, 0o666)

if __name__ == "__main__":
    unittest.main()

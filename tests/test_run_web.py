import unittest
import run_web

class TestRunWeb(unittest.TestCase):
    # Test case 1:
    def test_app_exists(self):
        """
        Checks that the run_web module has an 'app' attribute.
        """
        # Check for 'app' attribute
        self.assertTrue(hasattr(run_web, "app"))

if __name__ == "__main__":
    unittest.main()

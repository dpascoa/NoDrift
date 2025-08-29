import unittest
import run_web

class TestRunWeb(unittest.TestCase):
    def test_app_exists(self):
        self.assertTrue(hasattr(run_web, "app"))

if __name__ == "__main__":
    unittest.main()

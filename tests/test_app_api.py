import unittest
from app import app

class TestAppAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    # Test case 1:
    def test_index(self):
        """
        Checks that the index route returns status 200 and contains 'NoDrift'.
        """
        # Send GET request to index
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NoDrift", response.data)

    # Test case 2:
    def test_start_crawl(self):
        """
        Checks that starting a crawl returns status 200 or 400.
        """
        # Send POST request to start_crawl
        response = self.client.post("/api/start_crawl", json={"url": "http://example.com"})
        self.assertIn(response.status_code, [200, 400])

    # Test case 3:
    def test_download_log(self):
        """
        Checks that downloading a log returns status 200 or 404.
        """
        # Send GET request to download_log
        response = self.client.get("/download_log")
        self.assertIn(response.status_code, [200, 404])

if __name__ == "__main__":
    unittest.main()

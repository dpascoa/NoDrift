import unittest
from app import app

class TestAppAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NoDrift", response.data)

    def test_start_crawl(self):
        response = self.client.post("/api/start_crawl", json={"url": "http://example.com"})
        self.assertIn(response.status_code, [200, 400])

    def test_download_log(self):
        response = self.client.get("/download_log")
        self.assertIn(response.status_code, [200, 404])

if __name__ == "__main__":
    unittest.main()

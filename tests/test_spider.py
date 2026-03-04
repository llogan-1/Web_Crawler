import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import sqlite3

# Add the parent directory to the sys.path to allow imports from the main project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from spider import Spider

class TestSpider(unittest.TestCase):

    def setUp(self):
        self.mock_engine = MagicMock()
        self.mock_engine.time_max = 10**12 # Far in the future
        self.spider = Spider(self.mock_engine)

    def test_crawl(self):
        # Mock engine filter
        self.mock_engine.filter.get_divs.return_value = ["<div>content</div>"]
        self.mock_engine.filter.extract_data.return_value = (["http://link.com"], [("key", 1)], [("event", 1)])
        self.mock_engine.anchor = "http://anchor.com"

        html = "<html><body><div>content</div></body></html>"
        result = self.spider.crawl(html, "http://anchor.com")

        self.assertEqual(result[0], ["http://link.com"])
        self.assertEqual(result[1], [("key", 1)])
        self.assertEqual(result[2], [("event", 1)])

    def test_request_work(self):
        self.mock_engine.schedule_a_spider.return_value = ("<html></html>", "http://url.com")
        result = Spider.request_work("thread_1")
        self.assertEqual(result, ("<html></html>", "http://url.com"))

if __name__ == "__main__":
    unittest.main()

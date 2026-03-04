import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import sqlite3
import time

# Add the parent directory to the sys.path to allow imports from the main project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine import Engine

class TestEngine(unittest.TestCase):

    @patch('engine.sqlite3')
    @patch('engine.Spider')
    @patch('engine.Thread')
    def setUp(self, mock_thread, mock_spider, mock_sqlite):
        self.mock_filter = MagicMock()
        self.website_info = ("http://example.com", "http://example.com")
        
        # Mock sqlite3.connect to return an in-memory db
        self.mock_conn = sqlite3.connect(":memory:")
        mock_sqlite.connect.return_value = self.mock_conn
        
        # Avoid booting real threads
        with patch.object(Engine, 'boot', return_value=None):
            self.engine = Engine(self.website_info, 1, self.mock_filter, 1)
            self.engine.scheduler_conn = self.mock_conn
            self.engine.crawler_conn = self.mock_conn

    def test_init_crawler_db(self):
        cursor = self.mock_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls'")
        self.assertIsNotNone(cursor.fetchone())
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='keywords'")
        self.assertIsNotNone(cursor.fetchone())

    def test_already_crawled(self):
        cursor = self.mock_conn.cursor()
        cursor.execute("INSERT INTO urls (url) VALUES (?)", ("http://crawled.com",))
        self.mock_conn.commit()
        
        self.assertTrue(Engine.already_crawled("http://crawled.com", self.mock_conn))
        self.assertFalse(Engine.already_crawled("http://notcrawled.com", self.mock_conn))

    def test_export_scraped(self):
        data = (["http://newlink.com"], [("word", 5)], [("event", 2)])
        url = "http://current.com"
        
        self.engine.export_scraped(data, url, self.mock_conn, self.mock_conn)
        
        cursor = self.mock_conn.cursor()
        cursor.execute("SELECT url FROM tasks WHERE url='http://newlink.com'")
        self.assertIsNotNone(cursor.fetchone())
        
        cursor.execute("SELECT id FROM urls WHERE url='http://current.com'")
        url_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT keyword, count FROM keywords WHERE url_id=?", (url_id,))
        self.assertEqual(cursor.fetchone(), ("word", 5))

if __name__ == "__main__":
    unittest.main()

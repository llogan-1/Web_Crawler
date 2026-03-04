import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import sqlite3
import time

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from crawler.core.engine import Engine

class TestEngine(unittest.TestCase):

    @patch('crawler.core.engine.sqlite3')
    @patch('crawler.core.engine.Spider')
    @patch('crawler.core.engine.Thread')
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
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cookies'")
        self.assertIsNotNone(cursor.fetchone())

    def test_already_crawled(self):
        cursor = self.mock_conn.cursor()
        cursor.execute("INSERT INTO urls (url) VALUES (?)", ("http://crawled.com",))
        self.mock_conn.commit()
        
        self.assertTrue(Engine.already_crawled("http://crawled.com", self.mock_conn))
        self.assertFalse(Engine.already_crawled("http://notcrawled.com", self.mock_conn))

    def test_export_scraped(self):
        # links, keywords, keyevents, metadata
        metadata = {"date": "2023-01-01", "author": "John Doe", "description": "Test desc"}
        data = (["http://newlink.com"], [("word", 5)], [("event", 2)], metadata)
        url = "http://current.com"
        source_url = "http://source.com"
        cookies = {"session": "123"}
        
        # Updated signature
        self.engine.export_scraped(data, url, source_url, cookies, self.mock_conn, self.mock_conn)
        
        cursor = self.mock_conn.cursor()
        cursor.execute("SELECT url, source_url FROM tasks WHERE url='http://newlink.com'")
        task = cursor.fetchone()
        self.assertIsNotNone(task)
        self.assertEqual(task[1], url) # current url should be source for new link
        
        cursor.execute("SELECT id, publication_date, author FROM urls WHERE url='http://current.com'")
        row = cursor.fetchone()
        url_id = row[0]
        self.assertEqual(row[1], "2023-01-01")
        self.assertEqual(row[2], "John Doe")
        
        cursor.execute("SELECT keyword, count FROM keywords WHERE url_id=?", (url_id,))
        self.assertEqual(cursor.fetchone(), ("word", 5))
        
        cursor.execute("SELECT name, value FROM cookies WHERE url_id=?", (url_id,))
        self.assertEqual(cursor.fetchone(), ("session", "123"))

if __name__ == "__main__":
    unittest.main()

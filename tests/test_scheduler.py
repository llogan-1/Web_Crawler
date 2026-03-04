import unittest
import sqlite3
import sys
import os

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from crawler.core.scheduler import Scheduler

class TestScheduler(unittest.TestCase):

    def setUp(self):
        """Set up a temporary, in-memory database for each test."""
        self.db_conn = sqlite3.connect(":memory:")
        self.scheduler = Scheduler(self.db_conn)

    def tearDown(self):
        """Close the database connection after each test."""
        self.db_conn.close()

    def test_register_and_assign_schedulable(self):
        """Test that a URL can be registered and then assigned."""
        test_url = "http://example.com"
        source_url = "http://source.com"
        
        # Register the URL with a source
        self.scheduler.register_schedulable(test_url, source_url)
        
        # Assign the item
        assigned_url, assigned_source = self.scheduler.assign_item_to_spider("spider_1")
        
        # Check if the assigned URL and source are correct
        self.assertEqual(assigned_url, test_url)
        self.assertEqual(assigned_source, source_url)

    def test_assign_to_multiple_spiders(self):
        urls = ["http://1.com", "http://2.com"]
        for url in urls:
            self.scheduler.register_schedulable(url)
        
        url1_data = self.scheduler.assign_item_to_spider("spider_1")
        url2_data = self.scheduler.assign_item_to_spider("spider_2")
        
        self.assertEqual(url1_data[0], "http://1.com")
        self.assertEqual(url2_data[0], "http://2.com")
        self.assertEqual(self.scheduler.size(), 0)

    def test_assign_empty_returns_none_tuple(self):
        url, source = self.scheduler.assign_item_to_spider("spider_1")
        self.assertIsNone(url)
        self.assertIsNone(source)

    def test_unregister_schedulable(self):
        url = "http://example.com"
        self.scheduler.register_schedulable(url)
        self.assertEqual(self.scheduler.size(), 1)
        self.scheduler.unregister_schedulable(url)
        self.assertEqual(self.scheduler.size(), 0)

    def test_is_empty(self):
        self.assertTrue(self.scheduler.is_empty())
        self.scheduler.register_schedulable("http://example.com")
        self.assertFalse(self.scheduler.is_empty())

    def test_size(self):
        self.assertEqual(self.scheduler.size(), 0)
        urls = ["http://a.com", "http://b.com", "http://c.com"]
        for url in urls:
            self.scheduler.register_schedulable(url)
        self.assertEqual(self.scheduler.size(), 3)

if __name__ == "__main__":
    unittest.main()

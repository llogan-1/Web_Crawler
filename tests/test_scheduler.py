import unittest
import sqlite3
import sys
import os

# Add the parent directory to the sys.path to allow imports from the main project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scheduler import Scheduler

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
        
        # Register the URL
        self.scheduler.register_schedulable(test_url)
        
        # Assign the item
        assigned_url = self.scheduler.assign_item_to_spider("spider_1")
        
        # Check if the assigned URL is the one we registered
        self.assertEqual(assigned_url, test_url)

    def test_assign_to_multiple_spiders(self):
        urls = ["http://1.com", "http://2.com"]
        for url in urls:
            self.scheduler.register_schedulable(url)
        
        url1 = self.scheduler.assign_item_to_spider("spider_1")
        url2 = self.scheduler.assign_item_to_spider("spider_2")
        
        self.assertEqual(url1, "http://1.com")
        self.assertEqual(url2, "http://2.com")
        self.assertEqual(self.scheduler.size(), 0)

    def test_assign_empty_raises_error(self):
        with self.assertRaises(ValueError):
            self.scheduler.assign_item_to_spider("spider_1")

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

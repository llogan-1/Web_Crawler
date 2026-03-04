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

    def test_is_empty(self):
        """Test that is_empty returns True for a new scheduler and False after adding a task."""
        # A new scheduler should be empty
        self.assertTrue(self.scheduler.is_empty())
        
        # After adding a task, it should not be empty
        self.scheduler.register_schedulable("http://example.com")
        self.assertFalse(self.scheduler.is_empty())

    def test_size(self):
        """Test that size correctly returns the number of tasks."""
        # Size of a new scheduler should be 0
        self.assertEqual(self.scheduler.size(), 0)
        
        # Add some tasks and check the size
        urls = ["http://example.com", "http://example.org", "http://example.net"]
        for url in urls:
            self.scheduler.register_schedulable(url)
        
        self.assertEqual(self.scheduler.size(), len(urls))

if __name__ == "__main__":
    unittest.main()

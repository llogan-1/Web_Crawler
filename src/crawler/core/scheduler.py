from threading import Lock

class Scheduler:
    """
    Manages the queue of URLs to be crawled.
    
    Handles task distribution to spiders and ensures thread-safe access 
    to the underlying task database.
    """
    def __init__(self, scheduler_conn):
        """
        Initialize the Scheduler with a database connection.

        Args:
            scheduler_conn: SQLite connection to the tasks database.
        """
        self.lock = Lock()
        self.db_conn = scheduler_conn # Database connection
        self.spider_assignments = {}
        
        # Init necessary tables
        self._init_db()

    # Fetch the next schedulable item (URL and its source) from the database
    def assign_item_to_spider(self, spider_id: str):
        """
        Fetch and assign the next URL from the task queue to a spider.

        Args:
            spider_id (str): Identifier for the spider requesting a task.

        Returns:
            tuple: (url, source_url) of the assigned task, or (None, None) if queue is empty.
        """
        with self.lock, self.db_conn:
            cursor = self.db_conn.cursor()
            # Fetch both url and source_url
            cursor.execute('SELECT id, url, source_url FROM tasks ORDER BY id LIMIT 1')
            task = cursor.fetchone()

            if task:
                task_id, url, source_url = task
                self.spider_assignments[spider_id] = url
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                return (str(url), str(source_url) if source_url else None)
            else:
                return (None, None)

    def is_empty(self):
        """
        Check if the task queue is empty.

        Returns:
            bool: True if there are no more tasks in the database, False otherwise.
        """
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM tasks')
            val = cursor.fetchone()[0] == 0
            cursor.close()
            return val
        
    def size(self):
        """
        Get the current number of tasks in the queue.

        Returns:
            int: The count of pending tasks.
        """
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM tasks')
            size = cursor.fetchone()[0]
            cursor.close()
            return size

    def register_schedulable(self, url: str, source_url: str = None):
        """
        Register a new task (URL and its source) to the scheduler.

        Args:
            url (str): The URL to be crawled.
            source_url (str, optional): The URL that discovered this link.
        """
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('INSERT INTO tasks (url, source_url) VALUES (?, ?)', (url, source_url))
            self.db_conn.commit()
            cursor.close()

    def unregister_schedulable(self, url: str):
        """
        Unregister a task from the scheduler.

        Args:
            url (str): The URL to remove from the task queue.
        """
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE url = ?', (url,))
            self.db_conn.commit()
            cursor.close()
    
    def _init_db(self):
        """
        Initialize the database table for tasks.
        """
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    url TEXT NOT NULL,
                    source_url TEXT
                )
            ''')
            self.db_conn.commit()
            cursor.close()

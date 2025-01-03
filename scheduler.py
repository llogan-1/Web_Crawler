from threading import Lock

class Scheduler:
    def __init__(self, scheduler_conn):
        self.lock = Lock()
        self.db_conn = scheduler_conn # Database connection
        self.spider_assignments = {}
        
        # Init necessary tables
        self._init_db()

    # Fetch the next schedulable item (URL) from the database
    def assign_item_to_spider(self, spider_id: str):
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT id, url FROM tasks ORDER BY id LIMIT 1')
            task = cursor.fetchone()

            if task:
                task_id, url = task
                self.spider_assignments[spider_id] = url
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                self.db_conn.commit()
                return url
            else:
                raise ValueError("No tasks available to assign to the spider.")

    def is_empty(self):
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM tasks')
            val = cursor.fetchone()[0] == 0
            cursor.close()
            return val
        
    def size(self):
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM tasks')
            size = cursor.fetchone()[0]
            cursor.close()
            return size

    def register_schedulable(self, url: str):
        """Register a new task (URL) to the scheduler."""
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('INSERT INTO tasks (url) VALUES (?)', (url,))
            self.db_conn.commit()
            cursor.close()

    def unregister_schedulable(self, url: str):
        """Unregister a task from the scheduler."""
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE url = ?', (url,))
            self.db_conn.commit()
            cursor.close()
    
    def _init_db(self):
        with self.lock:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    url TEXT NOT NULL
                )
            ''')
            self.db_conn.commit()
            cursor.close()
from scheduler import Scheduler
from html_fetch import HTMLFetcher
from spider import Spider
from threading import Thread
from threading import Lock
import sqlite3
import time

class Engine:

    def __init__(self, website_info, mins, filter, thread_number):
        self._instance = self
        self.anchor = website_info[1]
        self.lock = Lock()
        self.filter = filter
        self.threads = []
        self.thread_number = thread_number

        # Timer
        self.time_max = time.time() + (mins * 60) # add mins minutes
        
        # Database connection
        self.scheduler_conn = sqlite3.connect("DataBases/scheduler.db", check_same_thread=False)
        self.crawler_conn = sqlite3.connect("DataBases/crawled.db", check_same_thread=False)

        # Define scheduler
        self.scheduler = Scheduler(self.scheduler_conn)
        self.scheduler.register_schedulable(website_info[0]) # First item in the scheduler is set

        # Define HTML fetcher
        self.htmlfetcher = HTMLFetcher()

        # Boot
        self._init_crawler_db()
        self.boot()

    def boot(self): # self is engine
        
        # Starting spider)s_
        main_spider = Spider(self)
        for i in range(self.thread_number):
            thread = Thread(target=main_spider.run, args=("thread_" + str(i), self.anchor,))
            self.threads.append(thread)
            thread.daemon = True # Spider can be daemon since run_spiders keeps program running indefinetly 
            thread.start()
        # Once threads can no longer .run, they will all be killed
        for thread in self.threads:
            thread.join() 

        
    def schedule_a_spider(self, thread_num : str):
        url = self.scheduler.assign_item_to_spider(thread_num)
        return (HTMLFetcher.fetch_html(url), url)
    
    def export_scraped(self, data, url, scheduler_conn, crawler_conn):
        print("Exporting scraped data...")
        # Unpackage data
        links = data[0]
        keywords = data[1]
        keyevents = data[2]

        # Insert content links into the scheduler database
        try:
            with scheduler_conn:
                cursor = scheduler_conn.cursor()
                for link in links:
                    cursor.execute('INSERT INTO tasks (url) VALUES (?)', (link,))
            print(f"{len(links)} content links added to scheduler DB.")
        except Exception as e:
            print(f"Error inserting content links into scheduler DB: {e}")
            
        # Insert keywords and events into the crawled database
        try:
            with crawler_conn:
                cursor = crawler_conn.cursor()

                # Insert or retrieve URL ID
                cursor.execute('INSERT OR IGNORE INTO urls (url) VALUES (?)', (url,))
                cursor.execute('SELECT id FROM urls WHERE url = ?', (url,))
                url_id = cursor.fetchone()[0]

                # Clear previous keywords and events for this URL
                cursor.execute('DELETE FROM keywords WHERE url_id = ?', (url_id,))
                cursor.execute('DELETE FROM keyevents WHERE url_id = ?', (url_id,))

                # Insert keywords
                for keyword, count in keywords:
                    cursor.execute('INSERT INTO keywords (url_id, keyword, count) VALUES (?, ?, ?)', (url_id, keyword, count))

                # Insert keyevents
                for event, count in keyevents:
                    cursor.execute('INSERT INTO keyevents (url_id, event, count) VALUES (?, ?, ?)', (url_id, event, count))

            print("Url, keywords, and keyevents added to crawled DB.")
        except Exception as e:
            print(f"Error inserting data into crawled DB: {e}")

    @staticmethod
    def already_crawled(url : str, crawler_conn):
        try:
            cursor = crawler_conn.cursor()

            # SQL query to check if the URL is in the 'urls' table
            cursor.execute("SELECT 1 FROM urls WHERE url = ?", (url,))
            result = cursor.fetchone()

            # If result is not None, URL is in the table
            if result:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            print(url)
            print(type(url))
            return False

    def _init_crawler_db(self):
        cursor = self.crawler_conn.cursor()

        # URLs table to store unique URLs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE
            )
        ''')

        # Keywords table to store keyword counts linked to URLs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER,
                keyword TEXT,
                count INTEGER,
                FOREIGN KEY (url_id) REFERENCES urls(id) ON DELETE CASCADE
            )
        ''')

        # Keyevents table to store event counts linked to URLs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyevents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER,
                event TEXT,
                count INTEGER,
                FOREIGN KEY (url_id) REFERENCES urls(id) ON DELETE CASCADE
            )
        ''')
        self.crawler_conn.commit()
        cursor.close()
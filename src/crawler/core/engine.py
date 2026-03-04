from .scheduler import Scheduler
from ..utils.html_fetch import HTMLFetcher
from .spider import Spider
from threading import Thread
from threading import Lock
import sqlite3
import time
import os
import json

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
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Database connection
        self.scheduler_conn = sqlite3.connect("data/scheduler.db", check_same_thread=False)
        self.crawler_conn = sqlite3.connect("data/crawled.db", check_same_thread=False)

        # Define scheduler
        self.scheduler = Scheduler(self.scheduler_conn)
        self.scheduler.register_schedulable(website_info[0], None) # First item, no source

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
        url_data = self.scheduler.assign_item_to_spider(thread_num)
        url, source_url = url_data
        if url:
            html_cookies = HTMLFetcher.fetch_html(url)
            html, cookies = html_cookies
            return (html, url, source_url, cookies)
        return (None, None, None, None)
    
    def export_scraped(self, data, url, source_url, cookies, scheduler_conn, crawler_conn):
        print(f"Exporting scraped data for {url}...")
        # Unpackage data: (links, keywords, keyevents, metadata)
        links = data[0]
        keywords = data[1]
        keyevents = data[2]
        metadata = data[3]

        # Insert content links into the scheduler database, passing current url as source_url
        try:
            with scheduler_conn:
                cursor = scheduler_conn.cursor()
                for link in links:
                    cursor.execute('INSERT INTO tasks (url, source_url) VALUES (?, ?)', (link, url))
            print(f"{len(links)} content links added to scheduler DB.")
        except Exception as e:
            print(f"Error inserting content links into scheduler DB: {e}")
            
        # Insert metadata and cookies into the crawled database
        try:
            with crawler_conn:
                cursor = crawler_conn.cursor()

                # Insert or retrieve URL ID with new columns
                cursor.execute('''
                    INSERT OR IGNORE INTO urls (url, source_url, publication_date, author, description) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (url, source_url, metadata.get("date"), metadata.get("author"), metadata.get("description")))
                
                # If already exists, update the metadata if it was NULL
                cursor.execute('''
                    UPDATE urls SET 
                        source_url = COALESCE(source_url, ?),
                        publication_date = COALESCE(publication_date, ?),
                        author = COALESCE(author, ?),
                        description = COALESCE(description, ?)
                    WHERE url = ?
                ''', (source_url, metadata.get("date"), metadata.get("author"), metadata.get("description"), url))

                cursor.execute('SELECT id FROM urls WHERE url = ?', (url,))
                url_id = cursor.fetchone()[0]

                # Clear previous keywords, events, and cookies for this URL
                cursor.execute('DELETE FROM keywords WHERE url_id = ?', (url_id,))
                cursor.execute('DELETE FROM keyevents WHERE url_id = ?', (url_id,))
                cursor.execute('DELETE FROM cookies WHERE url_id = ?', (url_id,))

                # Insert keywords
                for keyword, count in keywords:
                    cursor.execute('INSERT INTO keywords (url_id, keyword, count) VALUES (?, ?, ?)', (url_id, keyword, count))

                # Insert keyevents
                for event, count in keyevents:
                    cursor.execute('INSERT INTO keyevents (url_id, event, count) VALUES (?, ?, ?)', (url_id, event, count))
                
                # Insert cookies
                if cookies:
                    for name, value in cookies.items():
                        cursor.execute('INSERT INTO cookies (url_id, name, value) VALUES (?, ?, ?)', (url_id, name, value))

            print("URL details, keywords, keyevents, and cookies added to crawled DB.")
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
            return False

    def _init_crawler_db(self):
        cursor = self.crawler_conn.cursor()

        # URLs table updated with new columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                source_url TEXT,
                publication_date TEXT,
                author TEXT,
                description TEXT
            )
        ''')

        # Keywords table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER,
                keyword TEXT,
                count INTEGER,
                FOREIGN KEY (url_id) REFERENCES urls(id) ON DELETE CASCADE
            )
        ''')

        # Keyevents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyevents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER,
                event TEXT,
                count INTEGER,
                FOREIGN KEY (url_id) REFERENCES urls(id) ON DELETE CASCADE
            )
        ''')

        # Cookies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cookies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER,
                name TEXT,
                value TEXT,
                FOREIGN KEY (url_id) REFERENCES urls(id) ON DELETE CASCADE
            )
        ''')
        
        self.crawler_conn.commit()
        cursor.close()

from .scheduler import Scheduler
from ..utils.html_fetch import HTMLFetcher
from ..utils.robots_checker import RobotsChecker
from .spider import Spider
from threading import Thread
from threading import Lock
import sqlite3
import time
import os
import json
from datetime import datetime

class Engine:

    DEFAULT_USER_AGENT = 'MyPersonalPortfolioBot/1.0 (https://github.com/llogan-1/Web_Crawler; contact@example.com) Mozilla/5.0 (compatible; MyBot/1.0)'

    def __init__(self, website_info, mins, filter, thread_number, user_agent=None):
        self._instance = self
        self.anchor = website_info[1]
        self.lock = Lock()
        self.filter = filter
        self.threads = []
        self.thread_number = thread_number
        self.user_agent = user_agent if user_agent else self.DEFAULT_USER_AGENT

        # Robots.txt checker 
        self.robots_checker = RobotsChecker(user_agent=self.user_agent)

        # Timer
        self.time_max = time.time() + (mins * 60) # add mins minutes
        
        # Create unique folder for this crawl session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.data_dir = os.path.join("data", f"crawl_{timestamp}")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Database connection paths
        self.scheduler_db_path = os.path.join(self.data_dir, "scheduler.db")
        self.crawled_db_path = os.path.join(self.data_dir, "crawled.db")

        # Database connection
        self.scheduler_conn = sqlite3.connect(self.scheduler_db_path, check_same_thread=False)
        self.crawler_conn = sqlite3.connect(self.crawled_db_path, check_same_thread=False)

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
            # Spider now uses self.data_dir for its database connections
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
            # Check robots.txt before fetching
            if not self.robots_checker.is_allowed(url):
                print(f"URL disallowed by robots.txt: {url}")
                return (None, url, source_url, None) # Still return URL so it can be handled or skipped
            
            # Check and apply crawl-delay
            delay = self.robots_checker.get_crawl_delay(url)
            if delay:
                # Basic implementation: simple sleep
                time.sleep(delay)

            # Pass the user agent to fetch_html
            html_cookies = HTMLFetcher.fetch_html(url, user_agent=self.user_agent)
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

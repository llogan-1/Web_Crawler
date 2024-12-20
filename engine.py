from scheduler import Scheduler
from html_fetch import HTMLFetcher
from spider import Spider
from threading import Thread
from threading import Lock
import sqlite3

class Engine:

    def __init__(self, website_info):
        self._instance = self
        self.run = False
        self.lock = Lock()
        
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
        self.run = True
        
        # Starting spider
        main_spider = Spider(self)
        for i in range(7):
            thread = Thread(target=main_spider.run, args=("thread_" + str(i),))
            thread.daemon = True # Spider can be daemon since managespiders keeps program running indefinetly 
            thread.start()
        self.manage_spiders()

    def manage_spiders(self):
        print("Making all spiders")
        
        # Stops program when scheduler has nothing left to give
        while True: # need a better condition to stop program!
            if self.scheduler.is_empty():
                pass
            pass
        
    def schedule_a_spider(self, thread_num : str):
        url = self.scheduler.assign_item_to_spider(thread_num)
        return (HTMLFetcher.fetch_html(url), url)
    
    def export_scraped(self, data, url, scheduler_conn, crawler_conn):
        print("Exporting scraped data...")
        # Extract data
        title = data[0]
        content_links = data[2]
        catlinks = data[1]
        events = data[3][1]
        keywords = data[3][0]

        # Ensure keywords, events, and catlinks are flat lists of strings
        keywords = [str(item) for item in keywords]  # Convert all items to strings
        events = [str(item) for item in events]      # Convert all items to strings
        catlinks = [str(item) for item in catlinks]  # Convert all items to strings

        # Insert content links into the scheduler database
        try:
            with scheduler_conn:
                cursor = scheduler_conn.cursor()
                for link in content_links:
                    cursor.execute('INSERT INTO tasks (url) VALUES (?)', (link,))
            print(f"{len(content_links)} content links added to scheduler DB.")
        except Exception as e:
            print(f"Error inserting content links into scheduler DB: {e}")
            
        # Insert keywords, events, and catlinks into the crawled database
        try:
            with crawler_conn:
                cursor = crawler_conn.cursor()
                # Create or update the entry for the website address
                cursor.execute('''
                    INSERT INTO crawled (url, keywords, events, catlinks)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        keywords=excluded.keywords,
                        events=excluded.events,
                        catlinks=excluded.catlinks
                ''', (url, ','.join(keywords), ','.join(events), ','.join(catlinks)))
            print("Keywords, events, and catlinks added to crawled DB.")
        except Exception as e:
            print(f"Error inserting data into crawled DB: {e}")

    def _init_crawler_db(self):
        cursor = self.crawler_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawled (
                url TEXT PRIMARY KEY,
                keywords TEXT,
                events TEXT,
                catlinks TEXT
            )
        ''')
        self.crawler_conn.commit()
        cursor.close()
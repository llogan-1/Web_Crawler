from threading import Lock
import sqlite3
import time
import os

class Spider:
    """
    Worker class responsible for crawling individual web pages.
    
    Spiders request tasks from the Engine, fetch HTML content, 
    extract data using filters, and report results back to the Engine.
    """

    en = None

    def __init__(self, engine):
        """
        Initialize the Spider with a reference to the Engine.

        Args:
            engine (Engine): The central orchestration engine.
        """
        
        self.url = ''
        self.lock = Lock()
        Spider.en = engine

    def run(self, spider_num, anchor):
        """
        The main loop for the spider thread.
        
        Continuously requests work from the engine until the crawl time expires.

        Args:
            spider_num (str): Identifier for this spider thread.
            anchor (str): The base URL anchor for link filtering.
        """

        # Create new connections for each thread using the paths from the engine
        scheduler_conn = sqlite3.connect(Spider.en.scheduler_db_path)
        crawler_conn = sqlite3.connect(Spider.en.crawled_db_path)

        while True:
            if time.time() >= Spider.en.time_max:
                break

            WebData = Spider.request_work(spider_num) # request string of HTML text
            HTML = WebData[0]
            url = WebData[1]
            source_url = WebData[2]
            cookies = WebData[3]

            if not url:
                # No tasks available, wait a bit
                time.sleep(1)
                continue

            # If HTML is None but url exists, it might be disallowed by robots.txt or failed fetch
            if not HTML:
                # We should still mark it as "already crawled" (or "already checked") to avoid re-crawling
                # Insert empty metadata so it's recorded as skipped
                with self.lock:
                    Spider.en.export_scraped(([], [], [], {"date": "disallowed/failed", "author": None, "description": None}), 
                                            url, source_url, cookies, scheduler_conn, crawler_conn)
                continue

            if Spider.en.already_crawled(url, crawler_conn):
                continue
            
            print(f"{spider_num} processing: {url} (from {source_url})")
            data = Spider.crawl(self, HTML, anchor)
            with self.lock:
                Spider.en.export_scraped(data, url, source_url, cookies, scheduler_conn, crawler_conn)

        scheduler_conn.close()
        crawler_conn.close()

    def crawl(self, html_input : str, anchor : str):
        """
        Extract data from the provided HTML content.

        Args:
            html_input (str): The raw HTML content of the page.
            anchor (str): The base URL anchor for filtering.

        Returns:
            tuple: (links, keywords, keyevents, metadata) extracted from the page.
        """

        # Collect divs to analyze
        content_divs = Spider.en.filter.get_divs(html_input)
        if not content_divs:
            # Still extract metadata and links even if no content divs found
            import bs4
            soup = bs4.BeautifulSoup(html_input, 'html.parser')
            content_divs = [soup] 

        # Returns a tuple: (Links, KeyWords, KeyEvents, Metadata)
        # Passing html_input as raw_html for metadata extraction
        links_keywords_keyevents_meta = Spider.en.filter.extract_data(content_divs, Spider.en.anchor, raw_html=html_input)

        return links_keywords_keyevents_meta


    @staticmethod
    def request_work(spider_num : str):
        """
        Request a new crawling task from the Engine.

        Args:
            spider_num (str): Identifier for the requesting spider.

        Returns:
            tuple: (html, url, source_url, cookies) for the next task.
        """
        # Now returns (html, url, source_url, cookies)
        data = Spider.en.schedule_a_spider(spider_num)
        return data

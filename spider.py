from threading import Lock
import sqlite3
import time

class Spider:

    en = None

    def __init__(self, engine):
        
        self.url = ''
        self.lock = Lock()
        Spider.en = engine

    def run(self, spider_num, anchor):

        # Create new connections for each thread
        scheduler_conn = sqlite3.connect("DataBases/scheduler.db")  # New connection for each thread
        crawler_conn = sqlite3.connect("DataBases/crawled.db")  # New connection for each thread

        while True:
            if time.time() >= Spider.en.time_max:
                break

            print(spider_num+'\n')
            WebData = Spider.request_work(spider_num) # request string of HTML text
            HTML = WebData[0]
            url = WebData[1]

            if not HTML or Spider.en.already_crawled(url, crawler_conn):
                continue
            
            data = Spider.crawl(self, HTML, anchor)
            with self.lock:
                Spider.en.export_scraped(data, url, scheduler_conn, crawler_conn)

        scheduler_conn.close()
        crawler_conn.close()

    # Rework crawling and link gathering for generality.
    # Move soup to filter, use tuples for all possible types of content to find

    def crawl(self, html_input : str, anchor : str):

        # Collect divs to analyze
        content_divs = Spider.en.filter.get_divs(html_input)
        if not content_divs:
            print(f"No content divisions found for anchor {anchor}")
            return ([],[],[]
                    )
        # Returns a tuple of lists:  (Links, KeyWords, KeyEvents)
        links_keywords_keyevents = Spider.en.filter.extract_data(content_divs, Spider.en.anchor)

        return links_keywords_keyevents


    @staticmethod
    def request_work(spider_num : str):
        HTML = Spider.en.schedule_a_spider(spider_num)
        return HTML
    
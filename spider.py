from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from threading import Lock
import sqlite3
import time

#nltk.download('stopwords')

class Spider:

    en = None
    r = None

    def __init__(self, engine):
        print("Creating Spider")
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
            data = Spider.crawl(HTML, anchor)
            with self.lock:
                Spider.en.export_scraped(data, url, scheduler_conn, crawler_conn)

        scheduler_conn.close()
        crawler_conn.close()

    def crawl(html_input : str, anchor : str):
        soup = BeautifulSoup(html_input, 'html.parser')
        
        # Title of the webpage
        title = (soup.title.string).replace(" - Wikipedia", "") if soup.title else "No title found"
        
        # Clean data to analyze
        catlinks_div = soup.find('div', id='mw-normal-catlinks')
        content_div = soup.find('div', id='mw-content-text')
        # Keywords
        content_text = ""
        if content_div:
            paragraphs = content_div.find_all('p')  # Find all <p> tags
            content_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        
        # Get data
        catlinks = Spider.en.filter.get_catlinks(catlinks_div, anchor)
        content_links = Spider.en.filter.get_content_links(content_div, anchor)

        # Get keywords
        keywords_events = Spider.en.filter.get_keywords_and_events(content_text)

        # Return the scraped data
        data = (title, catlinks, content_links, keywords_events)
        return data


    @staticmethod
    def request_work(spider_num : str):
        HTML = Spider.en.schedule_a_spider(spider_num)
        return HTML
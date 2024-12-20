from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string
import get_content 

class Spider:

    en = None
    r = None

    def __init__(self, engine):
        print("Creating Spider")
        self.url = ''
        Spider.en = engine

    def run(self, spider_num):
        print("in run spider\n")
        print(spider_num)
        while True:
            WebData = Spider.request_work(spider_num) # request string of HTML text
            HTML = WebData[0]
            url = WebData[1]
            keys_and_links = Spider.crawl(HTML)
            Spider.en.export_scraped(keys_and_links, url)

    def crawl(html_input : str):
        print("crawling page")
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
        catlinks = get_content.get_catlinks(catlinks_div)
        content_links = get_content.get_content_links(content_div)

        # Get keywords
        keywords_events = get_content.get_keywords_and_events(content_text)

        # Return the scraped data
        data = (title, catlinks, content_links, keywords_events)
        return data


    @staticmethod
    def request_work(spider_num : str):
        HTML = Spider.en.schedule_a_spider(spider_num)
        return HTML
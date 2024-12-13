from urllib.request import urlopen
from link_finder import LinkFinder
from general_functions import *
from queue import Queue
import threading

class Spider:
    
    # Class vairables to be shared among all instance of Spider
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = None
    crawled = set()
    queue_lock = threading.Lock()  # Synchronize queue access
    crawled_lock = threading.Lock()  # Synchronize crawled access

    def __init__(self, project_name, base_url, domain_name, queue):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name 
        Spider.queue_file = Path(Spider.project_name + '/queue.txt')
        Spider.crawled_file = Path(Spider.project_name + '/crawled.txt')
        Spider.queue = queue
        self.boot()
        self.crawl_page('First Spider', Spider.base_url)
        self.add_links_to_queue(Spider.base_url)

    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.crawled = file_to_set(Spider.crawled_file)
        for link in file_to_set(Spider.queue_file):
            Spider.queue.put(link)

    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(f"{thread_name} now crawling: {page_url}")
            print(f"Queue size: {Spider.queue.qsize()} | Crawled: {len(Spider.crawled)}")
            links = Spider.gather_links(page_url)
            Spider.add_links_to_queue(links)
            with Spider.crawled_lock:  # Corrected: no parentheses here
                Spider.crawled.add(page_url)
            Spider.update_files()

    #connects to site, scrapes HTML code, converts to string, passes to link finder, gets set of all links and urls. as long as no issues, get all urls

    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)

            # Normalize Content-Type header to handle parameters like charset
            content_type = response.getheader('Content-Type', '').split(';')[0].strip()
            
            if content_type == 'text/html':  # Check if the response is HTML
                html_bytes = response.read()
                html_string = html_bytes.decode('utf-8', errors='ignore') #decode bytes to a string
            
            finder = LinkFinder(Spider.base_url, page_url, Spider.domain_name)
            finder.feed(html_string)  # Pass HTML content to LinkFinder
        
        except Exception as e:
            print(f"Cannot crawl page: {e}")
            return set()
        
        # Return the set of extracted links
        return finder.page_links()
    
    @staticmethod
    def add_links_to_queue(links):
        new_links = []
        with Spider.queue_lock:  # Ensure thread-safe modification
            for url in links:
                # Accessing underlying list to check membership
                if url not in Spider.queue.queue and url not in Spider.crawled:
                    if Spider.domain_name in url:
                        Spider.queue.put(url)  # Add to the queue
        Spider.update_files()  # Write to file after modifying the queue

    @staticmethod
    def update_files():
        with Spider.queue_lock, Spider.crawled_lock:
            set_to_file(set(Spider.queue.queue), Spider.queue_file)
            set_to_file(Spider.crawled, Spider.crawled_file)
from urllib.request import urlopen
from link_finder import LinkFinder
from general_functions import *


class Spider:
    
    # Class vairables to be shared among all instance of Spider
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name 
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page('First Spider', Spider.base_url)

    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling page ' + page_url)
            print('Queue: ' + str(len(Spider.queue)) + ' | Crawled: '+ str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_file()

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
                html_string = html_bytes.decode("utf-8")  # Decode bytes to a string
            
            finder = LinkFinder(Spider.base_url, page_url, Spider.domain_name)
            finder.feed(html_string)  # Pass HTML content to LinkFinder
        
        except Exception as e:
            print(f"Cannot crawl page: {e}")
            return set()
        
        # Return the set of extracted links
        return finder.page_links()
    
    
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if url in Spider.queue:
                continue
            if url in Spider.crawled:
                continue
            if Spider.domain_name not in url: #this is limiting to our primary domain name 
                continue
            Spider.queue.add(url)
        
    @staticmethod
    def update_file():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
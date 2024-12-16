from scheduler import Scheduler
from html_fetch import HTMLFetcher
from spider import Spider

class Engine:

    def __init__(self, website_info):
        # Define scheduler
        self.scheduler = Scheduler()
        self.scheduler.register_schedulable(website_info[0]) # First item in the scheduler is set
        # Define HTML fetcher
        self.htmlfetcher = HTMLFetcher()

        # Create first spider to scrape main.
        self.boot()

    @staticmethod
    def boot():
        print("booting engine")
        Spider()
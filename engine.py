from scheduler import Scheduler
from html_fetch import HTMLFetcher
from spider import Spider
from threading import Thread

class Engine:

    run = None

    def __init__(self, website_info):
        Engine._instance = self

        # Spider list
        self.spiders = []
        self.run = False
        # Define scheduler
        self.scheduler = Scheduler()
        self.scheduler.register_schedulable(website_info[0]) # First item in the scheduler is set
        # Define HTML fetcher
        self.htmlfetcher = HTMLFetcher()

        # Create first spider to scrape main.
        self.boot()

    def boot(self): # self is engine
        print("booting engine")
        self.run = True
        
        # Starting spider
        main_spider = Spider(self)
        thread_1 = Thread(target = main_spider.run)
        # SET THIS SPIDER TO BE DAEMON WHEN WE CONFIRM THE ENGINE RUNS INDEFINETLY
        self.spiders.append(thread_1)
        thread_1.start()
        
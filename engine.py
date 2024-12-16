from scheduler import Scheduler
from html_fetch import HTMLFetcher
from spider import Spider
from threading import Thread

class Engine:

    run = None
    scheduler = None
    htmlfetcher = None
    spiders = []

    def __init__(self, website_info):
        self._instance = self

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
        thread_1 = Thread(target=main_spider.run, args=("thread_1",))
        thread_1.daemon = True # Spider can be daemon since managespiders keeps program running indefinetly 
        self.spiders.append(thread_1)
        thread_1.start()
        self.manage_spiders(main_spider)

    def manage_spiders(self, main_Spider):
        print("Making all spiders")
        
        # Stops program when scheduler has nothing left to give
        while True:
            if self.scheduler.is_empty():
                break
            pass
        
    def schedule_a_spider(self, thread_num : str):
        self.scheduler.enqueue_request(thread_num)
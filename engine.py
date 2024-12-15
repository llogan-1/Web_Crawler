from scheduler import Scheduler

class Engine:

    def __init__(self, website_info):
        self.scheduler = Scheduler()
        

        # Start scraping
        self.boot()

    @staticmethod
    def boot():
        print("booting engine")
        #set db link
        #init the first spider
        
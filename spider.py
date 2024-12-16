import engine
class Spider:

    en = engine

    def __init__(self, engine):
        print("Creating Spider")
        self.url = ''
        self.en = engine


    def run(self, spider_num):
        print("in run spider\n")
        print(spider_num)
        i = 1
        while True:
            HTML = Spider.request_work(spider_num) # request string of HTML text
            Spider.crawl()
    
    @staticmethod
    def crawl():
        print("crawl over the html text")

    @staticmethod
    def request_work(spider_num : str):
        # Ask engine to be given HTML
        # Engine will give request to scheduler
        print("ask engine for html to parse")

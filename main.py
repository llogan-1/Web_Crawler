import threading
from queue import Queue
from spider import Spider
from domain import *
from general_functions import *


PROJECT_NAME = 'testproject'
HOMEPAGE = 'https://en.wikipedia.org/wiki/Main_Page'
DOMAIN_NAME = get_domain_name(HOMEPAGE)
QUEUE_FILE = PROJECT_NAME + '/queue.txt'
CRAWLED_FILE = PROJECT_NAME + 'crawled.txt'
NUMBER_OF_THREADS = 8
queue = Queue()
#initialize crawling
Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)


# Create workers threads (will die when main exits)
def create_workers():
    for _ in range(NUMBER_OF_THREADS): # don't need to use a variable so we just use _
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

# Do the next job in the queue
def work():
    while True:
        url = queue.get()
        try:
            Spider.crawl_page(threading.current_thread().name, url)
        except Exception as e:
            print(f"Error crawling {url}: {e}")
        finally:
            queue.task_done()

# Each queued link is a new job
def create_jobs():
    for link in file_to_set(Path(QUEUE_FILE)):
        queue.put(link)
    queue.join()
    crawl()



# Checks if items in Queue, if so, crawl them
def crawl():
    queued_links = file_to_set(Path(QUEUE_FILE))
    if (len(queued_links) > 0):
        print(str(len(queued_links)) + ' links in the queue')
        create_jobs()


# Runnable
if __name__ == "__main__":
    create_workers()
    crawl()
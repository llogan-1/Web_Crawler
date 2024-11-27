import threading
from queue import Queue, Full
from spider import Spider
from domain import *
from general_functions import *
import time


PROJECT_NAME = 'testproject'
HOMEPAGE = 'https://en.wikipedia.org/wiki/Main_Page'
DOMAIN_NAME = get_domain_name(HOMEPAGE)
QUEUE_FILE = PROJECT_NAME + '/queue.txt'
CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
MAX_QUEUE_SIZE = 100
NUMBER_OF_THREADS = 1
queue = Queue(maxsize=MAX_QUEUE_SIZE)
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
            print(f"Error crawling {url}: {e} \n")
        finally:
            queue.task_done()

# adds link to queue, limits the total queue
def add_to_queue(url):
    try:
        queue.put(url, block=True, timeout=1)  # Wait for 1 second before timing out if the queue is full
        print(f"Added {url} to the queue")
    except Full:
        print(f"Queue is full, waiting to add: {url}\n")

# Each queued link is a new job
def create_jobs():
    queued_links = file_to_set(Path(QUEUE_FILE))
    
    for link in queued_links:
        add_to_queue(link) 

    queue.join()
    crawl()



# Checks if items in Queue, if so, crawl them
def crawl():
    queued_links = file_to_set(Path(QUEUE_FILE))
    if (len(queued_links) > 0):
        print(str(len(queued_links)) + ' links in the queue' + '\n')
        create_jobs()

# Runnable
if __name__ == "__main__":
    create_workers()
    crawl()
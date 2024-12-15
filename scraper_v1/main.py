import threading
from queue import Queue, Full
from spider import Spider
from domain import get_domain_name
from general_functions import *
from pathlib import Path

PROJECT_NAME = 'testproject'
HOMEPAGE = 'https://en.wikipedia.org/wiki/Main_Page'
DOMAIN_NAME = get_domain_name(HOMEPAGE)
QUEUE_FILE = PROJECT_NAME + '/queue.txt'
CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
NUMBER_OF_THREADS = 6
queue = Queue()

def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


def work():
    while True:
        try:
            url = queue.get(block=True, timeout=5)  # Wait for URL
            Spider.crawl_page(threading.current_thread().name, url)
        except Exception as e:
            print(f"Error in thread: {e}")
        finally:
            queue.task_done()


def crawl():
    while True:
        if queue.empty():
            print("No more links in queue. Exiting crawl.\\")
            break
        print(f"Queue size: {queue.qsize()} | Crawled: {len(Spider.crawled)}")
        queue.join()


if __name__ == "__main__":
    Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME, queue)
    create_workers()
    crawl()
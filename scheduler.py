import heapq
from threading import Lock
import hashlib

def generate_key(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

class Scheduler:
    def __init__(self):
        self.priority_queue = []  # Internal priority queue using heapq
        self.lock = Lock()
        self.schedulable_data = {} # Track schedulable links


    # Used after a spider has finished crawling the data and add new data to the queue
    def register_schedulable(self, key: str, data):
        hashed_key = generate_key(key)  # Hash the key
        with self.lock:
            self.schedulable_data[hashed_key] = data

    def unregister_schedulable(self, key: str):
        hashed_key = generate_key(key)  # Hash the key
        with self.lock:
            if hashed_key in self.schedulable_data:
                del self.schedulable_data[hashed_key]

    def get_schedulable_data(self, key: str):
        hashed_key = generate_key(key)  # Hash the key
        with self.lock:
            return self.schedulable_data.get(hashed_key)


    # Spider will enqueue a request to the scheduler
    def enqueue_request(self, request: dict, priority: int = 0):
        with self.lock:
            heapq.heappush(self.priority_queue, (priority, request))
    # Spider will have their request dequeued
    def dequeue_request(self):
        with self.lock:
            if not self.priority_queue:
                return None
            return heapq.heappop(self.priority_queue)[1]

    def is_empty(self):
        with self.lock:
            return len(self.priority_queue) == 0

    def size(self):
        with self.lock:
            return len(self.priority_queue)
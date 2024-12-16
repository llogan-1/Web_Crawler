import heapq
from threading import Lock

class Scheduler:
    def __init__(self):
        self.request_queue = []  # Internal priority queue using heapq
        self.lock = Lock()
        self.schedulable_data = {} # Track schedulable links
        self.spider_assignments = {} # Track what spiders are working on


    # Used after a spider has finished crawling the data and add new data to the queue
    def register_schedulable(self, data : str):
        if data == "https://en.wikipedia.org/wiki/Main_Page": # IF RUNNING APPLICATION MULTIPLE TIMES, THIS WILL ENSURE WE DONT REDO STARTING
            pass
        with self.lock:
            self.schedulable_data[data] = {'status': 'available'}

    def unregister_schedulable(self, data: str):
        with self.lock:
            if data in self.schedulable_data:
                del self.schedulable_data[data]

    def get_schedulable_data(self, data: str):
        with self.lock:
            return self.schedulable_data.get(data)


    # Spider will enqueue a request to the scheduler
    def enqueue_request(self, spider_id):
        with self.lock:
            self.request_queue.append(spider_id)
    
    # Spider will have their request dequeued
    def dequeue_request(self):
        with self.lock:
            if not self.priority_queue:
                return None
            return self.request_queue.popleft()


    # Assign a schedulable item to a spider
    def assign_item_to_spider(self, spider_id: str):
        with self.lock:
            if not self.request_queue:
                return None
            item  = self.schedulable_data.pop(0)
            if item.get('status', 'available') == 'available':
                item['status'] = 'in-progress'  # Mark item as in-progress
                self.spider_assignments[spider_id] = item  # Track item given to spider_id
                return item # return data of item to spider
            print("No item to give to spider or status issue")
            return False
    
    # Mark a schedulable item as completed by a spider
    def complete_item(self, spider_id: str):
        with self.lock:
            if spider_id in self.spider_assignments:
                item = self.spider_assignments.pop(spider_id) # Get item and remove spider
                if item in self.schedulable_data:
                    self.schedulable_data[item] = 'completed'
                    return True
            return False


    def is_empty(self):
        with self.lock:
            return len(self.request_queue) == 0

    def size(self):
        with self.lock:
            return len(self.request_queue)
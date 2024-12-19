from threading import Lock

class Scheduler:
    def __init__(self):
        self.lock = Lock()
        self.schedulable_data = [] # Temporary data type
        self.spider_assignments = {}

    # Assign a schedulable item to a spider
    def assign_item_to_spider(self, spider_id: str):
        with self.lock:
            item  = self.schedulable_data.pop(0)
            self.spider_assignments[spider_id] = item  # Track item given to spider_id
            return item # return data of item to spider

    def is_empty(self):
        with self.lock:
            return len(self.schedulable_data) == 0

    def size(self):
        with self.lock:
            return len(self.schedulable_data)

    def register_schedulable(self, data : str):
        with self.lock:
            self.schedulable_data.append(data)

    def unregister_schedulable(self, data : str):
        with self.lock:
            if data in self.schedulable_data:
                self.schedulable_data.remove(data)
    
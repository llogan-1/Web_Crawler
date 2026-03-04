import urllib.robotparser
from urllib.parse import urlparse
import time
from threading import Lock

class RobotsChecker:
    def __init__(self, user_agent='*'):
        self.user_agent = user_agent
        self.parsers = {}  # domain -> RobotFileParser
        self.lock = Lock()
        self.last_fetch_time = {} # domain -> last time robots.txt was fetched

    def _get_parser(self, url):
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        with self.lock:
            if domain not in self.parsers:
                parser = urllib.robotparser.RobotFileParser()
                parser.set_url(f"{domain}/robots.txt")
                try:
                    parser.read()
                    self.parsers[domain] = parser
                    self.last_fetch_time[domain] = time.time()
                except Exception as e:
                    print(f"Error reading robots.txt for {domain}: {e}")
                    # If we can't read it, we'll assume everything is allowed but log it
                    # Alternatively, create a parser that allows nothing if you want to be very safe
                    return None
            
            # Optional: Refresh robots.txt if it's older than 1 hour
            elif time.time() - self.last_fetch_time.get(domain, 0) > 3600:
                 try:
                    self.parsers[domain].read()
                    self.last_fetch_time[domain] = time.time()
                 except:
                    pass

            return self.parsers[domain]

    def is_allowed(self, url):
        parser = self._get_parser(url)
        if not parser:
            return True # If no robots.txt found, assume everything is allowed
        
        return parser.can_fetch(self.user_agent, url)

    def get_crawl_delay(self, url):
        parser = self._get_parser(url)
        if not parser:
            return None
        
        try:
            delay = parser.crawl_delay(self.user_agent)
            return delay
        except:
            return None

import urllib.robotparser
from urllib.parse import urlparse
import time
from threading import Lock
import requests

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
            if domain not in self.parsers or (time.time() - self.last_fetch_time.get(domain, 0) > 3600):
                robots_url = f"{domain}/robots.txt"
                parser = urllib.robotparser.RobotFileParser(url=robots_url)  # ← added
                
                headers = {
                    'User-Agent': self.user_agent,
                    'Accept': 'text/plain, */*'
                }
                
                try:
                    response = requests.get(robots_url, headers=headers, timeout=10)
                    code = response.status_code
                    
                    if code == 200:
                        parser.parse(response.text.splitlines())
                    elif code in (401, 403):
                        parser.parse(["User-agent: *", "Disallow: /"])
                        print(f"403/401 → treating as Disallow All: {domain}")
                    
                except Exception as e:
                    print(f"Error fetching robots.txt {robots_url}: {e}")
                    # Optionally: parser.parse(["Disallow: /"]) here too
                
                self.parsers[domain] = parser
                self.last_fetch_time[domain] = time.time()
            
            return self.parsers[domain]

    def is_allowed(self, url):
        """Check if the given URL is allowed to be crawled according to robots.txt."""
        parser = self._get_parser(url)
        # can_fetch expects user_agent and url
        return parser.can_fetch(self.user_agent, url)

    def get_crawl_delay(self, url):
        """Get the crawl delay for the given URL, if specified."""
        parser = self._get_parser(url)
        try:
            delay = parser.crawl_delay(self.user_agent)
            return delay
        except:
            return None

from html.parser import HTMLParser
from urllib import parse

class LinkFinder(HTMLParser):
    
    domain_name = ''

    # Add the keyword search here.

    def __init__(self, base_url, page_url, domain_name):
        super().__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.domain_name = domain_name
        self.links = set()

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    if ('#' not in url):
                        self.links.add(url)
    
    def page_links(self):
        return self.links
    

    def error(self, message):
        pass

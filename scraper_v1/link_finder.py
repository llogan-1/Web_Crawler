from html.parser import HTMLParser
from urllib import parse

class LinkFinder(HTMLParser):
    def __init__(self, base_url, page_url, domain_name):
        super().__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.domain_name = domain_name
        self.links = set()

    #check for duplicate links

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attribute, value in attrs:
                if attribute == "href":
                    url = parse.urljoin(self.base_url, value)

                    # Combined filtering conditions
                    if (
                        url.startswith(("http://", "https://"))  # Valid URL scheme
                        and self.domain_name in url  # Matches the target domain
                        and not any(url.lower().endswith(ext) for ext in [".jpg", ".png", ".pdf", ".zip", ".exe"])  # Excluded extensions
                        and "#" not in url  # Ignore anchors
                    ):
                        self.links.add(url)


    def page_links(self):
        return self.links

    def error(self, message):
        print(f"HTML parsing error: {message}")
        pass

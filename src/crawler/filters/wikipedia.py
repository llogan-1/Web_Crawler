from urllib.parse import urljoin
from .base import BaseFilter
import re
from bs4 import BeautifulSoup

class WikipediaFilter(BaseFilter):

    def __init__(self):
        super().__init__()

    def get_content_links(self, content_container, anchor):
        if not content_container:
            return []

        links = [a['href'] for a in content_container.find_all('a', href=True)]
        cleaned_links = [
            urljoin(anchor, link) for link in links
            if (
                link.startswith('/wiki/')
                and ':' not in link
                and '#' not in link
                and not re.search(r'\.\w+$', link)
                and WikipediaFilter.is_utf8_valid(link)
            )
        ]
        return list(set(cleaned_links))

    
    def extract_data(self, content_containers, anchor, raw_html=None):
        """
        Extract links, keywords, events, and metadata specifically for Wikipedia pages.
        """
        if not content_containers:
            return ([], [], [], {"date": None, "author": None, "description": None})
            
        main_container = content_containers[0]
        
        cleaned_links = self.get_content_links(main_container, anchor)
        content_text = self.get_div_ptext(main_container)
        keywords_keyevents = self.get_keywords_and_events(content_text)
        
        # Use BaseFilter's metadata extraction
        metadata = self.extract_metadata(raw_html) if raw_html else {"date": None, "author": None, "description": None}

        return (cleaned_links, keywords_keyevents[0], keywords_keyevents[1], metadata)
    
    @staticmethod
    def get_div_ptext(container):
        if not container:
            return ""
            
        paragraphs = container.find_all('p')
        content_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return content_text

    @staticmethod
    def get_divs(html):
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        content_div = soup.find('div', id='mw-content-text')
        
        return [content_div] if content_div else []

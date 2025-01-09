from urllib.parse import urljoin
from Filters.base_f import BaseFilter
import re
from bs4 import BeautifulSoup

class WikipediaFilter(BaseFilter):

    def __init__(self):
        # Inherrit BaseFilter 
        super()

    def get_content_links(self, content_div, anchor):
        if not content_div or not content_div[0]:  # Simplified validation
            raise ValueError("content_div is empty or None")

        soup = BeautifulSoup(content_div[0], 'html.parser')
        
        links = [a['href'] for a in soup.find_all('a', href=True)]
        cleaned_links = [
            urljoin(anchor, link) for link in links
            if (
                link.startswith('/wiki/')
                and '#' not in link
                and not re.search(r'\.\w+$', link)
                and WikipediaFilter.is_utf8_valid(link)
            )
        ]
        return cleaned_links

    
    # Returns a tuple of lists:  (Links, KeyWords, KeyEvents)
    def extract_data(self, content_divs, anchor):
        cleaned_links = self.get_content_links(content_divs, anchor)
        content_text = self.get_div_ptext(content_divs[0])
        keywords_keyevents = self.get_keywords_and_events(content_text)

        return (cleaned_links, keywords_keyevents[0], keywords_keyevents[1])
    
    # Accept a single div in the form of a string, and return on the paragraph text
    @staticmethod
    def get_div_ptext(div):
        if not div:
            return ""
        soup = BeautifulSoup(div, 'html.parser')
        content_text = ""
        if div:
            paragraphs = soup.find_all('p')  # Find all <p> tags
            content_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        else:
            print("END CRAWLING PROCESS***")
        return content_text

    # Assume HTML is not empty and in proper HTML format.
    @staticmethod
    def get_divs(HTML):
        """Parse and extract content divisions."""
        soup = BeautifulSoup(HTML, 'html.parser')
        content_div = [str(soup.find('div', id='mw-content-text'))]
        return content_div
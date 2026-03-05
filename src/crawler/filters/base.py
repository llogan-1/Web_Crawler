from urllib.parse import urljoin
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from collections import Counter
from bs4 import BeautifulSoup
import re

# Global stop words for filtering
stop_words = set(stopwords.words("english"))

# Common identifiers for content areas
COMMON_IDENTIFIERS = [
    "content", "main", "article", "post", "container", "body-content", 
    "content-wrapper", "main-content", "entry-content", "post-content"
]

# Semantic tags
SEMANTIC_TAGS = ["main", "article", "section"]

# Noise tags
NOISE_TAGS = ["script", "style", "nav", "footer", "header", "aside", "form"]

class BaseFilter:
    """
    The base class for all content filters.
    
    Provides common logic for extracting content, links, metadata, and 
    keywords from HTML. Can be subclassed for site-specific logic.
    """
    
    def __init__(self):
        """
        Initialize the BaseFilter.
        """
        pass

    @staticmethod
    def get_divs(html):
        """
        Identify and extract the main content containers from HTML.

        Args:
            html (str): Raw HTML content.

        Returns:
            list: A list of BeautifulSoup tag objects representing content containers.
        """
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        content_containers = []

        for tag_name in SEMANTIC_TAGS:
            for tag in soup.find_all(tag_name):
                if tag not in content_containers:
                    content_containers.append(tag)

        if len(content_containers) < 1:
            for identifier in COMMON_IDENTIFIERS:
                tag_by_id = soup.find(id=identifier)
                if tag_by_id and tag_by_id not in content_containers:
                    content_containers.append(tag_by_id)
                
                for tag in soup.find_all(class_=identifier):
                    if tag not in content_containers:
                        content_containers.append(tag)

        if not content_containers and soup.body:
            content_containers.append(soup.body)

        return content_containers

    def extract_metadata(self, html):
        """
        Extract publication date, author, and description from HTML metadata tags.

        Args:
            html (str): Raw HTML content.

        Returns:
            dict: A dictionary containing 'date', 'author', and 'description'.
        """
        if not html:
            return {"date": None, "author": None, "description": None}
            
        soup = BeautifulSoup(html, 'html.parser')
        metadata = {"date": None, "author": None, "description": None}
        
        # 1. Description
        desc_tag = soup.find("meta", attrs={"name": "description"}) or \
                   soup.find("meta", attrs={"property": "og:description"})
        if desc_tag:
            metadata["description"] = desc_tag.get("content", "").strip()
            
        # 2. Author
        author_tag = soup.find("meta", attrs={"name": "author"}) or \
                     soup.find("meta", attrs={"property": "article:author"}) or \
                     soup.find(attrs={"rel": "author"})
        if author_tag:
            metadata["author"] = author_tag.get("content", author_tag.get_text()).strip()
        else:
            # Fallback for common author class names
            author_element = soup.find(class_=re.compile(r'author|byline|creator', re.I))
            if author_element:
                metadata["author"] = author_element.get_text().strip()
                
        # 3. Publication Date
        date_tag = soup.find("meta", attrs={"name": "publish-date"}) or \
                   soup.find("meta", attrs={"property": "article:published_time"}) or \
                   soup.find("meta", attrs={"name": "dcterms.created"}) or \
                   soup.find("time", attrs={"datetime": True})
        if date_tag:
            metadata["date"] = date_tag.get("datetime", date_tag.get("content", date_tag.get_text())).strip()
        else:
            # Fallback for common date class names
            date_element = soup.find(class_=re.compile(r'date|published|time', re.I))
            if date_element:
                metadata["date"] = date_element.get_text().strip()
                
        return metadata

    def get_keywords_and_events(self, text):
        """
        Process text to extract significant keywords (nouns) and events (verbs).

        Args:
            text (str): Cleaned text content from a page.

        Returns:
            tuple: (keywords, events) where each is a list of (word, count) tuples.
        """
        try:
            if not text or not BaseFilter.is_utf8_valid(text):
                return ([], [])

            preprocessed_text = BaseFilter.preprocess_text_nltk(text)
            words = word_tokenize(preprocessed_text)
            filtered_words = [word for word in words if word.lower() not in stop_words and word.isalpha()]
            
            if not filtered_words:
                return ([], [])

            pos_tags = pos_tag(filtered_words)
            all_keywords = [word for word, tag in pos_tags if tag.startswith("NN")]
            keywords = Counter(all_keywords).most_common(5)
            all_events = [word for word, tag in pos_tags if tag in {"VBD", "VBN"}]
            events = Counter(all_events).most_common(3)
            
            return (keywords, events)
        except Exception as e:
            print(f"Error processing text for keywords/events: {e}")
            return ([], [])

    def extract_data(self, content_containers, anchor, raw_html=None):
        """
        High-level method to extract all required data from content containers.

        Args:
            content_containers (list): List of BeautifulSoup tag objects.
            anchor (str): Base URL for resolving relative links.
            raw_html (str, optional): The original raw HTML for metadata extraction.

        Returns:
            tuple: (links, keywords, events, metadata)
        """
        if not content_containers:
            return ([], [], [], {"date": None, "author": None, "description": None})

        combined_text = self.get_div_text(content_containers)
        links = self.get_content_links_from_containers(content_containers, anchor)
        keywords, events = self.get_keywords_and_events(combined_text)
        
        metadata = self.extract_metadata(raw_html) if raw_html else {"date": None, "author": None, "description": None}

        return (links, keywords, events, metadata)
    
    def get_content_links_from_containers(self, containers, anchor):
        """
        Extract and resolve all internal links from the provided containers.

        Args:
            containers (list): List of BeautifulSoup tag objects.
            anchor (str): Base URL to ensure links remain within the target site.

        Returns:
            list: A list of absolute URLs.
        """
        unique_links = set()
        for container in containers:
            for a in container.find_all('a', href=True):
                href = a['href'].strip()
                if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    continue
                full_url = urljoin(anchor, href)
                if full_url.startswith(anchor):
                    unique_links.add(full_url)
        return list(unique_links)

    def get_div_text(self, containers):
        """
        Extract and clean text content from the provided containers.

        Args:
            containers (list): List of BeautifulSoup tag objects.

        Returns:
            str: Combined and cleaned text.
        """
        cleaned_text_parts = []
        import copy
        for container in containers:
            container_copy = copy.copy(container)
            for noise_tag in container_copy.find_all(NOISE_TAGS):
                noise_tag.decompose()
            text = container_copy.get_text(separator=' ', strip=True)
            if text:
                cleaned_text_parts.append(text)
        return " ".join(cleaned_text_parts)

    @staticmethod
    def is_relative_link(link):
        """
        Check if a link is relative.

        Args:
            link (str): The URL/path to check.

        Returns:
            bool: True if relative, False otherwise.
        """
        return not (link.startswith('http://') or link.startswith('https://') or link.startswith('www.'))

    @staticmethod
    def is_utf8_valid(text):
        """
        Validate if the text can be encoded/decoded as UTF-8.

        Args:
            text (str or bytes): The text to validate.

        Returns:
            bool: True if valid UTF-8, False otherwise.
        """
        try:
            if isinstance(text, bytes):
                text.decode("utf-8")
            else:
                text.encode("utf-8")
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False
        
    @staticmethod
    def preprocess_text_nltk(text):
        """
        Clean text for NLTK processing by removing non-alphanumeric characters.

        Args:
            text (str): Raw text.

        Returns:
            str: Cleaned text.
        """
        import re
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()

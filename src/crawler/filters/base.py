from urllib.parse import urljoin
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from collections import Counter
from bs4 import BeautifulSoup

# Global stop words for filtering
stop_words = set(stopwords.words("english"))

# Common identifiers for content areas across different website architectures
COMMON_IDENTIFIERS = [
    "content", "main", "article", "post", "container", "body-content", 
    "content-wrapper", "main-content", "entry-content", "post-content"
]

# Semantic tags that usually contain the primary content of a page
SEMANTIC_TAGS = ["main", "article", "section"]

# Noise tags to be removed before text analysis
NOISE_TAGS = ["script", "style", "nav", "footer", "header", "aside", "form"]

class BaseFilter:
    
    def __init__(self):
        pass

    @staticmethod
    def get_divs(html):
        """
        Extract relevant content containers from the HTML.
        Looks for semantic tags first, then falls back to common IDs and classes.
        """
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        content_containers = []

        # 1. Search for semantic tags
        for tag_name in SEMANTIC_TAGS:
            found_tags = soup.find_all(tag_name)
            for tag in found_tags:
                if tag not in content_containers:
                    content_containers.append(tag)

        # 2. Search for common IDs and classes if we haven't found much
        if len(content_containers) < 1:
            for identifier in COMMON_IDENTIFIERS:
                # Search by ID
                tag_by_id = soup.find(id=identifier)
                if tag_by_id and tag_by_id not in content_containers:
                    content_containers.append(tag_by_id)
                
                # Search by Class
                tags_by_class = soup.find_all(class_=identifier)
                for tag in tags_by_class:
                    if tag not in content_containers:
                        content_containers.append(tag)

        # 3. Fallback to body if nothing specific was found
        if not content_containers and soup.body:
            content_containers.append(soup.body)

        return content_containers
    
    def get_keywords_and_events(self, text):
        """
        Extract the most common keywords (nouns) and events (past-tense verbs) from text.
        """
        try:
            if not text or not BaseFilter.is_utf8_valid(text):
                return ([], [])

            # Preprocess the text
            preprocessed_text = BaseFilter.preprocess_text_nltk(text)
            words = word_tokenize(preprocessed_text)
            
            # Remove stopwords and non-alphabetic tokens
            filtered_words = [word for word in words if word.lower() not in stop_words and word.isalpha()]
            
            if not filtered_words:
                return ([], [])

            # Extract POS tags
            pos_tags = pos_tag(filtered_words)
            
            # Extract keywords (nouns: NN, NNP, NNS, NNPS)
            all_keywords = [word for word, tag in pos_tags if tag.startswith("NN")]
            keywords = Counter(all_keywords).most_common(5)
            
            # Extract events (verbs in past tense: VBD, VBN)
            all_events = [word for word, tag in pos_tags if tag in {"VBD", "VBN"}]
            events = Counter(all_events).most_common(3)
            
            return (keywords, events)
        except Exception as e:
            print(f"Error processing text for keywords/events: {e}")
            return ([], [])

    def extract_data(self, content_containers, anchor):
        """
        High-level method to extract links, keywords, and events from identified containers.
        """
        if not content_containers:
            return ([], [], [])

        # Extract clean text from all containers
        combined_text = self.get_div_text(content_containers)
        
        # Extract links from all containers (better than extracting from combined text)
        links = self.get_content_links_from_containers(content_containers, anchor)
        
        # Extract keywords and events from the cleaned text
        keywords, events = self.get_keywords_and_events(combined_text)

        return (links, keywords, events)
    
    def get_content_links_from_containers(self, containers, anchor):
        """
        Extract unique, valid links from the provided list of BS4 tag objects.
        """
        unique_links = set()
        for container in containers:
            for a in container.find_all('a', href=True):
                href = a['href'].strip()
                if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    continue
                
                # Resolve relative URLs
                full_url = urljoin(anchor, href)
                
                # Filter by anchor (domain-specific crawling)
                if full_url.startswith(anchor):
                    unique_links.add(full_url)

        return list(unique_links)

    def get_div_text(self, containers):
        """
        Extract and clean text content from a list of BS4 tag objects.
        Removes noise like scripts, styles, and navigation.
        """
        cleaned_text_parts = []
        
        for container in containers:
            # Create a copy to avoid modifying the original soup if used elsewhere
            # Though here get_divs usually provides fresh objects
            import copy
            container_copy = copy.copy(container)
            
            # Remove noise tags
            for noise_tag in container_copy.find_all(NOISE_TAGS):
                noise_tag.decompose()
            
            # Extract text with a space separator to prevent word merging
            text = container_copy.get_text(separator=' ', strip=True)
            if text:
                cleaned_text_parts.append(text)

        return " ".join(cleaned_text_parts)

    @staticmethod
    def is_relative_link(link):
        """Check if a link is relative."""
        return not (link.startswith('http://') or link.startswith('https://') or link.startswith('www.'))

    @staticmethod
    def is_utf8_valid(text):
        """Check if a string is valid UTF-8."""
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
        """Normalize text by removing common punctuation and special characters."""
        # More robust cleaning
        import re
        # Replace non-alphanumeric characters (except spaces) with spaces
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        # Collapse multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()

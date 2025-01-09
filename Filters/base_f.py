from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from collections import Counter
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

stop_words = set(stopwords.words("english"))
common_tags = [
    "content",        # Main content section
    "main",           # Primary content wrapper
    "footer",         # Footer content
    "sidebar",        # Side navigation or additional info
    "container",      # General-purpose container
    "nav",            # Navigation menu
    "article",        # Article content
    "blog",           # Blog post content
    "comments",       # User comments section
    "products",       # Product listings in e-commerce
    "post",           # Blog post or forum entry
    "description",    # Description of content or products
    "details",        # Content details or metadata
    "body-content",   # Main body content
    "summary",        # Summarized information
    "content-wrapper", # Wrapper for primary content
    "search-results", # Search results page
    "hero",           # Hero section at the top of the page
    "profile",        # User profile data
    "contact-info",   # Contact information
    "title",          # Page or post title
]


class BaseFilter:
    
    def __init__(self):
        pass

    # Assume HTML is not empty and in proper HTML format.
    # If no relevant divs, returns empty list to be flagged.
    @staticmethod
    def get_divs(HTML):
        soup = BeautifulSoup(HTML, 'html.parser')
        
        content_divs = []
        for div in common_tags:
            content_divs.append(soup.find('div', id=div))

        return content_divs
    
    def get_keywords_and_events(self, text):
        try:
            if not BaseFilter.is_utf8_valid(text):
                print("Invalid UTF-8 text, skipping...")
                return ([], [])

            # Preprocess the text
            preprocessed_text = BaseFilter.preprocess_text_nltk(text)
            words = word_tokenize(preprocessed_text)
            
            # Remove stopwords
            filtered_words = [word for word in words if word.lower() not in stop_words]
            
            # Extract POS tags
            pos_tags = pos_tag(filtered_words)
            
            # Extract keywords (nouns and proper nouns)
            all_keywords = [word for word, tag in pos_tags if tag in {"NN", "NNP"}]
            keywords = Counter(all_keywords).most_common(3)
            
            # Extract events (verbs in past tense)
            all_events = [word for word, tag in pos_tags if tag in {"VBD", "VBN"}]
            events = Counter(all_events).most_common(2)
            
            return (keywords, events)
        except Exception as e:
            # Log the exception (optional) and return empty lists
            print(f"Error processing text: {e}")
            return ([], [])

    # Returns a tuple of lists:  (Links, KeyWords, KeyEvents)
    def extract_data(self, content_divs, anchor):
        content = self.get_div_text(content_divs)

        links = self.get_content_links(content, anchor)
        keywords_keyevents = self.get_keywords_and_events(content)

        return (links, keywords_keyevents[0], keywords_keyevents[1])
    
    
    def get_content_links(self, content, anchor):
        links = []

        soup = BeautifulSoup(content, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith(anchor):
                links.append(href)
            if BaseFilter.is_relative_link(href):
                links.append(anchor + href)

        return links


    # Accept a list of divs in the form of a string, and return the paragraph text
    def get_div_text(self, divs : str):
        content_text = ""
        for div in divs:
            content_text += str(div)
        return content_text

    # Function to check if a link is relative
    @staticmethod
    def is_relative_link(link):
        return not (link.startswith('http://') or link.startswith('https://') or link.startswith('www.'))


    @staticmethod
    def is_utf8_valid(text):
        """Check if a string is valid UTF-8."""
        try:
            text.encode("utf-8")
            return True
        except UnicodeEncodeError:
            return False
        
    @staticmethod
    def preprocess_text_nltk(text):
        cleaned_text = (
            text.replace("\n", " ")  # Normalize text
            .replace("(", " ")
            .replace(")", " ")
            .replace("[", " ")
            .replace("]", " ")
            .replace(",", " ")
            .replace(";", " ")
        )
        return cleaned_text
    
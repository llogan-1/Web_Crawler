from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from collections import Counter
import re
from urllib.parse import urljoin, urlparse

stop_words = set(stopwords.words("english"))

class BaseFilter:
    def get_content_links(self, content_div, anchor):
        """Override this method in subclasses."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def get_catlinks(self, catlinks_div, anchor):
        """Override this method in subclasses."""
        raise NotImplementedError("This method should be implemented by subclasses.") 
    
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

    def is_internal_link(anchor, link):
        base_domain = urlparse(anchor).netloc  # Get the domain from the anchor
        link_domain = urlparse(urljoin(anchor, link)).netloc  # Get the domain of the full link

        return base_domain == link_domain  # Compare the domains
    
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
    
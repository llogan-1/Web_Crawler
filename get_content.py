from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from collections import Counter
import re
from urllib.parse import urljoin, urlparse

stop_words = set(stopwords.words("english"))

def is_utf8_valid(text):
    """Check if a string is valid UTF-8."""
    try:
        text.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False

def get_catlinks(catlinks_div, anchor):
    try:
        if catlinks_div:
            catlinks = [
                urljoin(anchor, a['href']) for a in catlinks_div.find_all('a', href=True)
                if is_internal_link(anchor, a['href']) and is_utf8_valid(a['href'])  # Only include valid UTF-8 links
            ]
            # Skip the first link if the list isn't empty
            return catlinks[1:] if len(catlinks) > 1 else []
        else:
            return []
    except Exception as e:
        print(f"Error processing category links: {e}")
        return []

def get_content_links(content_div, anchor):
    try:
        if content_div:
            links = [a['href'] for a in content_div.find_all('a', href=True)]
            cleaned_links = [
                urljoin(anchor, link) for link in links
                if (
                    is_internal_link(anchor, link)
                    and link.startswith('/wiki/')
                    and '#' not in link
                    and not re.search(r'\.\w+$', link)
                    and is_utf8_valid(link)  # Ensure the link is valid UTF-8
                )
            ]
            return cleaned_links
        else:
            return []
    except Exception as e:
        print(f"Error processing content links: {e}")
        return []

def get_keywords_and_events(text):
    try:
        if not is_utf8_valid(text):
            print("Invalid UTF-8 text, skipping...")
            return ([], [])

        # Preprocess the text
        preprocessed_text = preprocess_text_nltk(text)
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

def is_internal_link(anchor, link):
    base_domain = urlparse(anchor).netloc  # Get the domain from the anchor
    link_domain = urlparse(urljoin(anchor, link)).netloc  # Get the domain of the full link

    return base_domain == link_domain  # Compare the domains

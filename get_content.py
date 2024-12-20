import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag, ne_chunk
from collections import Counter

stop_words = set(stopwords.words("english"))

def get_catlinks(catlinks_div):
    prefix = "https://en.wikipedia.org"
    if catlinks_div:
        catlinks = [prefix + a['href'] for a in catlinks_div.find_all('a', href=True)]
        if catlinks:  # Remove the first item if the list is not empty
            catlinks.pop(0)
    else:
        catlinks = []
    return catlinks

import re

def get_content_links(content_div):
    # Tokenize and clean the text
    if content_div:
        links = [a['href'] for a in content_div.find_all('a', href=True)]
        content_links = clean_links(links)

        # Filter links to exclude any that end with a file extension (e.g., .pdf, .jpg, etc.)
        content_links = [link for link in content_links if not re.search(r'\.\w+$', link)]
    else:
        content_links = []
        
    return content_links


def get_keywords_and_events(text):
    preprocessed_text = preprocess_text_nltk(text)
    words = word_tokenize(preprocessed_text)
    #Remove stopwords
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

def clean_links(links):
    cleaned_links = []
    for link in links:
        if link[0] != '/':
            pass
        else:
            if '#' not in link:
                cleaned_links.append('https://en.wikipedia.org' +link)
    return cleaned_links
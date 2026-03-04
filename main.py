import sys
import os
import argparse
import nltk

# Ensure NLTK data is available
def setup_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK punkt tokenizer...")
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("Downloading NLTK stopwords...")
        nltk.download('stopwords')

    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        print("Downloading NLTK averaged_perceptron_tagger...")
        nltk.download('averaged_perceptron_tagger')

    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            nltk.download('punkt_tab', quiet=True)
        except:
            pass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from crawler.core.engine import Engine
    from crawler.filters.wikipedia import WikipediaFilter
    from crawler.filters.base import BaseFilter
except ImportError as e:
    print(f"Error: Could not import crawler modules. {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Web Crawler Entry Point")
    parser.add_argument("--start-url", type=str, default="https://en.wikipedia.org/wiki/Main_Page",
                        help="The initial URL to start crawling from.")
    parser.add_argument("--base-url", type=str, default="https://en.wikipedia.org",
                        help="The base URL/anchor for filtering links.")
    parser.add_argument("--mins", type=int, default=1,
                        help="Duration of the crawling process in minutes.")
    parser.add_argument("--threads", type=int, default=2,
                        help="Number of crawler threads.")
    parser.add_argument("--filter", type=str, choices=["wikipedia", "base"], default="wikipedia",
                        help="The type of filter to use (default: wikipedia).")

    args = parser.parse_args()

    # Setup NLTK data
    setup_nltk()

    # Initialize the selected filter
    if args.filter == "wikipedia":
        crawler_filter = WikipediaFilter()
    else:
        crawler_filter = BaseFilter()

    website_info = (args.start_url, args.base_url)

    print(f"Starting Web Crawler...")
    print(f"  Start URL: {args.start_url}")
    print(f"  Base URL:  {args.base_url}")
    print(f"  Duration:  {args.mins} minute(s)")
    print(f"  Threads:   {args.threads}")
    print(f"  Filter:    {args.filter}")

    try:
        Engine(website_info, args.mins, crawler_filter, args.threads)
        print("Crawling completed.")
    except Exception as e:
        print(f"An error occurred during crawling: {e}")

if __name__ == "__main__":
    main()

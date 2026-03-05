import sys
import requests

# Set UTF-8 as the default encoding
sys.stdout.reconfigure(encoding='utf-8')

class HTMLFetcher:
    """
    Utility class for fetching HTML content from the web.
    """
    def __init__(self):
        """
        Initialize the HTMLFetcher.
        """
        pass

    @staticmethod
    def fetch_html(url: str, user_agent: str = None):
        """
        Fetch HTML content and cookies from a given URL.

        Args:
            url (str): The URL to fetch.
            user_agent (str, optional): Custom User-Agent string to use.

        Returns:
            tuple: (html_content, cookies) if successful, otherwise (None, None).
        """
        # Default user agent if none provided
        ua = user_agent if user_agent else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        
        headers = {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extract cookies
            cookies = response.cookies.get_dict()
            
            html_content = response.content.decode(response.apparent_encoding, errors='replace')
            return (html_content, cookies)
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return (None, None)

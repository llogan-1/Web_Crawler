import sys
import requests

# Set UTF-8 as the default encoding
sys.stdout.reconfigure(encoding='utf-8')

class HTMLFetcher:
    def __init__(self):
        pass

    def fetch_html(url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.content.decode(response.apparent_encoding, errors='replace')
            return html_content
        except Exception as e:
            print(f"Error fetching URL: {e}")
            return ""
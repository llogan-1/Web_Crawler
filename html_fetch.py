import requests

class HTMLFetcher:
    """
    Class designated to simply extract all HTML code from a website
    """
    def __init__(self):
        pass # Doesn't need to do anything

    def fetch_html(self, url):
        try:
            # Request the url for code
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                return response.text
            else:
                return f"Error: Unable to fetch the webpage. Status code: {response.status_code}"
        except Exception as e:
            return f"An error occurred: {e}"
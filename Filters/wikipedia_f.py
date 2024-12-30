from urllib.parse import urljoin
from Filters.base_f import BaseFilter
import re

class WikipediaFilter(BaseFilter):
    def get_content_links(self, content_div, anchor):
        super()
        if content_div:
            links = [a['href'] for a in content_div.find_all('a', href=True)]
            cleaned_links = [
                urljoin(anchor, link) for link in links
                if (
                    link.startswith('/wiki/')
                    and '#' not in link
                    and not re.search(r'\.\w+$', link)
                    and WikipediaFilter.is_utf8_valid(link)
                )
            ]
            return cleaned_links
        return []

    def get_catlinks(self, catlinks_div, anchor):
        if catlinks_div:
            catlinks = [
                urljoin(anchor, a['href']) for a in catlinks_div.find_all('a', href=True)
                if a['href'].startswith('/wiki/Category:')
            ]
            # Drop the first catlink as it is always the name "catagory", which is not helpful.
            return catlinks[1:] if len(catlinks) > 1 else []
        return []
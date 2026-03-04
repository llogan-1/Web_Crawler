import unittest
import sys
import os
from bs4 import BeautifulSoup

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from crawler.filters.base import BaseFilter
from crawler.filters.wikipedia import WikipediaFilter

class TestBaseFilter(unittest.TestCase):
    def setUp(self):
        self.filter = BaseFilter()

    def test_is_relative_link(self):
        self.assertTrue(BaseFilter.is_relative_link("/wiki/Python"))
        self.assertFalse(BaseFilter.is_relative_link("http://example.com"))
        self.assertFalse(BaseFilter.is_relative_link("https://example.com"))
        self.assertFalse(BaseFilter.is_relative_link("www.example.com"))

    def test_preprocess_text_nltk(self):
        text = "Hello (world), [this] is; a test\n"
        expected = "Hello world this is a test"
        self.assertEqual(BaseFilter.preprocess_text_nltk(text), expected)

    def test_get_div_text(self):
        html1 = "<div>part1 <script>alert(1)</script></div>"
        html2 = "<div>part2 <style>.css{}</style></div>"
        soup1 = BeautifulSoup(html1, 'html.parser').div
        soup2 = BeautifulSoup(html2, 'html.parser').div
        self.assertEqual(self.filter.get_div_text([soup1, soup2]), "part1 part2")

    def test_extract_metadata(self):
        html = '''
        <html>
            <head>
                <meta name="description" content="Test description">
                <meta name="author" content="Test Author">
                <time datetime="2023-10-27">October 27</time>
            </head>
        </html>
        '''
        meta = self.filter.extract_metadata(html)
        self.assertEqual(meta["description"], "Test description")
        self.assertEqual(meta["author"], "Test Author")
        self.assertEqual(meta["date"], "2023-10-27")

class TestWikipediaFilter(unittest.TestCase):
    def setUp(self):
        self.filter = WikipediaFilter()

    def test_get_div_ptext(self):
        html = '<div><p>Paragraph 1.</p><p>Paragraph 2.</p></div>'
        soup = BeautifulSoup(html, 'html.parser').div
        text = WikipediaFilter.get_div_ptext(soup)
        self.assertEqual(text, "Paragraph 1. Paragraph 2.")

    def test_get_content_links_wikipedia(self):
        html = '<div><a href="/wiki/Python">Python</a><a href="/wiki/File:Image.jpg">File</a><a href="http://other.com">Other</a></div>'
        soup = BeautifulSoup(html, 'html.parser').div
        anchor = "https://en.wikipedia.org"
        links = self.filter.get_content_links(soup, anchor)
        self.assertIn("https://en.wikipedia.org/wiki/Python", links)
        self.assertNotIn("https://en.wikipedia.org/wiki/File:Image.jpg", links)
        self.assertNotIn("http://other.com", links)

if __name__ == "__main__":
    unittest.main()

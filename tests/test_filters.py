import unittest
import sys
import os

# Add the parent directory to the sys.path to allow imports from the main project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Filters.base_f import BaseFilter
from Filters.wikipedia_f import WikipediaFilter
from bs4 import BeautifulSoup

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
        expected = "Hello  world    this  is  a test "
        self.assertEqual(BaseFilter.preprocess_text_nltk(text), expected)

    def test_get_div_text(self):
        divs = ["<div>part1</div>", "<div>part2</div>"]
        self.assertEqual(self.filter.get_div_text(divs), "<div>part1</div><div>part2</div>")

    def test_get_content_links(self):
        content = '<a href="/relative">Link 1</a><a href="http://external.com">Link 2</a>'
        anchor = "http://base.com"
        links = self.filter.get_content_links(content, anchor)
        self.assertIn("http://base.com/relative", links)

class TestWikipediaFilter(unittest.TestCase):
    def setUp(self):
        self.filter = WikipediaFilter()

    def test_get_div_ptext(self):
        html = '<div><p>Paragraph 1.</p><p>Paragraph 2.</p></div>'
        text = WikipediaFilter.get_div_ptext(html)
        self.assertEqual(text, "Paragraph 1. Paragraph 2.")

    def test_get_content_links_wikipedia(self):
        content_div = ['<div><a href="/wiki/Python">Python</a><a href="/wiki/File:Image.jpg">File</a><a href="http://other.com">Other</a></div>']
        anchor = "https://en.wikipedia.org"
        links = self.filter.get_content_links(content_div, anchor)
        self.assertIn("https://en.wikipedia.org/wiki/Python", links)
        self.assertNotIn("https://en.wikipedia.org/wiki/File:Image.jpg", links)
        self.assertNotIn("http://other.com", links)

if __name__ == "__main__":
    unittest.main()

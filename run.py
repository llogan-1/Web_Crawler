from engine import Engine
from Filters.wikipedia_f import WikipediaFilter
from Filters.base_f import BaseFilter

wikipedia_info = ("https://en.wikipedia.org/wiki/Eggs_as_food", "https://en.wikipedia.org/")
britannica_info = ("https://www.britannica.com/money/on-track-retirement-savings", "https://www.britannica.com/")

filter = BaseFilter()
# filter = WikiFilter()
thread_number = 8

# Ensure that this info is correct and corresponds the anchor website
if __name__ == "__main__":

    
    Engine(britannica_info, 5, filter, thread_number)

    print("\nEngine fully initalize... Program completed")
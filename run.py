from engine import Engine
from Filters.wikipedia_f import WikipediaFilter

wikipedia_info = ("https://en.wikipedia.org/wiki/Eggs_as_food", "https://en.wikipedia.org/")
filter = WikipediaFilter()

# Ensure that this info is correct and corresponds the anchor website
if __name__ == "__main__":
    
    Engine(wikipedia_info, 1, filter)

    print("\nengine fully initalize, program completed.")
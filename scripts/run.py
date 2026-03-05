import sys
import os

# Add the project root to sys.path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_path)

# Import the main function from the root main.py
from main import main

"""
A convenience script to run the web crawler from within the scripts directory.
"""

if __name__ == "__main__":
    main()

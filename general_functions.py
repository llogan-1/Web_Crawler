from pathlib import Path
from typing import Set
import os

#Each unique domain crawled is a seperate folder
#future, change storage location here

def create_project_dir(directory: str):
    project_path = Path(directory)
    if not project_path.exists():
        print(f'Creating project: {directory}')
        project_path.mkdir()

#Create queued and crawled files (IF NOT CREATED)

def create_data_files(project_name: str, base_url: str):
    queue_file = Path(project_name + '/queue.txt')
    crawled_file = Path(project_name + '/crawled.txt')
    if not queue_file.is_file():
        write_file(queue_file, base_url)
    if not crawled_file.is_file():
        write_file(crawled_file, '')

#creates a new data file

def write_file(path: Path, data: str):
    try: 
        with path.open('w') as f:
            f.write(data)
    except IOError as e:
        print(f"Error writing to {path}: {e}")

# Add data onto an existing file

def append_to_file(path, data):
    try:
        with path.open('a') as f:
            f.write(data + '\n')
    except IOError as e:
        print(f"Error appending to {path}: {e}")

# Delete contents of file

def delete_file_contents(path):
    try:    
        with path.open('w'):
            pass
    except IOError as e:
        print(f"Error deleting {path}: {e}")

# read a file and convert each line to set of items

# we added a newline char earlier, removing it may slow this program
def file_to_set(file_name):
    try:
        with file_name.open('r') as f:
            return {line.strip() for line in f}
    except IOError as e:
        print(f"Error reading {file_name} to set: {e}")

#iterate through a set, with each item being on a new linfe of the file

def set_to_file(links, file):
    delete_file_contents(file)
    for link in links:
        append_to_file(file, link)


#simple test code
if __name__ == "__main__":
    project_name = "test_project"
    base_url = "http://example.com"
    queue_file = Path(project_name) / 'queue.txt'
    crawled_file = Path(project_name) / 'crawled.txt'

    # Test creating a project directory
    create_project_dir(project_name)

    # Test creating data files
    create_data_files(project_name, base_url)

    # Test writing and reading from a file
    print(f"Contents of {queue_file}:")
    print(queue_file.read_text())  # Should contain the base URL

    # Test appending to a file
    append_to_file(queue_file, "http://example2.com")
    append_to_file(queue_file, "http://example3.com")

    # Test reading file into a set
    queue_set = file_to_set(queue_file)
    print(f"Set created from {queue_file}: {queue_set}")

    # Test set to file
    new_links = {"http://example4.com", "http://example5.com"}
    set_to_file(new_links, queue_file)
    print(f"Updated {queue_file} with new set:")
    print(queue_file.read_text())

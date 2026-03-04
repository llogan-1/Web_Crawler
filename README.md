# Domain Web Crawler

A flexible, multithreaded web crawler designed for efficient data extraction from specific domains. This project demonstrates foundational crawling techniques and integrates SQLite for data persistence, allowing content indexing and further processing.

## Features

- **Domain-specific Crawling**: Target only predefined websites to stay within legal and ethical boundaries.
- **HTML Parsing**: Fetches and processes HTML content efficiently.
- **Multithreading**: Utilizes concurrent spiders to enhance crawling speed.
- **Data Persistence**: Stores extracted data in a structured SQLite database.
- **Configurable Filters**: Apply custom filters to limit search depth, file types, or content patterns.

## Usage

The project now features a dynamic entry point `main.py` in the root directory. You can also use `scripts/run.py` which acts as a wrapper.

```bash
python main.py --help
```

Options:
- `--start-url`: The initial URL to start crawling from (default: Wikipedia Main Page).
- `--base-url`: The base URL/anchor for filtering links (default: https://en.wikipedia.org).
- `--mins`: Duration of the crawling process in minutes (default: 1).
- `--threads`: Number of crawler threads (default: 2).
- `--filter`: The type of filter to use (`wikipedia` or `base`).

### Example
To crawl Wikipedia for 5 minutes with 4 threads:
```bash
python main.py --mins 5 --threads 4
```

## Project Structure

- **`main.py`**: Dynamic entry point with CLI arguments.
- **`src/crawler/core/`**: Core logic including `engine.py`, `spider.py`, and `scheduler.py`.
- **`src/crawler/filters/`**: Filtering logic (e.g., `wikipedia.py`, `base.py`).
- **`src/crawler/database/`**: Database management logic.
- **`src/crawler/utils/`**: Utility functions like `html_fetch.py`.
- **`scripts/`**: Shortcut scripts like `run.py`.
- **`tests/`**: Unit tests for the various components.
- **`data/`**: Directory where SQLite databases are stored.

## Installation

1. Clone the repository:  
   ```bash
   git clone https://github.com/llogan-1/Web_Crawler.git
   cd Web_Crawler

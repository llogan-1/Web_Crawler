# Domain Web Crawler

A flexible, multithreaded web crawler designed for efficient data extraction from specific domains. This project demonstrates foundational crawling techniques and integrates SQLite for data persistence, allowing content indexing and further processing.

## Features

- **Domain-specific Crawling**: Target only predefined websites to stay within legal and ethical boundaries.
- **HTML Parsing**: Fetches and processes HTML content efficiently.
- **Multithreading**: Utilizes concurrent spiders to enhance crawling speed.
- **Data Persistence**: Stores extracted data in a structured SQLite database.
- **Configurable Filters**: Apply custom filters to limit search depth, file types, or content patterns.

## Project Structure

- **`run.py`**: Main entry point to initialize and control the crawling process.
- **`spider.py`**: Core class handling individual page requests and content extraction.
- **`scheduler.py`**: Manages task distribution and rate-limiting to optimize performance.
- **`html_fetch.py`**: Handles HTTP requests and basic error handling.
- **`engine.py`**: Coordinates crawlers and manages high-level operations.
- **`Filters/`**: Contains logic to filter links and content based on user-defined criteria.
- **`DataBases/`**: Stores SQLite databases for easy data querying.

## Installation

1. Clone the repository:  
   ```bash
   git clone https://github.com/llogan-1/Web_Crawler.git
   cd Web_Crawler

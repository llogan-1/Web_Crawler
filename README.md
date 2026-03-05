# Domain-Specific Web Crawler

A robust, multithreaded web crawler designed for efficient, domain-constrained data acquisition. This project features automated parsing pipelines, concurrency control, and relational storage for structured data ingestion.

## Key Features

- **Domain-Constrained Crawling**: Targeted data collection to ensure relevance and adhere to ethical/legal boundaries.
- **Automated Parsing & Metadata Extraction**: Leverages BeautifulSoup and NLTK to transform unstructured HTML into structured datasets (keywords, key events, and metadata).
- **Robots.txt Compliance**: Integrated `RobotsChecker` to respect `robots.txt` rules and crawl delays.
- **Relational Data Persistence**: Utilizes SQLite for session-based storage of tasks, crawled URLs, keywords, and cookies.
- **Performance Benchmarking**: Dedicated script to identify optimal thread counts for maximum throughput.

## Project Structure

```text
ROOT\
├── main.py              # CLI entry point for the crawler
├── requirements.txt     # Project dependencies
├── src/
│   └── crawler/
│       ├── core/
│       │   ├── engine.py    # Orchestration engine (threads, DB coordination)
│       │   ├── scheduler.py # Task management and URL distribution
│       │   └── spider.py    # Worker logic for fetching and processing pages
│       ├── database/
│       │   └── manager.py   # Database utility functions
│       ├── filters/
│       │   ├── base.py      # Base class for content filtering and extraction
│       │   └── wikipedia.py # Wikipedia-specific filter implementation
│       └── utils/
│           ├── html_fetch.py    # Robust HTML fetching with cookie support
│           └── robots_checker.py # robots.txt parsing and compliance
├── scripts/
│   ├── benchmark_threads.py # Performance testing script
│   └── run.py               # Simple wrapper for main.py
├── tests/               # Unit tests for core components
└── data/                # Directory for session-specific SQLite databases
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/llogan-1/Web_Crawler.git
   cd Web_Crawler
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Crawl

To start crawling with default settings (Wikipedia, 1 minute, 2 threads):

```bash
python main.py
```

### Advanced Options

```bash
python main.py --start-url "https://thewebsite.com/Page2/" \
               --base-url "https://thewebsite.com/" \
               --mins 5 \
               --threads 8 \
               --filter base
```

- `--start-url`: The initial URL to start crawling from.
- `--base-url`: The domain/path constraint to stay within.
- `--mins`: Duration of the crawling session in minutes.
- `--threads`: Number of concurrent worker threads.
- `--filter`: Choice of content filter (`wikipedia` or `base` or any added).

### Benchmarking

To identify the optimal number of threads for your environment:

```bash
python scripts/benchmark_threads.py
```

This script will run multiple crawl sessions with varying thread counts and generate a performance graph in the `scripts/` directory.

## Data Storage

Each crawl session creates a unique, timestamped folder in the `data/` directory (e.g., `data/crawl_20260305_120000/`). This folder contains:

- `scheduler.db`: Tracks pending and completed tasks.
- `crawled.db`: Stores extracted content, metadata, and keywords.

## Dependencies

- **requests**: For handling HTTP requests.
- **beautifulsoup4**: For HTML parsing and data extraction.
- **nltk**: For natural language processing (tokenization, stop words).
- **matplotlib**: For generating performance benchmark graphs.

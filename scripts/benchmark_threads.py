import time
import os
import subprocess
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import sys

# Identify the project root (one level up from this script)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MAIN_PY = os.path.join(PROJECT_ROOT, 'main.py')
DATA_ROOT = os.path.join(PROJECT_ROOT, 'data')

def run_crawl(threads, mins=0.5, url="https://en.wikipedia.org/wiki/Main_Page"):
    """
    Run the crawler with a specific thread count and measure throughput.

    Args:
        threads (int): The number of threads to use.
        mins (float): Duration of the test crawl in minutes.
        url (str): The starting URL for the test.

    Returns:
        float: The number of pages scraped per second.
    """
    print(f"\n--- Testing with {threads} threads ---")
    
    start_time = time.time()
    try:
        # Run main.py using its absolute path from the project root
        cmd = [
            sys.executable, MAIN_PY, 
            "--start-url", url, 
            "--threads", str(threads), 
            "--mins", str(mins),
            "--filter", "wikipedia"
        ]
        # We run the command with PROJECT_ROOT as the current working directory
        subprocess.run(cmd, check=True, capture_output=True, cwd=PROJECT_ROOT)
    except subprocess.CalledProcessError as e:
        print(f"Error during crawl: {e}")
        return 0

    actual_duration = time.time() - start_time

    # Find the latest crawl folder in the project's data directory
    if not os.path.exists(DATA_ROOT):
        return 0
        
    subdirs = [os.path.join(DATA_ROOT, d) for d in os.listdir(DATA_ROOT) 
               if os.path.isdir(os.path.join(DATA_ROOT, d)) and d.startswith("crawl_")]
    
    if not subdirs:
        return 0
        
    latest_dir = max(subdirs, key=os.path.getmtime)
    db_path = os.path.join(latest_dir, "crawled.db")

    pages_scraped = 0
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM urls")
        pages_scraped = cursor.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")

    pps = pages_scraped / actual_duration
    print(f"Results: {pages_scraped} pages in {actual_duration:.2f}s ({pps:.2f} pages/sec)")
    return pps

def main():
    """
    Perform a multi-threaded performance benchmark and plot the results.
    
    Tests various thread counts and saves a performance graph to the scripts directory.
    """
    # Thread counts to try
    #thread_counts = [1, 2, 4, 8, 16, 24, 32]
    #thread_counts = [32, 48, 64, 72, 92]
    thread_counts = [64, 72, 92, 100, 104, 108, 112, 124]
    
    results = []

    print(f"Starting Thread Benchmark (Root: {PROJECT_ROOT})...")
    
    for t in thread_counts:
        pps = run_crawl(t)
        results.append(pps)

    # Plotting the results
    plt.figure(figsize=(10, 6))
    plt.plot(thread_counts, results, marker='o', linestyle='-', color='b')
    plt.title('Crawler Performance Benchmark')
    plt.xlabel('Number of Threads')
    plt.ylabel('Pages Scraped per Second')
    plt.grid(True)
    
    # Save the plot in the project root
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_name = f"benchmark_results_{timestamp}.png"
    plot_path = os.path.join(PROJECT_ROOT, "scripts", plot_name)
    plt.savefig(plot_path)
    
    print("\n--- Benchmark Complete ---")
    for t, r in zip(thread_counts, results):
        print(f"Threads: {t:2d} | Pages/Sec: {r:.2f}")
    
    optimal_index = results.index(max(results))
    print(f"\nRecommended optimal thread count: {thread_counts[optimal_index]}")
    print(f"Graph saved to: {plot_path}")

if __name__ == "__main__":
    main()

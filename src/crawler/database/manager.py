import sqlite3
from urllib.parse import urlparse

# Function to connect to the database and retrieve its contents
def check_db_contents(db_path, table_name):
    """
    Connect to a database and print the contents of a specified table.

    Args:
        db_path (str): The file path to the SQLite database.
        table_name (str): The name of the table to inspect.

    Returns:
        list: A list of rows fetched from the table.
    """
    try:
        data = []
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query to get all data from the table
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Print the contents
        count = 0
        if rows:
            print(f"\n\n\nContents of {table_name} in {db_path}:\n\n\n")
            for row in rows:
                data.append(row)
                print(row)
                print("\n")
                count = count + 1
        else:
            print(f"No data found in {table_name} in {db_path}.")
        print(count)
        # Close the connection
        cursor.close()
        conn.close()
        return data

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def url_check(data, i):
    """
    Print a specific column from a list of data rows.

    Args:
        data (list): A list of data rows (tuples).
        i (int): The index of the column to print.
    """
    for d in data:
        print(d[i])


# Paths to your databases
crawled_db_path = "DataBases/crawled.db"
scheduler_db_path = "DataBases/scheduler.db"

# Table names in the databases
crawled_table = "crawled"  # Replace with the actual table name in your crawled DB
scheduler_table = "tasks"  # Replace with the actual table name in your scheduler DB

if __name__ == "__main__":
    # Check contents of both databases
    data = check_db_contents(crawled_db_path, crawled_table)
    #index = 1
    #url_check(data, wiki, 0)
    #url_check(data, wiki, index)
    check_db_contents(scheduler_db_path, scheduler_table)

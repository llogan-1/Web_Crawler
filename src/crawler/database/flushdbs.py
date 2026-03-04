import sqlite3

def drop_tables(scheduler_conn, crawler_conn):
    try:
        # Drop the crawled table from the crawled database
        with crawler_conn:
            cursor = crawler_conn.cursor()
            cursor.execute('''DROP TABLE IF EXISTS keywords;''')
            cursor.execute('''DROP TABLE IF EXISTS keyevents;''')
            cursor.execute('''DROP TABLE IF EXISTS urls;''')
            print("Tables dropped from crawled DB.")
        
        # Drop the tasks table from the scheduler database
        with scheduler_conn:
            cursor = scheduler_conn.cursor()
            cursor.execute('''DROP TABLE IF EXISTS tasks;''')
            print("Table 'tasks' dropped from scheduler DB.")
    
    except Exception as e:
        print(f"Error dropping tables: {e}")

if __name__ == "__main__":
    scheduler_conn = sqlite3.connect("DataBases/scheduler.db", check_same_thread=False)
    crawler_conn = sqlite3.connect("DataBases/crawled.db", check_same_thread=False)

    drop_tables(scheduler_conn,crawler_conn)
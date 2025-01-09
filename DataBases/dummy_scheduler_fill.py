import sqlite3

wikipedia_urls = [
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "https://en.wikipedia.org/wiki/Java_(programming_language)",
        "https://en.wikipedia.org/wiki/C_(programming_language)",
        "https://en.wikipedia.org/wiki/JavaScript",
        "https://en.wikipedia.org/wiki/HTML",
        "https://en.wikipedia.org/wiki/CSS",
        "https://en.wikipedia.org/wiki/SQL",
        "https://en.wikipedia.org/wiki/Database",
        "https://en.wikipedia.org/wiki/Computer_science",
        "https://en.wikipedia.org/wiki/Software_engineering",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Deep_learning",
        "https://en.wikipedia.org/wiki/Cloud_computing",
        "https://en.wikipedia.org/wiki/Blockchain",
        "https://en.wikipedia.org/wiki/Web_development",
        "https://en.wikipedia.org/wiki/Internet_of_things",
        "https://en.wikipedia.org/wiki/Big_data",
        "https://en.wikipedia.org/wiki/Data_science",
        "https://en.wikipedia.org/wiki/Quantum_computing",
        "https://en.wikipedia.org/wiki/Distributed_computing",
        "https://en.wikipedia.org/wiki/Operating_system",
        "https://en.wikipedia.org/wiki/Virtualization",
        "https://en.wikipedia.org/wiki/Computer_network",
        "https://en.wikipedia.org/wiki/Programming_language",
        "https://en.wikipedia.org/wiki/Pseudocode",
        "https://en.wikipedia.org/wiki/Debugging",
        "https://en.wikipedia.org/wiki/Version_control",
        "https://en.wikipedia.org/wiki/Git",
        "https://en.wikipedia.org/wiki/CI/CD",
        "https://en.wikipedia.org/wiki/Agile_software_development",
        "https://en.wikipedia.org/wiki/Software_testing",
        "https://en.wikipedia.org/wiki/Unit_testing",
        "https://en.wikipedia.org/wiki/Integration_testing",
        "https://en.wikipedia.org/wiki/Responsive_web_design",
        "https://en.wikipedia.org/wiki/Mobile_app_development",
        "https://en.wikipedia.org/wiki/UX_design",
        "https://en.wikipedia.org/wiki/User_interface",
        "https://en.wikipedia.org/wiki/Web_scraping",
        "https://en.wikipedia.org/wiki/API",
        "https://en.wikipedia.org/wiki/RESTful_API",
        "https://en.wikipedia.org/wiki/GraphQL",
        "https://en.wikipedia.org/wiki/JSON",
        "https://en.wikipedia.org/wiki/XML",
        "https://en.wikipedia.org/wiki/SEO",
        "https://en.wikipedia.org/wiki/Content_management_system",
        "https://en.wikipedia.org/wiki/Wiki",
        "https://en.wikipedia.org/wiki/Internet",
        "https://en.wikipedia.org/wiki/Web_crawling",
        "https://en.wikipedia.org/wiki/Scrapy",
        "https://en.wikipedia.org/wiki/Beautiful_Soup"
    ]

britannica_urls = [
    "https://www.britannica.com/animal/lion",
    "https://www.britannica.com/plant/rose-plant",
    "https://www.britannica.com/biography/Albert-Einstein",
    "https://www.britannica.com/place/France",
    "https://www.britannica.com/science/photosynthesis",
    "https://www.britannica.com/event/World-War-II",
    "https://www.britannica.com/technology/computer",
    "https://www.britannica.com/art/Mona-Lisa-painting",
    "https://www.britannica.com/topic/democracy",
    "https://www.britannica.com/biography/William-Shakespeare",
    "https://www.britannica.com/science/atom",
    "https://www.britannica.com/place/Mount-Everest",
    "https://www.britannica.com/biography/Marie-Curie",
    "https://www.britannica.com/science/relativity-physics",
    "https://www.britannica.com/event/French-Revolution",
    "https://www.britannica.com/biography/Leonardo-da-Vinci",
    "https://www.britannica.com/science/evolution-scientific-theory",
    "https://www.britannica.com/place/Great-Wall-of-China",
    "https://www.britannica.com/biography/Isaac-Newton",
    "https://www.britannica.com/science/quantum-mechanics",
    "https://www.britannica.com/event/American-Civil-War",
    "https://www.britannica.com/biography/Charles-Darwin",
    "https://www.britannica.com/science/black-hole-astronomy",
    "https://www.britannica.com/place/Egypt",
    "https://www.britannica.com/biography/Mahatma-Gandhi",
    "https://www.britannica.com/science/DNA",
    "https://www.britannica.com/event/Russian-Revolution",
    "https://www.britannica.com/biography/Nikola-Tesla",
    "https://www.britannica.com/science/climate-change",
    "https://www.britannica.com/place/United-Kingdom",
    "https://www.britannica.com/biography/Abraham-Lincoln",
    "https://www.britannica.com/event/Industrial-Revolution",
    "https://www.britannica.com/biography/Thomas-Edison",
    "https://www.britannica.com/science/plate-tectonics",
    "https://www.britannica.com/place/India",
    "https://www.britannica.com/biography/Christopher-Columbus",
    "https://www.britannica.com/science/electricity",
    "https://www.britannica.com/event/Cold-War",
    "https://www.britannica.com/biography/Adolf-Hitler",
    "https://www.britannica.com/science/acid",
    "https://www.britannica.com/place/China",
    "https://www.britannica.com/biography/George-Washington",
    "https://www.britannica.com/science/virus",
    "https://www.britannica.com/event/Renaissance",
    "https://www.britannica.com/biography/Benjamin-Franklin",
    "https://www.britannica.com/science/human-genome",
    "https://www.britannica.com/place/Japan",
    "https://www.britannica.com/biography/Elon-Musk",
    "https://www.britannica.com/science/chemistry"
]


def add_urls_to_db(db_conn):
    
    # Create a cursor object to interact with the database
    cursor = db_conn.cursor()
    
    # Insert URLs into the tasks table
    for url in britannica_urls:
        try:
            cursor.execute('''
                INSERT INTO tasks (url) VALUES (?)
            ''', (url,))
        except sqlite3.IntegrityError:
            print(f"URL {url} already exists in the database.")
    
    # Commit changes to the database
    db_conn.commit()

    print("50 Wikipedia URLs have been added to the tasks table.")
    cursor.close()

def _init_db(db_conn):
        cursor = db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                url TEXT NOT NULL
            )
        ''')
        db_conn.commit()
        cursor.close()

db_conn = sqlite3.connect('DataBases/scheduler.db')

_init_db(db_conn)

# Example usage:
# Assuming `db_conn` is your SQLite connection object
# Add URLs to the tasks table
add_urls_to_db(db_conn)

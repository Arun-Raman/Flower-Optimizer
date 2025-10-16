import sqlite3
from datetime import date


# If you are having issues with opening database file, check your current working directory and change the DB_PATH variable accordingly
DB_NAME = "scraped_data.db"
DB_PATH = "Flower-Optimizer/website/databases" + DB_NAME

def table_exists(table_name):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name=?;""",
            (table_name,))
        result = c.fetchone()
        return result is not None


def create_table(table_name):
    """Create the 'search' table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                idx INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                product_name TEXT NOT NULL,
                vendor TEXT NOT NULL,
                price_per_box REAL NOT NULL CHECK(price_per_box >= 0),
                number_per_box INTEGER NOT NULL CHECK(number_per_box > 0),
                delivery_date DATE NOT NULL,
                stems_available INTEGER NOT NULL CHECK(stems_available > 0)
            );""")
        conn.commit()


def add_entry(table_name, category, product_name, vendor, price_per_box,
              number_per_box, delivery_date, stems_available):  # adds entry to table and returns idx

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(f"""
            INSERT INTO {table_name} (
                category, product_name, vendor, price_per_box,
                number_per_box, delivery_date, stems_available
            )
            VALUES (?, ?, ?, ?, ?, ?, ?);""", 
            (category, product_name, vendor, price_per_box,
              number_per_box, delivery_date, stems_available))
        conn.commit()
        
        return c.lastrowid


def get_entry(table_name, idx):  # returns dictionary
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # allows dict-like access
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table_name} WHERE idx = ?;", (idx,))
        row = c.fetchone()
        if row:
            return dict(row)
        else:
            print("Error: entry doesn't exist")
            return None
        

def get_all_entries(table_name):  # returns list of dictionaries
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name}")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def delete_entry(table_name, idx):  # returns true if deleted, false otherwise
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(f"DELETE FROM {table_name} WHERE idx = ?;", (idx,))


def delete_table(table_name):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.commit()


### Example ###
if __name__ == "__main__":
    if(not table_exists("search")):
        print("creating table \"search\"")
        create_table("search")

    entry_id = add_entry(
        table_name="search",
        category="Roses",
        product_name="Red Passion",
        vendor="FlowerCo",
        price_per_box=39.99,
        number_per_box=25,
        delivery_date=str(date.today()),
        stems_available=500
    )

    entry = get_entry("search", entry_id)
    print(entry)

    delete_entry("search", entry_id)
    entry = get_entry("search", entry_id)
    print(entry)

    entry_id = add_entry(
        table_name="search",
        category="Roses",
        product_name="Red Passion",
        vendor="FlowerCo",
        price_per_box=39.99,
        number_per_box=25,
        delivery_date=str(date.today()),
        stems_available=500
    )
    entry_id = add_entry(
        table_name="search",
        category="Dafodils",
        product_name="Orange Julius",
        vendor="FlowerCo",
        price_per_box=39.99,
        number_per_box=25,
        delivery_date=str(date.today()),
        stems_available=500
    )
    print("get_all_entries")
    print(get_all_entries("search"))
    print("=============================")

    delete_table("search")

    print("table_exists? ", table_exists("search"))

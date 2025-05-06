import sqlite3

def init_db():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS product_movements")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS locations")

    cursor.execute('''

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            REAL NOT NULL,
            quantity INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS location (
            location_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS productmovement (
            movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            from_location INTEGER,
            to_location INTEGER,
            product_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            FOREIGN KEY (from_location) REFERENCES location(location_id),
            FOREIGN KEY (to_location) REFERENCES location(location_id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")

import sqlite3

def init_db():
    conn = sqlite3.connect('automate.db')
    c = conn.cursor()

    # Inventory table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER NOT NULL,
        price REAL NOT NULL,
        mileage INTEGER NOT NULL,
        color TEXT NOT NULL,
        status TEXT DEFAULT 'available',
        description TEXT,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Leads table
    c.execute('''CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        interest TEXT,
        budget REAL,
        status TEXT DEFAULT 'new',
        notes TEXT,
        follow_up DATE,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Bookings table
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        car_interest TEXT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('automate.db')
    conn.row_factory = sqlite3.Row
    return conn
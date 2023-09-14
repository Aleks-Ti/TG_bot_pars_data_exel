import sqlite3

con = sqlite3.connect('db.sqlite')

cur = con.cursor()


def create_db():
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER,
        name TEXT
    );
        CREATE TABLE IF NOT EXISTS date_exel(
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        url TEXT,
        xpath TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    ''')


create_db()
con.commit()
con.close()

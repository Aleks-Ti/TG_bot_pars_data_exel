import sqlite3
from database.create_user_profile import user_exists


def added_parse_date(date_telegram_profile):
    '''Добавление пользователя в базу данных.'''
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()

    tg_id = date_telegram_profile['id']

    if user_exists(tg_id, cur):
        cur.execute('''
        INSERT INTO date_exel(user_id, title, url, xpath)
        VALUES (?, ?, ?);
        ''', (tg_id, ))

    con.commit()
    con.close()

import sqlite3

from .create_user_profile import user_exists


async def added_parse_date_db(date_telegram_profile, data_files):
    """Добавление данных загруженного файла xlsx."""
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()

    tg_id = date_telegram_profile['id']

    if await user_exists(tg_id, cur):
        for _, row in data_files.iterrows():
            title = row['title']
            url = row['url']
            xpath = row['xpath']

            cur.execute(
                '''
            INSERT INTO date_exel(user_id, title, url, xpath)
            VALUES (?, ?, ?, ?);
            ''',
                (tg_id, title, url, xpath),
            )

    con.commit()
    con.close()

import sqlite3

from .create_user_profile import user_exists


async def select_date_db(date_telegram_profile):
    """Получения данных url/xpath пользователя."""
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()

    tg_id = date_telegram_profile['from']['id']

    if await user_exists(tg_id, cur):
        cur.execute(
            '''
        SELECT url, xpath
        FROM date_exel
        WHERE user_id == (?)''',
            (tg_id,),
        )
        date = cur.fetchall()
        con.commit()
        con.close()
        return date

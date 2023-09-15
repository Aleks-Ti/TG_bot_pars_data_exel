import sqlite3


async def user_exists(tg_user_id, db_connector):
    """Проверка - существует ли пользователь или нет."""
    db_connector.execute(
        'SELECT id FROM users WHERE telegram_id = ?', (tg_user_id,)
    )
    return db_connector.fetchone()


async def added_user(date_telegram_profile):
    """Добавление пользователя в базу данных."""
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()

    tg_id = date_telegram_profile['id']
    name = date_telegram_profile['first_name']

    if not await user_exists(tg_id, cur):
        cur.execute(
            '''
        INSERT INTO users(telegram_id, name)
        VALUES (?, ?);
        ''',
            (tg_id, name),
        )

    con.commit()
    con.close()

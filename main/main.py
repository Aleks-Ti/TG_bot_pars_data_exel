import io
import logging
import os

import pandas as pd
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentTypes, Message
from dotenv import load_dotenv

from database.create_user_profile import added_user
from database.insert_data_db import added_parse_date_db
from database.return_url_path import select_date_db
from pars_date import price
from settings import COMMANDS_FUNC, PARSE_PRICE, UPLOAD_FILE

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TOKEN')

storage = MemoryStorage()
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=storage)


logging.basicConfig(
    format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=os.path.join(os.path.dirname(__file__), 'program.log'),
    encoding='utf-8',
)


class ByteState(StatesGroup):
    """Машина состояния.

    Ожидание пользовательского ввода.
    """

    name = State()
    cancel = State()


@dp.message_handler(commands=['cancel'], state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """Обработчик команды отмена."""
    current_state = await state.get_state()
    if current_state is not None:
        logging.info('Cancelling state %r', current_state)
        await state.finish()
        await message.answer('Операция отменена.')
    else:
        await message.answer('Нет активных операций для отмены.')


@dp.message_handler(commands=['cmd_upload_file'])
async def cmd_upload_file(message: types.Message):
    """Пользовательский ввод и состояние для конвертации."""
    await ByteState.name.set()
    await message.reply('Загрузите ваш файл!')


@dp.message_handler(commands=['pars_site_price'])
async def pars_site_price(message: types.Message):
    """Получение цен на зюзюблика"""
    data_sampling = await select_date_db(message)
    get_price = await price(data_sampling)
    await message.answer(get_price)


@dp.message_handler(state=ByteState.name, content_types=ContentTypes.DOCUMENT)
async def parse_date(message: Message, state: FSMContext):
    """Получение файла и данных."""
    if document := message.document:
        try:
            file_extension = document.file_name.split('.')[-1].lower()
            if file_extension == 'xlsx':
                file_data = io.BytesIO()
                await document.download(destination_file=file_data)
                file_data.seek(0)
                df = pd.read_excel(file_data)
                await message.reply(df.head().to_string())
                await added_parse_date_db(message['from'], df)
        except Exception as err:
            await logging.error(
                f'Произошла ошибка при обработке файла: {str(err)}'
            )
            await message.reply(
                'Не удалось обработать данные.\n'
                'Убедитесь, что файл c расширением xlsx.\n'
                'Проверьте структуру данных в файле:\n'
                '\t\t - файл должен иметь структуру трех колонок.'
                '\t\t - title, url, xpath\n'
                '\t\t - имя,\tадресс, xpath подготовленный путь до цены'
            )
        await state.finish()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    Вызывается в случаем получения команды `/start`

    methods:
        create_user - создания юзера и занесения в базу данных.
    """

    await added_user(message['from'])

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton(text=UPLOAD_FILE)
    button_2 = types.KeyboardButton(text='/cancel')
    button_3 = types.KeyboardButton(text=PARSE_PRICE)
    keyboard.add(button_1, button_2, button_3)

    await message.reply(
        'Вас приветствует Ваш персональный помощник!\n'
        'Вы можете загрузить файл кликнув -> /cmd_upload_file\n'
        'Для отмены, выберите -> /cancel\n'
        'Или жмите по кнопке внизу 👇\n',
        reply_markup=keyboard,
    )


@dp.message_handler(
    lambda message: message.text in COMMANDS_FUNC, content_types=['text']
)
async def listen_message(message: types.Message):
    """Отлов нажатой кнопки, и подключение функционала."""
    commands = {
        UPLOAD_FILE: cmd_upload_file,
        PARSE_PRICE: pars_site_price,
    }
    selected_command = commands.get(message.text)

    if selected_command:
        await selected_command(message)


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    except BaseException as err:
        logging.info(f'Ошибка: {err}')

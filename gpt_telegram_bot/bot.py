import os
import logging
import openai
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect('../db/database.db', check_same_thread=False)
cursor = conn.cursor()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    if message.text == '/start':
        await message.reply("Привет. С помощью этого бота ты сможешь воспользоваться всеми возможностями chat GPT.")
    else:
        await message.reply("Просто отправь сообщение и chat GPT ответит тебе.")



@dp.message_handler()
async def echo(message: types.Message):
    await message.answer('Обработка запроса...')

    msgs = cursor.execute(f'SELECT message, answer FROM messages WHERE user_id = {message.from_user.id}')
    msgs = cursor.fetchall()

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for msg in msgs:
        messages.extend([{"role": "user", "content": msg[0]}, {"role": "assistant", "content": msg[1]}])
    messages.append({"role": "user", "content": message.text})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    cursor.execute('INSERT INTO messages (user_id, message, answer) VALUES (?, ?, ?)', (message.from_user.id, message.text, response['choices'][0]['message']['content']))
    conn.commit()

    await message.answer(response['choices'][0]['message']['content'])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
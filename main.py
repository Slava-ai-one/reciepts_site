import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramAPIError
import sqlite3
from aiogram.enums import ChatMemberStatus

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

dp = Dispatcher()
BOT_TOKEN = '7966628296:AAG_6x5E_srubv-WwCfsQRoFAVq5OSEUgio'
site = 'Рецепты и точка'


async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def process_start_command(message: types.Message):
    if message.from_user.username:
        user_name = message.from_user.username
    elif message.from_user.first_name:
        user_name = message.from_user.first_name
    else:
        user_name = "Друг"

    await message.reply(
        f"Привет, {user_name}!\nЭтот бот является удобным дополнением к сайту {site}, здесь ты можешь публиковать свои рецепты приготовления еды и просматривать чужие.", reply_markup=kb)


@dp.message(Command('profile'))
async def process_profile_command(message: types.Message):
    await message.reply("Здесь будет статистика личного профиля пользователя")


@dp.message(Command('publish'))
async def process_publish_command(message: types.Message):
    await message.reply("Здесь можно будет опубликовать собственный рецепт")


@dp.message(Command('recipes'))
async def process_recipes_command(message: types.Message):
    await message.reply("Здесь можно будет посмотреть ленту рецептов")


@dp.message(Command('rating'))
async def process_rating_command(message: types.Message):
    await message.reply("Здесь можно будет посмотреть статистику 3 лучших пользователей")


@dp.message()
async def other_message(message: types.Message):
    if message.text == 'Мой профиль':
        asyncio.create_task(process_profile_command(message))
    elif message.text == 'Опубликовать рецепт':
        asyncio.create_task(process_publish_command(message))
    elif message.text == 'Смотреть рецепты':
        asyncio.create_task(process_recipes_command(message))
    elif message.text == 'Рейтинг':
        asyncio.create_task(process_rating_command(message))
    else:
        await message.answer('Пожалуйста, работай с ботом только по кнопкам')


reply_keyboard = [
    [KeyboardButton(text='Мой профиль'), KeyboardButton(text='Опубликовать рецепт')],
    [KeyboardButton(text='Смотреть рецепты'), KeyboardButton(text='Рейтинг')]
]
kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)

if __name__ == '__main__':
    asyncio.run(main())

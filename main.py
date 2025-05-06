import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramAPIError
import sqlite3
from aiogram.enums import ChatMemberStatus

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

dp = Dispatcher()
BOT_TOKEN = '7966628296:AAG_6x5E_srubv-WwCfsQRoFAVq5OSEUgio'
site = 'Рецепты и точка'
channel = '@Recipes_And_Point'
bot = Bot(token=BOT_TOKEN)

conn = sqlite3.connect('botik.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
               (user_id INTEGER PRIMARY KEY, 
                username TEXT)''')
conn.commit()


async def check_subscription(user_id: int):
    try:
        chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except TelegramAPIError:
        return False


def get_subscription_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться на канал", url=f"https://t.me/{channel[1:]}")],
        [InlineKeyboardButton(text="Я подписался ✅", callback_data="check_subscription")]
    ])
    return keyboard


@dp.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery):
    if await check_subscription(callback.from_user.id):
        await callback.message.delete()
        await process_menu_command(callback.message)
    else:
        await callback.answer("Ты ещё не подписан на канал!", show_alert=True)


@dp.message(Command('menu'))
async def process_menu_command(message: types.Message):
    kbm = [
        [KeyboardButton(text='Погрузиться в мир кулинарии')]
    ]
    kbmenu = ReplyKeyboardMarkup(keyboard=kbm, resize_keyboard=True, one_time_keyboard=False)
    await message.answer('Ты подписался, молодец! Теперь можешь продолжить работу с ботом', reply_markup=kbmenu)


@dp.message(Command('start'))
async def process_start_command(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (user_id, message.from_user.username)
        )
        conn.commit()

    if not await check_subscription(user_id):
        await message.answer(
            "📢 Для использования бота необходимо подписаться на наш канал!\n\n"
            "После подписки нажмите кнопку 'Я подписался'",
            reply_markup=get_subscription_keyboard()
        )
        return

    await process_menu_command(message)


async def start_bot(message: types.Message):
    if message.from_user.username:
        user_name = message.from_user.username
    elif message.from_user.first_name:
        user_name = message.from_user.first_name
    else:
        user_name = "Друг"

    await message.reply(
        f"Привет, {user_name}!\nЭтот бот является удобным дополнением к сайту {site}, здесь ты можешь публиковать свои рецепты приготовления еды и просматривать чужие.",
        reply_markup=kb)


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
    elif message.text == 'Погрузиться в мир кулинарии':
        asyncio.create_task(start_bot(message))
    else:
        await message.answer('Пожалуйста, работай с ботом только по кнопкам')


reply_keyboard = [
    [KeyboardButton(text='Мой профиль'), KeyboardButton(text='Опубликовать рецепт')],
    [KeyboardButton(text='Смотреть рецепты'), KeyboardButton(text='Рейтинг')]
]
kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

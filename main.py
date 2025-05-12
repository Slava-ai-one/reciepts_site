import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramAPIError
import sqlite3
from aiogram.enums import ChatMemberStatus
from data.check_on_login_52_42 import Checking_login_im_inspect_you_shell_not_pass
from data import db_recepts_session
from data import users_table_recepts
from data import recept_table
from random import randint

db_recepts_session.global_init("db/blogs.db")
authorized = Checking_login_im_inspect_you_shell_not_pass()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

dp = Dispatcher()
BOT_TOKEN = '7966628296:AAG_6x5E_srubv-WwCfsQRoFAVq5OSEUgio'
site = 'Рецепты и точка'
channel = '@Recipes_And_Point'
bot = Bot(token=BOT_TOKEN)


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
    reply_keyboard = [
        [KeyboardButton(text='Да'), KeyboardButton(text='Нет')]
    ]
    kblogreg = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.reply('Есть ли у вас аккаунт?', reply_markup=kblogreg)
    if message.text == 'Да':
        await message.reply('Введите логин:')
        db_user_name = message.text
        await message.reply('Введите пароль:')
        db_user_password = message.text
        try:
            user = db_recepts_session.create_session().query(users_table_recepts.User()).filter(
                users_table_recepts.User.name == db_user_name).first()
            if (db_user_name) not in db_recepts_session.create_session().query(users_table_recepts.User.name).all():
                await message.reply('Такого пользователя не существует')
            elif not db_recepts_session.create_session().query(users_table_recepts.User).filter(
                    users_table_recepts.User.name == db_user_name).first().check_password(db_user_password):
                await message.reply('Данные пользователя неверны')
            elif db_recepts_session.create_session().query(users_table_recepts.User).filter(
                    users_table_recepts.User.name == db_user_name).first().check_password(db_user_password):
                user = db_recepts_session.create_session().query(users_table_recepts.User).filter(
                    users_table_recepts.User.name == db_user_name).first()
                authorized.logined()
                await message.reply('Авторизация успешно пройдена')
        except Exception:
            await message.reply('Что-то пошло не так')

    elif message.text == 'Нет':
        await message.reply('Введите логин:')
        db_user_name = message.text
        await message.reply('Введите пароль:')
        db_user_password = message.text
        await message.reply('Введите почту:')
        db_user_email = message.text

        user = users_table_recepts.User()
        user.name = db_user_name
        user.email = db_user_email
        user.set_password(db_user_password)
        db_sess = db_recepts_session.create_session()
        db_sess.add(user)
        db_sess.commit()
        authorized.logined()
        await message.reply('Вы успешно зарегистрировались')

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
        user_name = "друг"

    reply_keyboard = [
        [KeyboardButton(text='Мой профиль'), KeyboardButton(text='Опубликовать рецепт')],
        [KeyboardButton(text='Смотреть рецепты'), KeyboardButton(text='Рейтинг')]
    ]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.reply(
        f"Привет, {user_name}!\nЭтот бот является удобным дополнением к сайту {site}, здесь ты можешь публиковать свои рецепты приготовления еды и просматривать чужие.",
        reply_markup=kb)


@dp.message(Command('profile'))
async def process_profile_command(message: types.Message):
    await message.reply("Здесь будет статистика личного профиля пользователя")


@dp.message(Command('publish'))
async def process_publish_command(message: types.Message, db_user_name):
    if authorized.check():
        count = len(db_recepts_session.create_session().query(recept_table.Recepts.id).all()) + 1
        # спросить название описание текст рецепта и фото, кнопки с тегами вида блюда
        # проверка на тип сообщения: фото
        recept = recept_table.Recepts()
        reply_keyboard_tags = [
            [KeyboardButton(text='Суп'), KeyboardButton(text='Десерт')],
            [KeyboardButton(text='Чай'), KeyboardButton(text='Гарнир')]
        ]
        kbtags = ReplyKeyboardMarkup(keyboard=reply_keyboard_tags, resize_keyboard=True, one_time_keyboard=False)
        await message.reply('Введите название рецепта:')
        recept.title = message.text
        await message.reply('Введите описание рецепта:')
        recept.discription = message.text
        await message.reply('Отправьте фотографию рецепта:')
        image = message.text
        recept.way_to_image = f"/static/img/hero_file{count}.png"
        await message.reply('Выберите категорию блюда:', reply_markup=kbtags)
        recept.category_tags = message.text
        while message.text != 'Суп' or message.text != 'Десерт' or message.text != 'Чай' or message.text != 'Гарнир':
            await message.reply('Пожалуйста, выберите категорию блюда из предложенных:', reply_markup=kbtags)
            recept.category_tags = message.text
        await message.reply('Напишите рецепт:')
        text = message.text
        recept.user_id = db_recepts_session.create_session().query(users_table_recepts.User.id).filter(
            users_table_recepts.User.name == db_user_name).first()[0]
        with open(f'static/text_files/text_recept_{count}', mode='w') as f:
            f.write('\n'.join(text.split('\r\n')))
            recept.content = f'static/text_files/text_recept_{count}'

            db_sess = db_recepts_session.create_session()
            db_sess.add(recept)
            db_sess.commit()

        await message.reply("Здесь можно будет опубликовать собственный рецепт")

    @dp.message(Command('recipes'))
    async def process_recipes_command(message: types.Message):
        if len(db_recepts_session.create_session().query(recept_table.Recepts.id).all()) != 0:
            x = randint(1, len(db_recepts_session.create_session().query(recept_table.Recepts.id).all()))
            ans = db_recepts_session.create_session().query(recept_table.Recepts).filter(
                recept_table.Recepts.id == x).first()
            with open(f"{ans.content}", mode='r') as f:
                b = f.readlines()
                ans.content = ''.join(b)
            title = ans.title
            discription = ans.discription
            image = ans.way_to_image
            category_tags = ans.category_tags
            content = ans.content
        else:
            await message.reply("Рецептов пока нет, опубликуйте его первым!")
        await message.reply("Здесь можно будетпосмотреть ленту рецептов")

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

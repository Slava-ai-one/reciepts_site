import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.exceptions import TelegramAPIError
from aiogram.enums import ChatMemberStatus
from data.check_on_login_52_42 import Checking_login_im_inspect_you_shell_not_pass
from data import db_recepts_session
from data import users_table_recepts
from data import recept_table
from random import randint
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

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


class Form(StatesGroup):
    waiting_for_account_confirmation = State()
    waiting_for_login = State()
    waiting_for_password = State()
    waiting_for_email = State()


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
async def process_start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        await message.answer(
            "📢 Для использования бота необходимо подписаться на наш канал!\n\n"
            "После подписки нажмите кнопку 'Я подписался'",
            reply_markup=get_subscription_keyboard()
        )
        return

    reply_keyboard = [[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]]
    kblogreg = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.answer('Есть ли у вас аккаунт?', reply_markup=kblogreg)
    await state.set_state(Form.waiting_for_account_confirmation)


@dp.message(Form.waiting_for_account_confirmation)
async def process_account_confirmation(message: types.Message, state: FSMContext):
    reply_keyboard = [[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]]
    kblogreg = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await state.update_data(account_confirmation=message.text)
    if message.text == 'Да':
        await message.answer('Введите логин:', reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.waiting_for_login)
    elif message.text == 'Нет':
        await message.answer('Введите логин для регистрации:', reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.waiting_for_login)
    else:
        await message.answer('Пожалуйста, выберите да или нет', reply_markup=kblogreg)


@dp.message(Form.waiting_for_login)
async def process_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer('Введите пароль:')
    await state.set_state(Form.waiting_for_password)


@dp.message(Form.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get('account_confirmation') == 'Нет':
        await state.update_data(password=message.text)
        await message.answer('Введите email:')
        await state.set_state(Form.waiting_for_email)
    else:
        db_user_name = user_data['login']
        db_user_password = message.text

        try:
            user = db_recepts_session.create_session().query(users_table_recepts.User).filter(
                users_table_recepts.User.name == db_user_name).first()
            if not user:
                await message.answer('Такого пользователя не существует')
            elif not user.check_password(db_user_password):
                await message.answer('Неверный пароль')
            else:
                authorized.logined(user.id)
                await message.answer('Авторизация успешна!')
                await process_menu_command(message)

        except Exception:
            await message.answer('Ошибка')
        await state.clear()


@dp.message(Form.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user = users_table_recepts.User()
    user.name = user_data['login']
    user.email = message.text
    user.set_password(user_data['password'])

    db_sess = db_recepts_session.create_session()
    db_sess.add(user)
    db_sess.commit()

    authorized.logined(user.id)

    await message.answer('Регистрация успешна!')
    await process_menu_command(message)
    await state.clear()


async def start_bot(message: types.Message):
    if message.from_user.username:
        user_name = message.from_user.username
    elif message.from_user.first_name:
        user_name = message.from_user.first_name
    else:
        user_name = "друг"

    reply_keyboard = [
        [KeyboardButton(text='Смотреть рецепты'), KeyboardButton(text='Опубликовать рецепт')]
    ]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.reply(
        f"Привет, {user_name}!\nЭтот бот является удобным дополнением к сайту {site}, здесь ты можешь публиковать свои рецепты приготовления еды и просматривать чужие.",
        reply_markup=kb)


'''@dp.message(Command('publish'))
async def process_publish_command(message: types.Message):
    try:
        if authorized.check():
            count = len(db_recepts_session.create_session().query(recept_table.Recepts.id).all()) + 1
            # спросить название описание текст рецепта и фото, кнопки с тегами вида блюда
            # проверка на тип сообщения: фото
            recept = recept_table.Recepts()
            reply_keyboard_tags = [
                [KeyboardButton(text='Суп'), KeyboardButton(text='Десерт')],
                [KeyboardButton(text='Напитки'), KeyboardButton(text='Гарнир')]
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
            if message.text != 'Суп' or message.text != 'Десерт' or message.text != 'Напитки' or message.text != 'Гарнир':
                await message.reply('Пожалуйста, выберите категорию блюда из предложенных:', reply_markup=kbtags)
            else:
                recept.category_tags = message.text
            await message.reply('Напишите рецепт:')
            text = message.text
            recept.user_id = authorized.get_id()
            with open(f'static/text_files/text_recept_{count}', mode='w') as f:
                f.write('\n'.join(text.split('\r\n')))
                recept.content = f'static/text_files/text_recept_{count}'
                db_sess = db_recepts_session.create_session()
                db_sess.add(recept)
                db_sess.commit()

            await message.reply("Здесь можно будет опубликовать собственный рецепт")
    except Exception as f:
        print(f)'''


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
        image = FSInputFile(ans.way_to_image)
        category_tags = ans.category_tags
        content = ans.content
        reply_keyboard_next = [
            [KeyboardButton(text='Следующий рецепт')]
        ]
        kbnext = ReplyKeyboardMarkup(keyboard=reply_keyboard_next, resize_keyboard=True, one_time_keyboard=False)
        await message.answer_photo(
            photo=image,
            caption=f"{title}\n\n"
                    f"{discription}\n\n"
                    f"{category_tags}\n\n"
                    f"{content}",
            reply_markup=kbnext
        )
    else:
        await message.reply("Рецептов пока нет, опубликуйте его первым!")


@dp.message()
async def other_message(message: types.Message):
    '''if message.text == 'Опубликовать рецепт':
        asyncio.create_task(process_publish_command(message))'''
    if message.text == 'Смотреть рецепты':
        asyncio.create_task(process_recipes_command(message))
    elif message.text == 'Следующий рецепт':
        asyncio.create_task(process_recipes_command(message))
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

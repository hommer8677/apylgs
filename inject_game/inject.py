import json, random

from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from config import is_valid_path

FILE = "/app/data/injected.json"

inj = Router()
inj.message.filter(F.chat.type.in_({"group", "supergroup"}))
random_num = 0

@inj.message(Command("inject_help"))
async def inject_help(message: types.Message):
    await message.answer("Игра с шприцами - это игра, в которой вы можете заразиться ВИЧ, если вколоте подозрительный шприц.")
    await message.answer("Команды для игры:\n"
                        "/inject - Найти шприц\n"
                        "/cure - Вылечиться\n"
                        "/all_inject - Показать всех зараженных")
@inj.message(Command("inject"))
async def inject(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Вколоть", callback_data="inj"),
                types.InlineKeyboardButton(text="Выкинуть", callback_data="no_inj"))
    await message.answer("Ты нашёл подозрительный шприц. Что ты будешь делать?", reply_markup=builder.as_markup())
@inj.message(Command("cure"))
async def cure(message: types.Message):
    global random_num
    is_valid_path(FILE)
    with open(FILE, encoding='utf-8') as file:
        data = json.load(file)
    if str(message.chat.id) not in data or f"@{message.from_user.username}" not in data[str(message.chat.id)]:
        return await message.answer("Ты не болен!")
    random_num = random.randint(1, 5)
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="1", callback_data="cure_1"))
    builder.row(types.InlineKeyboardButton(text="2", callback_data="cure_2"))
    builder.row(types.InlineKeyboardButton(text="3", callback_data="cure_3"))
    builder.row(types.InlineKeyboardButton(text="4", callback_data="cure_4"))
    builder.row(types.InlineKeyboardButton(text="5", callback_data="cure_5"))
    await message.answer("У тебя появилась уникальная возможность вылечиться!\n"
                        "Для того чтобы снова стать здоровым, тебе нужно отгадать число от 1 до 5:\n", 
                        reply_markup=builder.as_markup())
@inj.callback_query(F.data.startswith("cure_"))
async def process_cure(callback: types.CallbackQuery):
    global random_num
    is_valid_path(FILE)
    with open(FILE, encoding='utf-8') as file:
        data = json.load(file)
    if str(callback.message.chat.id) not in data or f"@{callback.from_user.username}" not in data[str(callback.message.chat.id)]:
        return await callback.answer("Ты не болен!")
    user_choice = int(callback.data.split("_")[1])
    if user_choice == random_num:
        await callback.answer("Поздравляем! Ты вылечился!")
        await callback.message.edit_text("Поздравляем! Ты вылечился!")
        data[str(callback.message.chat.id)].remove(f"@{callback.from_user.username}")
        with open(FILE, "w", encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    else:
        await callback.answer("К сожалению, ты не угадал. Попробуй еще раз.")
        await callback.message.edit_text("К сожалению, ты не угадал. Попробуй еще раз.")
@inj.message(Command("all_inject"))
async def all_inject(message: types.Message):
    is_valid_path(FILE)
    with open(FILE, encoding='utf-8') as file:
        data = json.load(file)
    chat_id = str(message.chat.id)
    if chat_id in data:
        users = ", ".join(data[chat_id])
        if not users: return await message.answer("Никто не заразился.")
        await message.answer(f"Заболевшие в этом чате:\n{users}")
    else:
        await message.answer("Никто не заразился.")
@inj.callback_query(F.data == "inj")
async def process_inj(callback: types.CallbackQuery):
    is_valid_path(FILE)
    result = random.randint(0, 1)
    if result == 1:
        with open(FILE, encoding='utf-8') as file:
            data = json.load(file)
        chat_id = str(callback.message.chat.id)
        username = callback.from_user.username
        await callback.answer("Ты вколол шприц и заразился ВИЧ!")
        await callback.message.edit_text("Ты вколол шприц и заразился ВИЧ!")
        if chat_id not in data:
            data[chat_id] = [f"@{username}"]
        else: 
            if f"@{username}" not in data[chat_id]: 
                data[chat_id].append(f"@{username}")
        with open(FILE, "w", encoding='utf-8') as file:
            json.dump(data, file)
    else:
        await callback.answer("Ты вколол шприц и словил лютейший кайф")
        await callback.message.edit_text("Ты вколол шприц и словил лютейший кайф")
@inj.callback_query(F.data == "no_inj")
async def process_no_inj(callback: types.CallbackQuery):
    await callback.answer() # Просто убираем анимацию загрузки
    await callback.message.answer("Мудрый выбор!")
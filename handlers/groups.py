import json, re, os
from dotenv import load_dotenv

from aiogram import Router, F, types
from aiogram.filters import Command, CommandObject
from config import DATA_FILE, chats, get_banwords, add_group, in_group, gif_add, stick_add, is_valid_path

load_dotenv()
HOMMER_ID=int(os.getenv("HOMMER_ID"))
BANK=str(os.getenv("BANK"))

group_router = Router()
group_router.message.filter(F.chat.type.in_({"group", "supergroup"}))

@group_router.my_chat_member(F.new_chat_member.status.in_({"member", "administrator"}))
async def welcome_and_save(event: types.ChatMemberUpdated):
    chat_id = str(event.chat.id)
    add_group(chat_id)
    await event.bot.send_message(chat_id, "Всем привет! Я в деле.")

@group_router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer("Привет! Я бот для управления банвордами и отслеживания популярности гифок и стикеров в этом чате.\n\n"
                        "Доступные команды:\n"
                        "/add - Добавить запрещённое слово(only admin) ➕\n"
                        "Если хотите добавить несколько слов - напишите их через запятую и оберните в квадратные скобки," 
                        "например: \n<i><b>/add [слово1, слово2, слово3]</b></i>\n"
                        "/del - Удалить запрещённое слово(only admin) 🗑\n"
                        "/del_all - Удалить все запрещённые слова(only admin) 🗑\n"
                        "/banwords - Показать список запрещённых слов ❌\n"
                        "/get_gif - Показать самую популярную гифку в этом чате 🖼️\n"
                        "/get_sticker - Показать самый популярный стикер в этом чате 📎\n"
                        "/get_sticker_pack - Показать самый популярный набор стикеров в этом чате 📦\n"
                        "/money - Поклянчить денег у друга 💵\n" 
                        "Команда должна вводиться по следующему паттерну: \n<i><b>/money @{юзернейм_друга} {сумма}</b></i>\n"
                        "/inject_help - Показать помощь по инъекциям 💉", parse_mode="HTML")
@group_router.message(Command("add"))
async def add_word(message: types.Message):
    is_valid_path()
    if str(message.chat.id) not in chats:
        if not in_group(str(message.chat.id)):
            add_group(str(message.chat.id))
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in ["administrator", "creator"] and message.from_user.id != HOMMER_ID:
        print(member.status)
        return await message.reply("❌ Ты не админ")
    
    words = message.text.replace("/add", "").strip().lower()
    if not words:
        return await message.reply("🖊 Напиши слово после команды")
    if words[0] == '[' and words[-1] == ']':
        clean_text = words[1:-1].replace(",", " ")
        words = clean_text.split()
    else:
        words = words.split()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    chat_id = str(message.chat.id)

    added_words = 0
    for word in words:
        if word not in data[chat_id]["banwords"] and len(word) > 1:
            if word[0] == "@": return message.reply("❌ Ты не можешь добавлять в банлист юзернеймы")
            elif word == "@apylgs_tg_bot":
                return message.reply("Команда /add позволяет добавить запрещённое слово в банлист(only admin) ➕\n"
                                    "Если хотите добавить несколько слов - напишите их через запятую и оберните в квадратные скобки," 
                                    "например: \n<i><b>/add [слово1, слово2, слово3]</b></i>\n", parse_mode="HTML")
            added_words += 1
            data[chat_id]["banwords"].append(word)
            #await message.answer(f"Добавлено слово: {word}")
    with open(DATA_FILE, "w", encoding="utf-8") as f:        
        json.dump(data, f, ensure_ascii=False, indent=4)
    return await message.answer(f"✅ Добавлено новых слов: {added_words}")
@group_router.message(Command("del"))
async def del_word(message: types.Message):
    is_valid_path()
    chat_id = str(message.chat.id)

    if chat_id not in chats:
        if not in_group(chat_id):
            add_group(chat_id)
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        return await message.reply("❌ Ты не админ")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    words = message.text.replace("/del", "").strip().lower()
    if not words:
        return await message.reply("🖊 Напиши слово после команды")
    if words[0] == '[' and words[-1] == ']':
        clean_text = words[1:-1].replace(",", " ")
        words = clean_text.split()
    else:
        words = words.split()

    if len(words) == 1:
        if words[0] == "@apylgs_tg_bot":
            return message.reply("Команда /del позволяет удалить запрещённое слово из банлиста(only admin) 🗑\n
                                "Если вы хотите удалить несколько слов сразу - напишите их через запятую и оберните в квадратные скобки,
                                "например: \n<i><b>/del [слово1, слово2, слово3]</b></i>\n",parse_mode="HTML")
        if words[0] not in data[chat_id]["banwords"]:
            return await message.reply(f"❌ Слова {words[0]} нет в банворде")
        if words[0] in data[chat_id]["banwords"]:
            data[chat_id]["banwords"].remove(words[0])
            with open(DATA_FILE, "w", encoding="utf-8") as f:        
                json.dump(data, f, ensure_ascii=False, indent=4)
            return await message.reply(f"🗑 Слово {words[0]} удалено из банворда")            

    added_words = 0
    for word in words:
        if word in data[chat_id]["banwords"]:
            added_words += 1
            data[chat_id]["banwords"].remove(word)
            #await message.answer(f"Удалено слово: {word}")
    with open(DATA_FILE, "w", encoding="utf-8") as f:        
        json.dump(data, f, ensure_ascii=False, indent=4)
    return await message.answer(f"🗑 Удалено слов: {added_words}")

@group_router.message(Command("del_all"))
async def del_all_words(message: types.Message):
    is_valid_path()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    chat_id = str(message.chat.id)
    if chat_id not in chats:
        if not in_group(chat_id):
            add_group(chat_id)
            chats.add(chat_id)
    data[chat_id]["banwords"].clear()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return await message.reply("🗑 Все слова удалены из банворда")

@group_router.message(Command("banwords"))
async def get_banwords_list(message: types.Message):
    is_valid_path()
    if in_group(str(message.chat.id)):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        chat_id = str(message.chat.id)
        if not data[chat_id]["banwords"]:
            return await message.answer("Список пуст")
        #await message.answer(", ".join(get_banwords(str(message.chat.id))))
        await message.answer(str(get_banwords(str(message.chat.id))))
@group_router.message(F.animation)
async def add_gif_counter(message: types.Message):
    gif_id = message.animation.file_id
    gif_add(str(message.chat.id), gif_id)
@group_router.message(Command("get_gif"))
async def get_gif(message: types.Message):
    is_valid_path()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    gifs = data.get(str(message.chat.id), {}).get("gif", {})
    if gifs:  # Проверка, что словарь не пустой
        max_key = max(gifs, key=gifs.get)
        await message.answer_animation(animation=max_key,
                                       caption="Самая популярная гифка в этом чате")
        await message.answer(f"Она была отправлена {gifs[max_key]} раз(а)")
    else:
        await message.answer("Гифок нету")

@group_router.message(F.sticker)
async def check_sticker(message: types.Message):
    chat_id = str(message.chat.id)
    #Получаем данные о стикере
    sticker_set = message.sticker.set_name # Название набора (пака)
    sticker_id = message.sticker.file_id   # ID конкретного стикера

    stick_add(chat_id, sticker_id, sticker_set)
@group_router.message(Command("get_sticker"))
async def get_sticker(message: types.Message):
    is_valid_path()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    sticks = data.get(str(message.chat.id), {}).get("stickers", {})
    if sticks:  # Проверка, что словарь не пустой
        max_key = max(sticks, key=sticks.get)
        await message.answer(f"Самый популярный стикер в этом чате: ")
        await message.answer_animation(animation=max_key)
        await message.answer(f"Он был отправлен {sticks[max_key]} раз(а)")
    else:
        await message.answer("Стикеров нету")

@group_router.message(Command("get_sticker_pack"))
async def get_sticker_pack(message: types.Message):
    is_valid_path()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    sticker_sets = data.get(str(message.chat.id), {}).get("sticker_sets", {})
    if sticker_sets:  # Проверка, что словарь не пустой
        max_key = max(sticker_sets, key=sticker_sets.get)
        link = f"https://t.me/addstickers/{max_key}"
        await message.answer(f"Самый популярный набор стикеров в этом чате: {link}")
        await message.answer(f"Он был использован {sticker_sets[max_key]} раз(а)")
    else:
        await message.answer("Наборов стикеров нету")

@group_router.message(Command("money"))
async def loan(message: types.Message, command: CommandObject):
    if command.args: args = command.args.split()
    else: 
        if message.from_user.id == HOMMER_ID:
            return await message.answer(f"{BANK} займи пж 100 денег")
    username = ""
    money = 100
    if len(args) == 1:
        is_num = args[0].replace(",", ".").replace(".", "", 1).isdigit()
        if is_num:
            money = args[0]
        else:
            username = args[0]
            money = 100
    elif len(args) == 2:
        first_arg_is_num = args[0].replace(",", ".").replace(".", "", 1).isdigit()
        
        if first_arg_is_num:
            return await message.answer("Введи аргументы по инструкции")
        else:
            username = args[0]
            money = args[1]
    else:
        return await message.answer("Введи аргументы по инструкции")
    if not username.startswith("@"):
        username = "@" + username
    try:
        money = float(money)
    except: return await message.answer("Второй аргумент должен быть числом")
    return await message.answer(f"{username} займи пж {money:g} денег")

@group_router.message(F.text | F.caption)
async def check_banwords(message: types.Message):
    if message.from_user.id == message.bot.id:
        return
    chat_id = str(message.chat.id)
    if chat_id not in chats:
        if not in_group(chat_id):
            add_group(chat_id)
        chats.add(chat_id)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    if chat_id in data and data[chat_id]["banwords"]:
        text = (message.text or message.caption or "").lower()

        for word in data[chat_id]["banwords"]:
            clean_word = word.strip().lower()
            if clean_word:
                if clean_word[0] == "@": return
                if clean_word in text:
                    try:
                        await message.delete()
                        print(f"Удалено: {clean_word} найдено в {text}")
                    except Exception as e:
                        print(f"Ошибка удаления: {e}")
                    break

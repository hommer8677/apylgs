import json, os
from decimal import Decimal

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_FILE = os.path.join(BASE_DIR, "db.json")
#DATA_FILE = "db.json"
DATA_FILE = "/app/data/db.json"
chats = set()

def get_banwords(chat_id):
    with open(DATA_FILE, encoding='utf-8') as file:
        data = json.load(file)
    return data[chat_id]["banwords"]

def in_group(chat_id) -> bool:
    with open(DATA_FILE, encoding='utf-8') as file:
        data = json.load(file)
    return chat_id in data

def load_data():
    # Если файла нет или он пустой, возвращаем пустой словарь
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_group(chat_id):
    chat_id = str(chat_id)
    data = load_data()
    
    if chat_id not in data:
        data[chat_id] = {
            "banwords": [],
            "stickers": {},
            "sticker_sets": {},
            "gif": {} # Сразу добавим и гифки
        }
        save_data(data)
    return data


def gif_add(chat_id, gif_id):
    chat_id = str(chat_id)
    data = add_group(chat_id)
    if "gif" not in data[chat_id]:
        data[chat_id]["gif"] = {}
    current_count = data[chat_id]["gif"].get(gif_id, 0)
    data[chat_id]["gif"][gif_id] = current_count + 1
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def stick_add(chat_id, sticker_id, sticker_set=None):
    chat_id = str(chat_id)
    data = add_group(chat_id)
    if "stickers" not in data[chat_id]:
        data[chat_id]["stickers"] = {}
    if "sticker_sets" not in data[chat_id]:
        data[chat_id]["sticker_sets"] = {}
    data[chat_id]["stickers"][sticker_id] = data[chat_id]["stickers"].get(sticker_id, 0) + 1
    if sticker_set:
        data[chat_id]["sticker_sets"][sticker_set] = data[chat_id]["sticker_sets"].get(sticker_set, 0) + 1
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_valid_path(file=DATA_FILE):
    if not os.path.exists(file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump({}, f) 


def format_decimal(n):
    # normalize() убирает лишние нули в конце
    return format(Decimal(str(n)).normalize(), 'f')
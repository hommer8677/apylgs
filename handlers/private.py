import os
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from dotenv import load_dotenv
    
load_dotenv()
HOMMER_ID=int(os.getenv("HOMMER_ID"))
private_router = Router()
private_router.message.filter(F.chat.type == "private")

@private_router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я групповой бот. Мой функционал пока весьма скуден. Я умею: \n"
                        "   Удалять сообщения с банвордами\n"
                        "   Показывать самый популярный стикер/стикерпак/гифку в чате\n"
                        "   Во мне так же есть подобие русской рулетки\n\n"
                        "Свои идеи по расширению функционала вы можете предложить прямо в этом боте "
                        "написав текстовое сообщение в чат. Ваше сообщение будет переслано владельцу бота\n"
                        "Если вы отправите стикер или гифку, вы узнаете его уникальный id")
@private_router.message(Command("db"))
async def db(message: types.Message):
    if message.from_user.id == HOMMER_ID:
        await message.answer_document(FSInputFile("db.json"))
    else:
        await message.answer("У вас нет доступа к этой команде")

@private_router.message(F.sticker)
async def sticker_info(message: types.Message):
    sticker_id = message.sticker.file_id
    sticker_set = message.sticker.set_name
    sticker_smile = message.sticker.emoji
    url = f"https://t.me/addstickers/{sticker_set}"
    if sticker_set:
        await message.answer(f"ID стикера: <pre>{sticker_id}</pre>\n"
                             f"🖼️ Набор стикеров: {sticker_set}\n"
                             f"😀 Смайлик: {sticker_smile}\n"
                             f"🔗 Ссылка: {url}", parse_mode="HTML")
    else:
        await message.answer(f"ID стикера: <pre>{sticker_id}</pre>\n"
                             f"🖼️ Набор стикеров: {sticker_set}\n"
                             f"😀 Смайлик: {sticker_smile}", parse_mode="HTML")
@private_router.message(F.animation)
async def gif_info(message: types.Message):
    gif_id = message.animation.file_id
    await message.answer(f"ID гифки: <pre>{gif_id}</pre>", parse_mode="HTML")

@private_router.message(F.photo, ~F.caption)
async def get_photo_id(message: types.Message):
    photo = message.photo[-1]
    file_id = photo.file_id
    unique_id = photo.file_unique_id
    file_size = photo.file_size
    width = photo.width 
    height = photo.height
    await message.reply(
            f"🎬 **ID фото:**\n"
            f"`{file_id}`\n\n"
            f"📊 **Информация:**\n"
            f"• Вес: {file_size} байт\n"
            f"• Размер: {width}x{height}\n"
            f"• Unique ID: `{unique_id}`",
            parse_mode="Markdown"
        )

@private_router.message(F.video, ~F.caption)
async def get_video_id(message: types.Message):
    """Получает file_id из отправленного видео"""
    video = message.video
    # Основной file_id видео
    file_id = video.file_id
    # Дополнительная информация
    unique_id = video.file_unique_id  # уникальный ID (меняется при каждом новом файле)
    duration = video.duration  # длительность в секундах
    width = video.width  # ширина
    height = video.height  # высота
    file_size = video.file_size  # размер в байтах
    await message.reply(
        f"🎬 **ID видео:**\n"
        f"`{file_id}`\n\n"
        f"📊 **Информация:**\n"
        f"• Длительность: {duration} сек\n"
        f"• Размер: {width}x{height}\n"
        f"• Вес: {file_size} байт\n"
        f"• Unique ID: `{unique_id}`",
        parse_mode="Markdown"
    )
@private_router.message(F.document, ~F.caption)
async def get_document_id(message: types.Message):
    """Получает file_id из отправленного документа (любого файла)"""
    document = message.document
    # Основной file_id документа
    file_id = document.file_id
    # Дополнительная информация
    unique_id = document.file_unique_id
    file_name = document.file_name  # имя файла
    mime_type = document.mime_type  # тип файла (например, video/mp4, application/pdf)
    file_size = document.file_size  # размер в байтах
    await message.reply(
        f"📄 **ID документа:**\n"
        f"`{file_id}`\n\n"
        f"📊 **Информация:**\n"
        f"• Имя: {file_name}\n"
        f"• Тип: {mime_type}\n"
        f"• Вес: {file_size} байт\n"
        f"• Unique ID: `{unique_id}`",
        parse_mode="Markdown"
    )
@private_router.message(F.voice, ~F.caption)
async def get_voice_id(message: types.Message):
    """Получает file_id из голосового сообщения"""
    voice = message.voice
    # Основной file_id
    file_id = voice.file_id
    # Дополнительная информация
    unique_id = voice.file_unique_id
    duration = voice.duration  # длительность в секундах
    file_size = voice.file_size  # размер в байтах
    mime_type = getattr(voice, 'mime_type', 'audio/ogg')  # обычно audio/ogg для ГС
    # Форматируем длительность в мм:сс
    minutes = duration // 60
    seconds = duration % 60
    duration_str = f"{minutes}:{seconds:02d}"
    await message.reply(
        f"🎤 **ID голосового сообщения:**\n"
        f"`{file_id}`\n\n"
        f"📊 **Информация:**\n"
        f"• Длительность: {duration_str} ({duration} сек)\n"
        f"• Размер: {file_size} байт ({file_size // 1024} KB)\n"
        f"• Тип: {mime_type}\n"
        f"• Unique ID: `{unique_id}`",
        parse_mode="Markdown"
    )
@private_router.message(F.video_note, ~F.caption)
async def detailed_video_note(message: types.Message):
    vn = message.video_note
    
    # Форматируем размер файла
    def format_size(bytes_size):
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        else:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
    
    info = (
        f"📹 **Видеосообщение (кружок)**\n\n"
        f"🆔 `file_id`:\n`{vn.file_id}`\n\n"
        f"🔑 `file_unique_id`:\n`{vn.file_unique_id}`\n\n"
        f"⏱ Длительность: `{vn.duration}` сек\n"
        f"📐 Размер: `{vn.length}`x`{vn.length}` px\n"
        f"📦 Объём: `{format_size(vn.file_size)}`\n"
    )
    
    await message.answer(info, parse_mode='Markdown')

@private_router.message(F.text | F.caption)
async def forward_text(message: types.Message):
    file_id = message.text.strip()
    try:
        # Пробуем получить информацию о файле
        file_info = await message.bot.get_file(file_id)
        # Если получили — значит ID валидный
        file_path = file_info.file_path
        
        if 'photo' in file_path or file_path.startswith('photos/'):
            await message.answer_photo(file_id)
        elif 'animation' in file_path or file_path.startswith('animations/'):
            await message.answer_animation(file_id)
        elif 'sticker' in file_path or file_path.startswith('stickers/'):
            await message.answer_sticker(file_id)
        elif 'video_note' in file_path or file_path.startswith('video_notes/'):
            await message.answer_video_note(file_id)
        elif 'video' in file_path:
            await message.answer_video(file_id)
        elif 'voice' in file_path:
            await message.answer_voice(file_id)
        else:
            await message.answer_document(file_id)
    except:
        try:
            await message.forward(chat_id=HOMMER_ID)
            await message.reply("Сообщение отправлено создателю")
        except Exception as e:
            await message.reply(str(e))

@private_router.message()
async def handle_text(message: types.Message):
    file_id = message.text.strip()
    try:
        # Пробуем получить информацию о файле
        file_info = await message.bot.get_file(file_id)
        
        # Если получили — значит ID валидный
        # Теперь определяем тип по mime_type или пути
        file_path = file_info.file_path
        
        if 'photo' in file_path or file_path.startswith('photos/'):
            await message.answer_photo(file_id)
        elif 'animation' in file_path or file_path.startswith('animations/'):
            await message.answer_animation(file_id)
        elif 'sticker' in file_path or file_path.startswith('stickers/'):
            await message.answer_sticker(file_id)
        elif 'video_note' in file_path or file_path.startswith('video_notes/'):
            await message.answer_video_note(file_id)
        elif 'video' in file_path:
            await message.answer_video(file_id)
        elif 'voice' in file_path:
            await message.answer_voice(file_id)
        else:
            await message.answer_document(file_id)
            
    except Exception as e:
        await message.answer(f"❌ Неверный file_id или файл недоступен\nОшибка: {e}")

import asyncio, logging, os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from aiogram import F, types

from handlers.private import private_router
from handlers.groups import group_router
from inject_game.inject import inj

load_dotenv()
TOKEN=os.getenv("TOKEN")
HOMMER_ID=int(os.getenv("HOMMER_ID"))
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def setup_bot_commands(bot: Bot):
    await bot.set_my_commands(
        commands=[BotCommand(command="start", description="Запуск бота")],
        scope=BotCommandScopeAllPrivateChats()
    )
    await bot.set_my_commands(
        commands=[
            BotCommand(command="help", description="Помощь по командам"),
            BotCommand(command="add", description="Добавить banword"), 
            BotCommand(command="del", description="Удалить banword"),
            BotCommand(command="banwords", description="Показать список запрещенных слов")
        ],
        scope=BotCommandScopeAllGroupChats()
    )

async def main():
    dp.include_routers(inj, private_router, group_router)
    await setup_bot_commands(bot)
    await dp.start_polling(bot)
if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
    except Exception:
        logging.exception("Бот остановлен из-за ошибки")
        raise
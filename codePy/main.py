from telegram_bot.bot_telegram import start_bot
import utils.database as db
import asyncio


def main():
    asyncio.run(start_bot())


if __name__ == '__main__':
    # db.drop_tables()
    db.create_database()
    main()

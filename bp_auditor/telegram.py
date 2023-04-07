import os

from pathlib import Path

import telebot
from telebot.types import InputFile


def send_file_over_telegram(file_path: Path) -> None:
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

    telebot.TeleBot(TOKEN).send_document(
        CHAT_ID,
        InputFile(file_path)
    )


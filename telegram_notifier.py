# telegram_notifier.py
import requests
import re
import html

from dotenv import load_dotenv
import os

# Get tokens and ids from .env file
load_dotenv()  # loads
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Choose parse mode: "MarkdownV2", "HTML", or None
TELEGRAM_PARSE_MODE = "MarkdownV2"

def escape_markdown(text):
    # Escapes special characters for MarkdownV2
    return re.sub(r'([_*\[\]()~`>#+=|{}.!\\-])', r'\\\1', text)

def escape_html(text):
    return html.escape(text)

def clean_message(msg: str) -> str:
    if not msg:
        return "[empty message]"
    
    # Strip whitespace, force to string, and truncate if huge
    msg = str(msg).strip()
    if len(msg) > 4000:  # Telegram limit
        msg = msg[:3990] + "... (truncated)"

    if TELEGRAM_PARSE_MODE == "MarkdownV2":
        return escape_markdown(msg)
    elif TELEGRAM_PARSE_MODE == "HTML":
        return escape_html(msg)
    else:
        return msg

def send_telegram_message(msg: str):
    cleaned = clean_message(msg)
    if not cleaned.strip():
        print("[WARN] Telegram message was empty after cleanup. Skipping.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': cleaned
    }
    if TELEGRAM_PARSE_MODE:
        payload['parse_mode'] = TELEGRAM_PARSE_MODE

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"[ERROR] Telegram API responded with {response.status_code}: {response.text}")
        else:
            print("[✅] Telegram message sent.")
    except Exception as e:
        print(f"[EXCEPTION] Failed to send Telegram message: {e}")
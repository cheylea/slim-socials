# email_watcher.py
import imaplib
import email
from email.header import decode_header
from telegram_notifier import send_telegram_message

from dotenv import load_dotenv
import os

# Get tokens and ids from .env file
load_dotenv()  # loads
EMAIL = os.getenv('EMAIL_USER')
APP_PASSWORD = os.getenv('EMAIL_PASS')

IMAP_SERVER = 'imap.gmail.com'
SEARCH_KEYWORDS = ['Instagram', 'Facebook', 'LinkedIn', 'New message', 'posted in']

def clean_subject(subject):
    decoded = decode_header(subject)
    return ''.join(
        part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
        for part, encoding in decoded
    )

def check_email():
    try:
        print("Checking mail for notifications...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, APP_PASSWORD)
        mail.select("inbox")

        # Search for unseen messages
        status, messages = mail.search(None, '(UNSEEN)')
        if status != 'OK':
            return

        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                continue

            msg = email.message_from_bytes(data[0][1])
            subject = clean_subject(msg['Subject'])

            if any(keyword in subject for keyword in SEARCH_KEYWORDS):
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            charset = part.get_content_charset() or 'utf-8'
                            body = part.get_payload(decode=True).decode(charset, errors='ignore')
                            break
                else:
                    charset = msg.get_content_charset() or 'utf-8'
                    body = msg.get_payload(decode=True).decode(charset, errors='ignore')

                # Send Telegram message
                preview = body.strip().replace('\r', '').replace('\n', ' ')[:200]
                if 'Facebook' in subject or 'Facebook' in body:
                    subject.replace("Facebook", "📘 Facebook")
                elif 'Instagram' in subject or 'Instagram' in body:
                    subject.replace("Instagram", "🎞️ Instagram")
                elif 'LinkedIn' in subject or 'LinkedIn' in body:
                    subject.replace("LinkedIn", "💼 LinkedIn")
                else:
                    subject.replace("New message", "📩 New message")
                send_telegram_message(f"{subject}\n\n{preview}...")
        print("...checking complete")
        mail.logout()

    except Exception as e:
        print(f"[ERROR] {e}")
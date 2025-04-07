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
SEARCH_KEYWORDS = ['Instagram', 'Facebook', 'LinkedIn', 'New message']
SEARCH_SENDERS = ['@linkedin.com', '@facebookmail.com', '@mail.instagram.com']

def clean_subject(subject):
    decoded = decode_header(subject)
    return ''.join(
        part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
        for part, encoding in decoded
    )

def get_text_between_chars(text, start_char, end_char):
    # Find the position of start and end characters
    start_index = text.find(start_char)
    end_index = text.find(end_char, start_index)

    # If both characters are found, return the substring between them
    if start_index != -1 and end_index != -1:
        length = len(start_char)
        return text[start_index + length:end_index]
    return None  # Return None if the characters are not found

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
            sender = msg['From']

            if any(keyword in subject for keyword in SEARCH_KEYWORDS) or any(keyword in sender for keyword in SEARCH_SENDERS):
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
                if 'Facebook' in subject or 'Facebook' in body:
                    print("yup!")
                    subject = subject.replace("Facebook", "📘 Facebook")
                    print(subject)
                elif 'Instagram' in subject or 'Instagram' in body:
                    subject = subject.replace("Instagram", "🎞️ Instagram")
                elif 'LinkedIn' in subject or 'LinkedIn' in body:
                    subject = subject.replace("LinkedIn", "💼 LinkedIn")
                else:
                    subject = subject.replace("New message", "📩 New message")
                
                if 'Facebook' not in subject and 'Facebook' in body:
                    print("yup!")
                    subject = "📘 Facebook: " + subject
                    print(subject)
                elif 'Instagram' not in subject and 'Instagram' in body:
                    subject = "🎞️ Instagram: " + subject
                elif 'LinkedIn' not in subject and 'LinkedIn' in body:
                    subject = "💼 LinkedIn: " + subject
                
                if 'Facebook' in subject:
                    start = 'Hi Cheylea,'
                    end = 'This message was sent to cheyleahopkinson@gmail.com.'
                    preview = get_text_between_chars(body, start, end)
                    print(preview)
                else:
                    preview = body.strip().replace('\r', '').replace('\n', ' ')[:1000]
                send_telegram_message(f"{subject}\n\n{preview}...")
        print("...checking complete")
        mail.logout()

    except Exception as e:
        print(f"[ERROR] {e}")
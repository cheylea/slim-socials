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
SEARCH_KEYWORDS = ['Facebook', 'LinkedIn', 'New message', 'Delivery cancelled', 'Vinted', 'Amazon', 'Only 24 hours to grab your parcel', 'Your parcel is ready to collect']
SEARCH_SENDERS = ['@linkedin.com', '@facebookmail.com', '@vinted.co.uk', 'shipment-tracking@amazon.co.uk', 'order-update@amazon.co.uk', 'jobarnard.writes@gmail.com']

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
            status, data = mail.fetch(num, "(BODY.PEEK[])")
            if status != 'OK':
                continue

            msg = email.message_from_bytes(data[0][1])
            subject = clean_subject(msg['Subject'])
            sender = msg['From']

            if any(keyword in subject for keyword in SEARCH_KEYWORDS) or any(keyword in sender for keyword in SEARCH_SENDERS):
                body = ""
                preview = ""
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
                if 'Facebook' in subject or '@facebookmail.com' in sender:
                    subject = subject.replace("Facebook", "📘 Facebook")
                elif 'LinkedIn' in subject or '@linkedin.com' in sender:
                    subject = subject.replace("LinkedIn", "💼 LinkedIn")
                elif 'Vinted' in subject or '@vinted.co.uk' in sender:
                    subject = subject.replace("Vinted", "👗 Vinted")
                elif 'Amazon' in subject or '@amazon.co.uk' in sender:
                    subject = subject.replace("Amazon", "📦 Amazon")
                
                
                if 'Facebook' not in subject and '@facebookmail.com' in sender:
                    subject = "📘 Facebook: " + subject
                elif 'LinkedIn' not in subject and '@linkedin.com' in sender:
                    subject = "💼 LinkedIn: " + subject
                elif 'Vinted' not in subject and '@vinted.co.uk' in sender:
                    subject = "👗 Vinted: " + subject
                elif 'Amazon' not in subject and '@amazon.co.uk' in sender:
                    subject = "📦 Amazon: " + subject
                elif '@inpost.co.uk' in sender:
                    subject = "🟡 InPost: " + subject
                else:
                    subject = "📩" + subject
                
                if 'Facebook' in subject:
                    start = 'Hi Cheylea,'
                    end = 'This message was sent to cheyleahopkinson@gmail.com.'
                    preview = get_text_between_chars(body, start, end)
                elif 'Vinted' in subject or '@vinted.co.uk' in sender:
                    if 'New offer' in subject:
                        start1 = 'New offer:</p>'
                        start2 = '£'
                        end1 = '</div>'
                        end2 = '<br /><br />'
                        preview = get_text_between_chars(body, start1, end1)
                        preview = '£' + get_text_between_chars(preview, start2, end2)
                    elif 'Order update' or 'New message' in subject:
                        start1 = 'New message:</p>'
                        start2 = '<p>'
                        end = '</p>'
                        preview = get_text_between_chars(body, start1, end)
                        preview = get_text_between_chars(body, start2, end)
                elif 'shipment-tracking@amazon.co.uk' in sender:
                    start = 'Track package'
                    end = 'Quantity:'
                    preview = get_text_between_chars(body, start, end)
                elif 'order-update@amazon.co.uk' in sender:
                    preview = ""
                else:
                    preview = body.strip().replace('\r', '').replace('\n', ' ')[:1000]
                
                send_telegram_message(f"{subject}\n\n{preview}...")

                mail.store(num, '+FLAGS', '\\Seen')
        print("...checking complete")
        mail.logout()

    except Exception as e:
        print(f"[ERROR] {e}")

def count_unread_emails():
    try:
        # Connect to the email server
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))

        # Select the mailbox you want to check
        imap.select("inbox")

        # Search for unread emails
        status, messages = imap.search(None, 'UNSEEN')
        unread_count = len(messages[0].split())

        # Send result to Telegram
        send_telegram_message(f'📬 You have {unread_count} unread emails: <a href="googlegmail://">open gmail</a>', parse_mode="HTML")

        imap.logout()
    except Exception as e:
        send_telegram_message(f"[ERROR] Failed to check unread email count: {str(e)}")

def check_promotions():
    try:
        print("Checking for promotional emails (Gmail category)...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, APP_PASSWORD)
        mail.select("inbox")

        # Gmail's smart category filter
        status, messages = mail.search(None, 'X-GM-RAW "category:promotions is:unread"')
        if status != 'OK':
            return

        for num in messages[0].split():
            status, data = mail.fetch(num, "(BODY.PEEK[])")
            if status != 'OK':
                continue

            msg = email.message_from_bytes(data[0][1])
            subject = clean_subject(msg['Subject'])
            sender = msg['From']

            print(f"[PROMO] Marking as read: {subject} from {sender}")
            mail.store(num, '+FLAGS', '\\Seen')  # ✅ Mark as read

        print("...promo check complete")
        mail.logout()

    except Exception as e:
        print(f"[ERROR] check_promotions failed: {e}")
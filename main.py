# main.py
from discord_watcher import run_discord_bot
from email_watcher import check_email, count_unread_emails, check_promotions
from discord_notifier import send_discord_message
import threading
import time
import schedule

def email_loop():
    while True:
        check_email()
        time.sleep(60)  # Check every 60 seconds

def email_promotion_loop():
    while True:
        check_promotions()
        time.sleep(60)  # Check every 60 seconds

def scheduler_loop():
    schedule.every().day.at("12:30").do(count_unread_emails)

    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    # Start the email checker in a background thread
    threading.Thread(target=email_promotion_loop, daemon=True).start()
    threading.Thread(target=email_loop, daemon=True).start()
    threading.Thread(target=scheduler_loop, daemon=True).start()
    
    # Run the Discord bot (this blocks, so it comes last)
    run_discord_bot()
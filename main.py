# main.py
from discord_watcher import run_discord_bot
from email_watcher import check_email
import threading
import time

def email_loop():
    while True:
        check_email()
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    # Start the email checker in a background thread
    email_thread = threading.Thread(target=email_loop, daemon=True)
    email_thread.start()

    # Run the Discord bot (this blocks, so it comes last)
    run_discord_bot()
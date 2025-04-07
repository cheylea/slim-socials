# slim-socials
Repository for creating a slimmed down version of my social media notifications

# Setting Up
When setting up you will need a few things to make sure the different watchers work.

In your repository create a .env file and fill out the following:

```
EMAIL_USER=youremail@gmail.com
EMAIL_PASS=yourapppassword 
DISCORD_BOT_TOKEN = 'your bot token'
TARGET_CHANNEL_IDS = ['channelid1', 'channelid2', 'channelid3' etc]
TELEGRAM_BOT_TOKEN = '8114419754:AAE0J0W9X7FA19zkCfQDwVKIGsACntwposg'
TELEGRAM_CHAT_ID = 7829996114
```
For the email password, gmail doesn't support using your straight password, so you will need to make sure 2 factor authentication is on and create an app password. Use the Google guidance [here](https://support.google.com/accounts/answer/185833?hl=en).

Make sure the Telegram Chat ID doesn't have '' around it.
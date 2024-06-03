# Leet bot

Bot to measure the first /1337 in a groupchat.

When time is exactly 13:37 people can get points according to who is first and who participates the most.

## Prerequisite

- telegram bot created with botfather https://www.telegram.me/BotFather
- Token for the bot
- add the bot to chat group and find the chatid of those chats. You can use this url with your token https://api.telegram.org/bot<YourBOTToken>/getUpdates

## Installing and running
install requirements:

```
python -m pip install -r requirements.txt

```

Start the bot:
```
python main.py
```

If you don't have a config.conf file available. You will create it on the first run.

# Generating podman image

For podman you can generate a image by running 

```
./build.sh
```
Copy the telegram-leet-bot.container file to .config/containers/systemd/
```
# cat .config/containers/systemd/telegram-leet-bot.container
# systemctl --user daemon-reload
# systemctl --user start telegram-leet-bot



## Developing
You can use the -t argument to test ne configurations and functions. 

```
python main.py -t
```
# tgbot
Easy-to-use Python implementation of the Telegram Bot API.

## Getting started
Make sure you have obtained a bot token from @BotFather.

### Initializing the bot
```python
import tgbot

bot = tgbot.Bot(token = "YOUR_BOT_TOKEN")
```

### Handling the /start command
```python
def handle_start_command(chat, user, message):
    if user == None:
        chat.send_message("Hello channel!")
    else:
        chat.send_message("Hello {0}!".format(user.first_name))

bot.on_message.match("/start", handle_start_command)
```

### Starting the bot
```python
# Make sure to include this line, since tgbot makes use of processes.
if __name__ == "__main__":
    bot.start()
```

## Using webhooks
Using webhooks is easy! Tgbot will set up a HTTPS server for you. Make sure you have OpenSSL installed on your system.

### Initializing a bot using a webhook
```python
bot = tgbot.Bot(token = "YOUR_BOT_TOKEN", use_webhook = True)
```

### Changing the webhook server port
Tgbot uses port `8443` by default, but this can be changed by passing `webhook_port` to `Bot`.
```python
bot = tgbot.Bot(token = "YOUR_BOT_TOKEN", use_webhook = True, webhook_port = 443)
```
Not all ports are supported (Reference: https://core.telegram.org/bots/api#setwebhook).

### Webhooks on Windows
OpenSSL binaries for Windows are available at http://gnuwin32.sourceforge.net/packages/openssl.htm. You can either add the directory in which openssl.exe resides to your PATH environment variable or pass `openssl_command` to `Bot`.
E.g.
```python
bot = tgbot.Bot(token = "YOUR_BOT_TOKEN", use_webhook = True, openssl_command = "A:\\openssl\\bin\\openssl.exe")
```

## Examples

### Uploading a photo
```python
def show_photo(chat):
    chat.send_photo(open("photo.jpg", "rb"), caption = "A photo")
```
Don't close the file object! The message will be sent in another thread. Tgbot will close the file handle. To only upload a photo once (best practice), one could rewrite the `show_photo` function.
```python
import threading
from time import time

mutex = threading.Lock()
file_id = None

def show_photo(chat):
    def print_delta(sent_message):
        print("That message took {0} seconds to send!".format(time() - t))
    with mutex:
        t = time()
        global file_id
        if file_id != None:
            chat.send_photo(file_id, caption = "A photo").then(print_delta)
        else:
            message = chat.send_photo(open("photo.jpg", "rb"), caption = "A photo").then(print_delta).await()
            # message.photo contains a list of PhotoSize objects
            largest_photo = sorted(message.photo, key = lambda photo_size: -photo_size.width * photo_size.height)[0]
            file_id = largest_photo.id
```
The function `print_delta` prints the improved deltas.


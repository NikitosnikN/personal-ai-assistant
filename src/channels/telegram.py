import os
import asyncio
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError


class TelegramChannel:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("CHAT_ID")
        self.bot = Bot(token=self.token)
        self.offset = None

    def send_message(self, text):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
            )
            print(f"TelegramChannel: Sent message to chat_id {self.chat_id}")
            return "Message sent successfully on Telegram"
        except TelegramError as e:
            print(f"TelegramChannel Error sending message: {e}")
            return f"Failed to send message: {str(e)}"

    def receive_messages(self, after_timestamp):
        try:
            loop = asyncio.get_event_loop()
            updates = loop.run_until_complete(self.bot.get_updates(offset=self.offset))
            if updates:
                 print(f"TelegramChannel: Received {len(updates)} updates via get_updates()")
            new_messages = []
            for update in updates:
                if self.offset is None or update.update_id >= self.offset:
                    self.offset = update.update_id + 1

                if isinstance(update, Update) and update.message:
                    message = update.message
                    # print(f"Update ID: {update.update_id}, Message Date: {message.date.timestamp()}, After Timestamp: {after_timestamp}")
                    if message.date.timestamp() > after_timestamp:
                        new_messages.append({
                            "text": message.text,
                            "date": message.date.strftime("%Y-%m-%d %H:%M"),
                        })
            return new_messages
        except TelegramError as e:
            print(f"TelegramChannel Error receiving messages: {e}")
            return f"Failed to retrieve messages: {str(e)}"

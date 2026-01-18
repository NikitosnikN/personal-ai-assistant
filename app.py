import time
import sqlite3
from dotenv import load_dotenv
from src.channels.telegram import TelegramChannel
from src.agents.personal_assistant import PersonalAssistant
import datetime

# Load .env variables
load_dotenv()

# Initialize sqlite3 DB for saving agent memory
conn = sqlite3.connect("db/checkpoints.sqlite", check_same_thread=False)

# Use telegram for communicating with the agent
telegram = TelegramChannel()
# Use Slack for communicating with the agent
# slack = SlackChannel()

# Initiate personal assistant
personal_assistant = PersonalAssistant(conn)

# Configuration for the Langgraph checkpoints, specifying thread ID
config = {"configurable": {"thread_id": "1"}}


def monitor_channel(after_timestamp, config):
    while True:
        new_messages = telegram.receive_messages(after_timestamp)
        if isinstance(new_messages, list) and new_messages:
            print(f"[{datetime.datetime.now()}] Received {len(new_messages)} new messages.")
            for message in new_messages:
                print(f"[{datetime.datetime.now()}] Processing message: {message['text']}")
                sent_message = (
                    f"Message: {message['text']}\n"
                    f"Current Date/time: {message['date']}"
                )
                print(f"[{datetime.datetime.now()}] Invoking Personal Assistant...")
                answer = personal_assistant.invoke(sent_message, config=config)
                print(f"[{datetime.datetime.now()}] Assistant response: {answer}")
                telegram.send_message(answer, chat_id=message.get('chat_id'))
                print(f"[{datetime.datetime.now()}] Response sent to Telegram.")
        elif isinstance(new_messages, str):
            print(f"Telegram error: {new_messages}")

        # after_timestamp = int(time.time()) # Removed to fix missing messages issue. Offset is used instead.
        time.sleep(5)  # Sleep for 5 seconds before checking again
        

if __name__ == "__main__":
    print("Personal Assistant Manager is running")
    telegram.drop_pending_messages()
    monitor_channel(int(time.time()), config)

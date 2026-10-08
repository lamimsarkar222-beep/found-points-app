import os
import telebot
from flask import Flask, request
from supabase import create_client, Client

app = Flask(__name__)

# এগুলো রেন্ডারের Value থেকে রিড করবে
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@app.route('/')
def home():
    return "Running!"

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    supabase.table("users").upsert({"telegram_id": user_id, "username": username}).execute()
    bot.reply_to(message, "স্বাগতম!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

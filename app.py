import os
from flask import Flask, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# Supabase Credentials from Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    return "Bot and Database App is Running!"

@app.route('/test-db')
def test_db():
    try:
        # সুপাবেজে একটি টেস্ট ডাটা পাঠাচ্ছি কানেকশন চেক করার জন্য
        data = {"key": "connection_test", "value": {"status": "success"}}
        response = supabase.table("app_settings").insert(data).execute()
        return "Database Connected Successfully!"
    except Exception as e:
        return f"Database Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

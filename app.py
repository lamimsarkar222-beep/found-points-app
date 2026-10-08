import os
from flask import Flask, render_template_string, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ==========================================
# CONFIGURATION
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://found-points-app.onrender.com")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

BOT_USERNAME = "found_points_bot"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Webhook সেটআপ করা
bot.remove_webhook()
bot.set_webhook(url=f"{WEBAPP_URL}/{BOT_TOKEN}")

# ==========================================
# WEBAPP HTML & JS CONTENT
# ==========================================
HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Found Points</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>

<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Arial,sans-serif;background:#080c12;color:#fff;min-height:100vh;padding-bottom:82px}}
.app{{max-width:480px;margin:auto;padding:16px}}
.page{{display:none}}.page.active{{display:block}}
.header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}}
.logo{{font-size:25px;font-weight:800}}
.logo span{{color:#72a7ff}}
.card{{background:linear-gradient(145deg,#171e27,#10151c);border:1px solid #252e39;border-radius:21px;padding:18px;margin-bottom:14px}}
.balance-label{{color:#8f9baa;font-size:13px}}
.balance{{font-size:35px;font-weight:800;margin:5px 0}}
.fc{{color:#75a9ff;font-size:14px}}
.stats{{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:16px}}
.stat{{background:#111820;border-radius:14px;padding:12px}}
.stat small{{color:#7f8995}}
.stat b{{display:block;margin-top:5px;font-size:16px}}
.btn{{border:0;background:#6e9fff;color:#08101a;font-weight:800;border-radius:11px;padding:10px 13px;cursor:pointer}}
.btn.stop{{background:#45252b;color:#ff9ba5}}
input,select{{width:100%;padding:13px;border-radius:12px;border:1px solid #303b48;background:#0f151c;color:#fff;margin:6px 0 10px;outline:none}}
.nav{{position:fixed;bottom:0;left:0;right:0;height:70px;background:#10151c;border-top:1px solid #252e39;display:flex;justify-content:center;z-index:20}}
.nav-inner{{width:100%;max-width:480px;display:flex;justify-content:space-around;align-items:center}}
.nav button{{background:none;border:0;color:#727d89;font-size:10px;cursor:pointer}}
.nav button.active{{color:#76a9ff}}
</style>
</head>

<body>
<div class="app">

<!-- HOME -->
<section id="home" class="page active">
  <div class="header"><div class="logo">Found <span>Points</span></div></div>
  <div class="card">
    <div class="balance-label">Your Balance</div>
    <div class="balance" id="balance">0</div>
    <div class="fc">FC Points</div>
    <div class="stats">
      <div class="stat"><small>Today's Earned</small><b id="today">0 FC</b></div>
      <div class="stat"><small>Ads Watched</small><b id="ads">0 / 20</b></div>
    </div>
  </div>
  <div class="card">
    <h3>⏱️ Normal Earning</h3>
    <p style="color:#9aa6b3;font-size:13px;margin:8px 0;">Earn 1 FC every 6s. Max 200 FC/day.</p>
    <button id="startBtn" class="btn" onclick="startEarning()">Start Earning</button>
    <button id="stopBtn" class="btn stop" style="display:none" onclick="stopEarning()">Stop</button>
  </div>
</section>

<!-- REFERRAL -->
<section id="referral" class="page">
  <div class="header"><div class="logo">Referral</div></div>
  <div class="card">
    <div class="balance-label">Your Referral Link</div><br>
    <input id="refLink" readonly>
    <button class="btn" style="width:100%" onclick="copyReferral()">Copy Link</button>
  </div>
  <div class="card">
    <small>Total Invites</small>
    <h2 id="refCount">0</h2>
  </div>
</section>

<!-- WITHDRAW -->
<section id="withdraw" class="page">
  <div class="header"><div class="logo">Withdrawal</div></div>
  <div class="card">
    <div class="balance-label">Minimum Withdraw</div>
    <div class="balance">20,000 FC</div>
  </div>
  <select id="method">
    <option value="bKash">bKash</option>
    <option value="Nagad">Nagad</option>
  </select>
  <input id="payment" placeholder="Enter Account Number">
  <button class="btn" style="width:100%" onclick="withdraw()">Submit</button>
</section>

</div>

<div class="nav">
  <div class="nav-inner">
    <button class="active" onclick="showPage('home',this)">Home</button>
    <button onclick="showPage('referral',this)">Referral</button>
    <button onclick="showPage('withdraw',this)">Withdraw</button>
  </div>
</div>

<script>
const SUPABASE_URL = "{SUPABASE_URL}";
const SUPABASE_ANON_KEY = "{SUPABASE_ANON_KEY}";
const BOT_USERNAME = "{BOT_USERNAME}";

const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
const tg = window.Telegram?.WebApp;
if(tg){{ tg.ready(); tg.expand(); }}

let user = {{
  id: tg?.initDataUnsafe?.user ? String(tg.initDataUnsafe.user.id) : "demo_123",
  first_name: tg?.initDataUnsafe?.user?.first_name || "User",
  username: tg?.initDataUnsafe?.user?.username ? "@"+tg.initDataUnsafe.user.username : "@user",
  referred_by: tg?.initDataUnsafe?.start_param ? tg.initDataUnsafe.start_param.replace("ref_", "") : null
}};

let dbData = {{ balance: 0, today: 0, ads: 0, referrals: 0 }};
let timer = null;

async function initApp() {{
  document.getElementById("refLink").value = `https://t.me/${{BOT_USERNAME}}?start=ref_${{user.id}}`;
  
  let {{ data, error }} = await supabase.from('users').select('*').eq('telegram_id', user.id).single();
  
  if (error || !data) {{
    if (user.referred_by && user.referred_by !== user.id) {{
      let {{ data: refUser }} = await supabase.from('users').select('*').eq('telegram_id', user.referred_by).single();
      if (refUser) {{
        await supabase.from('users').update({{ balance: (refUser.balance||0)+100, referrals: (refUser.referrals||0)+1 }}).eq('telegram_id', user.referred_by);
      }}
    }}
    let {{ data: newUser }} = await supabase.from('users').insert([{{
      telegram_id: user.id, first_name: user.first_name, username: user.username, balance: 0, today_earned: 0, ads_watched: 0, referrals: 0
    }}]).select().single();
    if(newUser) dbData = {{ balance: 0, today: 0, ads: 0, referrals: 0 }};
  }} else {{
    dbData = {{ balance: data.balance||0, today: data.today_earned||0, ads: data.ads_watched||0, referrals: data.referrals||0 }};
  }}
  updateUI();
}}

function updateUI() {{
  document.getElementById("balance").textContent = dbData.balance;
  document.getElementById("today").textContent = dbData.today + " FC";
  document.getElementById("refCount").textContent = dbData.referrals;
}}

function showPage(id, btn) {{
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.getElementById(id).classList.add("active");
  document.querySelectorAll(".nav button").forEach(b => b.classList.remove("active"));
  if(btn) btn.classList.add("active");
}}

function startEarning() {{
  document.getElementById("startBtn").style.display = "none";
  document.getElementById("stopBtn").style.display = "inline-block";
  timer = setInterval(async () => {{
    if(dbData.today >= 200){{ stopEarning(); return; }}
    dbData.balance++;
    dbData.today++;
    updateUI();
    await supabase.from('users').update({{ balance: dbData.balance, today_earned: dbData.today }}).eq('telegram_id', user.id);
  }}, 6000);
}}

function stopEarning() {{
  if(timer) clearInterval(timer);
  document.getElementById("startBtn").style.display = "inline-block";
  document.getElementById("stopBtn").style.display = "none";
}}

function copyReferral() {{
  navigator.clipboard.writeText(document.getElementById("refLink").value);
  alert("Referral Link Copied!");
}}

async function withdraw() {{
  const pay = document.getElementById("payment").value;
  if(dbData.balance < 20000) return alert("Minimum 20,000 FC required!");
  if(!pay) return alert("Enter account number!");
  await supabase.from('withdrawals').insert([{{ telegram_id: user.id, amount: dbData.balance, account_info: pay, status: 'Pending' }}]);
  dbData.balance = 0;
  updateUI();
  await supabase.from('users').update({{ balance: 0 }}).eq('telegram_id', user.id);
  alert("Request Submitted!");
}}

window.addEventListener("DOMContentLoaded", initApp);
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CONTENT)

# Telegram Webhook Endpoint
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("Start Earning Now 🚀", web_app=WebAppInfo(url=WEBAPP_URL))
    markup.add(btn)
    bot.send_message(message.chat.id, "🌟 *Welcome to Found Points!*", parse_mode="Markdown", reply_markup=markup)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

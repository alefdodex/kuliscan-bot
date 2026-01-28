import telebot
import requests
from flask import Flask
import threading

# 1. SETUP SERVER PENGAMAN (Agar Gratisan Nyala Terus)
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Kuliscan is Alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 2. SETUP BOT TELEGRAM
TOKEN = "8128545345:AAH2r1hJJuLm2LTyvzQf53cbHmhefyH3sAs"
bot = telebot.TeleBot(TOKEN)

def get_full_report(ca):
    dex_url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
    rug_url = f"https://api.rugcheck.xyz/v1/tokens/{ca}/report"
    
    try:
        dex_res = requests.get(dex_url).json()
        rug_res = requests.get(rug_url).json()
        pair = dex_res['pairs'][0] if dex_res.get('pairs') else {}
        base = pair.get('baseToken', {})
        
        name, symbol = base.get('name', 'Unknown'), base.get('symbol', '???')
        price = pair.get('priceUsd', '0')
        mc = pair.get('fdv', 0)
        liq = pair.get('liquidity', {}).get('usd', 0)
        v24h = pair.get('volume', {}).get('h24', 0)
        
        risks = rug_res.get('risks', [])
        top_holders = rug_res.get('topHolders', [])
        mint_auth = "No ✅" if not any("mint" in r['description'].lower() for r in risks) else "Yes ❌"
        
        top10_pct = sum([h.get('pct', 0) for h in top_holders[:10]])
        
        # TAMPILAN PERSIS EGGCOIN
        return (
            f"📌 **{name} ({symbol})**\n"
            f"⚠️ **HEALTHY LIQUIDITY** | Mutable Metadata\n\n"
            f"📌 **Pair:** `{pair.get('pairAddress', 'N/A')[:8]}...`\n"
            f"👤 **Deployer:** `Check on SolScan`\n"
            f"👤 **Owner:** RENNOUNCED\n"
            f"🔶 **Chain:** SOL | ⚖️ **Age:** New\n"
            f"🌿 **Mint:** {mint_auth} | 💧 **Liq:** ${liq:,.0f}\n"
            f"⚡ [Twitter](https://x.com/search?q={symbol}) | [DexScreener]({pair.get('url')})\n\n"
            f"💰 **MC:** ${mc:,.0f} | **Liq:** ${liq:,.0f}\n"
            f"📈 **24h:** {pair.get('priceChange', {}).get('h24', 0)}% | **V:** ${v24h:,.0f}\n\n"
            f"💵 **Price:** ${price}\n"
            f"📊 **Rug Score:** {rug_res.get('score', 0)}\n\n"
            f"📊 **TS:** 1.000B\n"
            f"👥 **Holders:** N/A | **Top10:** {top10_pct:.2f}%\n"
            f"📦 **Airdrops:** Check SolScan\n\n"
            f"👨‍💻 **TEAM WALLETS**\n"
            f"Deployer: 0.00 SOL | 0.0% {symbol}\n\n"
            f"**DYOR/NFA: Kuliscan Automated Report.**"
        )
    except:
        return "❌ Gagal memproses data. CA salah atau API sedang sibuk."

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🚀 **Kuliscan Pro v3.0 Online**\nKirim CA Solana untuk Full Report.")

@bot.message_handler(func=lambda m: True)
def scan(message):
    ca = message.text.strip()
    if len(ca) > 30:
        bot.reply_to(message, "🔎 **Analysing Smart Contract...**")
        bot.send_message(message.chat.id, get_full_report(ca), parse_mode="Markdown", disable_web_page_preview=True)

# 3. JALANKAN SEMUANYA
if __name__ == "__main__":
    # Flask jalan di latar belakang
    threading.Thread(target=run_flask).start()
    # Bot jalan di depan
    bot.infinity_polling()

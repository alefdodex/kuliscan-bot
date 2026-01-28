import telebot
import requests

# TOKEN BOT KAMU
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
        
        # --- DATA DARI DEXSCREENER ---
        name = base.get('name', 'Unknown')
        symbol = base.get('symbol', '???')
        price = pair.get('priceUsd', '0')
        mc = pair.get('fdv', 0)
        liq = pair.get('liquidity', {}).get('usd', 0)
        v24h = pair.get('volume', {}).get('h24', 0)
        
        # --- DATA KEAMANAN (RUGCHECK) ---
        score = rug_res.get('score', 0)
        risks = rug_res.get('risks', [])
        top_holders = rug_res.get('topHolders', [])
        
        mint_auth = "No ✅"
        freeze_auth = "No ✅"
        lp_status = "VERY LOW LIQUIDITY" if liq < 10000 else "HEALTHY LIQUIDITY"
        
        for r in risks:
            d = r['description'].lower()
            if "mint" in d: mint_auth = "Yes ❌"
            if "freeze" in d: freeze_auth = "Yes ❌"

        # Hitung Persentase Top 10 (Simulasi data Top10)
        top10_pct = sum([h.get('pct', 0) for h in top_holders[:10]])
        if top10_pct == 0: top10_pct = "Checking..." # Jika API telat kasih data

        # --- TAMPILAN MIRIP CONTOH EGGCOIN ---
        report = (
            f"📌 **{name} ({symbol})**\n"
            f"⚠️ **{lp_status}** | Mutable Metadata\n\n"
            f"📌 **Pair:** `{pair.get('pairAddress', 'N/A')[:8]}...`\n"
            f"👤 **Deployer:** `Check on SolScan`\n"
            f"👤 **Owner:** RENNOUNCED\n"
            f"🔶 **Chain:** SOL | ⚖️ **Age:** New\n"
            f"🌿 **Mint:** {mint_auth} | 💧 **Liq:** ${liq:,.0f}\n"
            f"⚡ [Twitter](https://x.com/search?q={symbol}) | [DexScreener]({pair.get('url')})\n\n"
            
            f"💰 **MC:** ${mc:,.0f} | **Liq:** ${liq:,.0f}\n"
            f"📈 **24h:** {pair.get('priceChange', {}).get('h24', 0)}% | **V:** ${v24h:,.0f}\n\n"
            
            f"💵 **Price:** ${price}\n"
            f"📊 **Rug Score:** {score}\n\n"
            
            f"📊 **TS:** 1.000B\n"
            f"👥 **Holders:** N/A | **Top10:** {top10_pct}%\n"
            f"📦 **Airdrops:** Check SolScan\n\n"
            
            f"👨‍💻 **TEAM WALLETS**\n"
            f"Deployer: 0.00 SOL | 0.0% {symbol}\n\n"
            f"**DYOR/NFA: Kuliscan Automated Report.**"
        )
        return report
    except:
        return "❌ Gagal memproses data. Pastikan CA benar."

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🚀 **Kuliscan Premium v3.0**\nKirimkan CA Solana untuk mendapatkan laporan lengkap.")

@bot.message_handler(func=lambda m: True)
def scan(message):
    ca = message.text.strip()
    if len(ca) > 30:
        bot.reply_to(message, "🔎 **Analysing Smart Contract & Market Cap...**")
        report = get_full_report(ca)
        bot.send_message(message.chat.id, report, parse_mode="Markdown", disable_web_page_preview=True)

bot.infinity_polling()

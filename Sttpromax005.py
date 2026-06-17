import logging
import random
import html
import requests
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================= CONFIG =================
BOT_TOKEN = "8056085005:AAGQdlmn1fZp_ps3VuUEXyprlJwEZSaeyoY"
ADMIN_ID = 8263739354
GROQ_API_KEY = "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"

USER_LIST = set()
LUCKY_DRAW_COOLDOWN = {}

# Image URLs
WELCOME_IMAGE = "https://iili.io/CnwXYb9.md.png"
ORDER_CONFIRM_IMAGE = "https://iili.io/Cn6QeBj.md.png"
ORDER_PENDING_IMAGE = "https://iili.io/Cn68MG9.md.png"

PAYMENT_INFO = (
    "<b>💰 Payment Account🔰</b>\n\n"
    "<b>💌 KPay / WavePay</b>\n\n"
    "👤 Daw Aye Nwet\n\n"
    "☎️ <code>09756068378</code> (Tap to copy)\n\n"
    "📌 Note မှာ <b>Tg Acc Name</b> သာရေးပါ\n\n"
    "⚠️ ငွေလွှဲပြီးပါက <i>ပြေစာ</i> ပို့ပေးရန် မမေ့ပါနဲ့။"
)

# ================= PRODUCT CATALOG =================
CATALOG = {
    "TT": {
        "title": "📱 TikTok Boost Services",
        "type": "tiktok",
        "note": "🚫 Video က Public ဖြစ်ရန် လိုအပ်ပါသည်။\n⏳ ပုံမှန်ကြာချိန်: 15min to 24hours\n👑 Moni View ကြာချိန်: 24hours to 72hours",
        "items": {
            "LK":  {"name": "Likes (ပြန်မကျ)",       "emoji": "❤️", "tiers": {300: 1500, 500: 2000, 1000: 3000, 5000: 14000, 10000: 28000}},
            "VWD": {"name": "Views (ပြန်ကျနိုင်)",     "emoji": "🍀", "tiers": {1000: 500, 3000: 1500, 5000: 2500, 10000: 5000, 100000: 49000}},
            "VWN": {"name": "Views (ပြန်မကျ)",        "emoji": "🎵", "tiers": {1000: 1000, 3000: 2500, 5000: 4500, 10000: 9000, 100000: 85000}},
            "MV":  {"name": "Monetization Views",      "emoji": "👑", "tiers": {1000: 1000, 5000: 2500, 10000: 5000}},
            "FL":  {"name": "Followers (အကျနည်း)",    "emoji": "👥", "tiers": {100: 4000, 300: 11000, 500: 19000, 1000: 37000}},
            "FV":  {"name": "Favourites (ပြန်မကျ)",   "emoji": "💗", "tiers": {500: 500, 1000: 1000, 10000: 10000}},
            "SH":  {"name": "Shares (ပြန်မကျ)",       "emoji": "📤", "tiers": {500: 800, 1000: 1500, 10000: 13000}},
            "JP":  {"name": "Japan Region ACC",        "emoji": "🇯🇵", "tiers": {1: 8000}},
            "PM":  {"name": "Tiktok Promote 1$",       "emoji": "📹", "tiers": {1: 8000}},
        }
    },
    "PUBG": {
        "title": "🎮 PUBG UC & PASS",
        "type": "fixed",
        "note": "🔣 <b>ID & IN GAME NAME</b> ပေးရန် လိုအပ်ပါသည်\n⏳ <b>ကြာချိန် - 30 Min</b>",
        "ask_label": "🆔 PUBG <b>ID</b> နှင့် <b>IN GAME NAME</b> ကို ပို့ပေးပါခင်ဗျာ",
        "groups": {
            "UC": {
                "title": "🔥 UC ပက်ကေ့ဂျ်များ",
                "items": {
                    "UC60":   {"name": "🔥 60 UC",   "price": 5000},
                    "UC325":  {"name": "🔥 325 UC",  "price": 24000},
                    "UC660":  {"name": "🔥 660 UC",  "price": 42000},
                    "UC1800": {"name": "🔥 1800 UC", "price": 120000},
                    "UC3850": {"name": "🔥 3850 UC", "price": 220000},
                    "UC8100": {"name": "🔥 8100 UC", "price": 400000},
                }
            },
            "PK": {
                "title": "💰 Special Packs",
                "items": {
                    "MYTHIC":  {"name": "🌟 Mythic Emblem Pack",   "price": 23000},
                    "MATRL":   {"name": "🌟 Material Pack",        "price": 14000},
                    "FIRSTBY": {"name": "💵 First Purchase Pack",  "price": 5500},
                }
            },
            "PP": {
                "title": "🎮 Prime Pass",
                "items": {
                    "PP1":  {"name": "Prime Pass - 1 Month",  "price": 6000},
                    "PP3":  {"name": "Prime Pass - 3 Months", "price": 15000},
                    "PP6":  {"name": "Prime Pass - 6 Months", "price": 27000},
                    "PP12": {"name": "Prime Pass - 1 Year",   "price": 53000},
                }
            },
            "PPP": {
                "title": "🎮 Prime Plus Pass",
                "items": {
                    "PPP1":  {"name": "Prime Plus Pass - 1 Month",  "price": 50000},
                    "PPP3":  {"name": "Prime Plus Pass - 3 Months", "price": 165000},
                    "PPP6":  {"name": "Prime Plus Pass - 6 Months", "price": 312000},
                    "PPP12": {"name": "Prime Plus Pass - 1 Year",   "price": 624000},
                }
            },
        }
    },
    "MLBB": {
        "title": "💎 Mlbb Diamond",
        "type": "fixed",
        "note": "🔣 Game <b>ID</b> နှင့် <b>Server ID</b> ပေးရန် လိုအပ်ပါသည်",
        "ask_label": "🆔 MLBB <b>Game ID (Server ID)</b> ကို ပို့ပေးပါခင်ဗျာ\nဥပမာ - <code>123456789 (1234)</code>",
        "groups": {
            "DM": {
                "title": "💎 Diamond ဈေးများ",
                "items": {
                    "WP":    {"name": "💎 Weekly Pass",  "price": 6500},
                    "D86":   {"name": "💎 86",           "price": 5700},
                    "D172":  {"name": "💎 172",          "price": 12000},
                    "D257":  {"name": "💎 257",          "price": 16500},
                    "D343":  {"name": "💎 343",          "price": 22000},
                    "D429":  {"name": "💎 429",          "price": 28500},
                    "D600":  {"name": "💎 600",          "price": 37500},
                    "D706":  {"name": "💎 706",          "price": 39900},
                    "D878":  {"name": "💎 878",          "price": 48500},
                    "D1050": {"name": "💎 1050",         "price": 59100},
                    "D1135": {"name": "💎 1135",         "price": 65900},
                    "D2195": {"name": "💎 2195",         "price": 128000},
                    "D3688": {"name": "💎 3688",         "price": 189000},
                    "D5532": {"name": "💎 5532",         "price": 296000},
                    "D9288": {"name": "💎 9288",         "price": 479000},
                }
            },
            "DD": {
                "title": "💎💎 Double Diamond ဈေးများ",
                "items": {
                    "DD50":  {"name": "💎 (50+50)",   "price": 3600},
                    "DD150": {"name": "💎 (150+150)", "price": 10500},
                    "DD250": {"name": "💎 (250+250)", "price": 16500},
                    "DD500": {"name": "💎 (500+500)", "price": 33500},
                }
            },
        }
    },
    "APPS": {
        "title": "📱 Apps (CapCut / Canva)",
        "type": "fixed",
        "note": "",
        "ask_label": "📧 လိုအပ်သော <b>Email / Account Info</b> ကို ပို့ပေးပါခင်ဗျာ",
        "items": {
            "CAPCUT1M": {"name": "📱 Capcut Pro - 1 Month (Private)",                "price": 20000},
            "CANVA1Y":  {"name": "📱 Canva Pro (Edu) - 1 Year (Myanmar Font✅ Fast⚡️)", "price": 8000},
        }
    },
    "TG": {
        "title": "⭐ Telegram Premium & Accounts",
        "type": "fixed",
        "note": (
            "🔣 <b>Login</b> ဝယ်ယူပါက Phone Number + Login Code လိုအပ်ပါသည်။\n"
            "🔣 <b>Gift Plan</b> အတွက် Telegram <b>Username</b> သာ လိုအပ်ပါသည်။\n"
            "🔣 <b>Gift Link</b> ကို Link နှိပ်ပြီး အသုံးပြုလို့ရပါသည်။"
        ),
        "ask_label": "👤 လိုအပ်သော <b>Username / Phone Number / Link</b> ကို ပို့ပေးပါခင်ဗျာ",
        "items": {
            "TGP1M":    {"name": "⭐ Telegram Premium 1 Month (Login)", "price": 23000},
            "TGSMS":    {"name": "📩 SMS Fee",                          "price": 10000},
            "TGGIFT3":  {"name": "🎁 Gift Plan - 3 Months (Username)",  "price": 56000},
            "TGGIFT6":  {"name": "🎁 Gift Plan - 6 Months (Username)",  "price": 74500},
            "TGGIFT12": {"name": "🎁 Gift Plan - 12 Months (Username)", "price": 128000},
            "TGLINK3":  {"name": "🎁 Gift Link - 3 Months",             "price": 53000},
            "TGLINK6":  {"name": "🎁 Gift Link - 6 Months",             "price": 70000},
            "TGLINK12": {"name": "🎁 Gift Link - 12 Months",            "price": 130000},
            "TGACC":    {"name": "✨ Telegram Account (1pc)",           "price": 2000},
        }
    },
}

# ===== Derived helper tables for TikTok flow =====
PRICE_TABLE = {item["name"]: item["tiers"] for item in CATALOG["TT"]["items"].values()}
SVC_SHORT = {item["name"]: code for code, item in CATALOG["TT"]["items"].items()}
SVC_LONG = {code: item["name"] for code, item in CATALOG["TT"]["items"].items()}

TIKTOK_TIPS = [
    "💡 <b>TikTok Tip:</b> ဗီဒီယိုတင်ရင် Hook (ပထမဆုံး ၃ စက္ကန့်) ကို စိတ်ဝင်စားဖို့ကောင်းအောင် ဆွဲဆောင်ပါ။",
    "💡 <b>TikTok Tip:</b> Trending Audio တွေကို နောက်ခံညှပ်သုံးပေးရင် Views တက်ဖို့ အခွင့်အလမ်း ပိုများပါတယ်။",
    "💡 <b>TikTok Tip:</b> Hashtag ၃ ခု ကနေ ၅ ခုလောက်ပဲ သုံးတာက TikTok Algorithm ကို ပိုကူညီပေးပါတယ်။",
    "💡 <b>TikTok Tip:</b> ညနေ ၆ နာရီမှ ၉ နာရီအတွင်း မှန်မှန်တင်ပေးခြင်းက ပရိသတ်အသစ်တွေဆီ ရောက်ရှိဖို့ အကောင်းဆုံးပါပဲ။"
]

# ================= AI ASSISTANT (Groq API) =================
def ask_ai(user_text, conversation_history=None):
    """Call AI via Groq with conversation history support."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    system_prompt = (
        "သင်သည် Knox All-in-One Shop ၏ ဖော်ရွေပြီး စမတ်ကျသော AI Assistant ဖြစ်သည်။ "
        "ဆိုင်တွင် TikTok Boost Services, PUBG UC & PASS, MLBB Diamond, CapCut Pro, Canva Pro, "
        "Telegram Premium/Account တို့ကို ရောင်းချသည်။ "
        "Customer က ဘာပဲမေးမေး မြန်မာလို ယဉ်ကျေးပျူငှာစွာ တိုတိုနှင့် လိုရင်း ပြန်ဖြေပါ။ "
        "TikTok ဝန်ဆောင်မှုများ၏ ဈေးနှုန်း:\n"
        "❤️ Likes: 300=1,500ks | 500=2,000ks | 1,000=3,000ks | 5,000=14,000ks | 10,000=28,000ks\n"
        "🍀 Views(ပြန်ကျနိုင်): 1k=500ks | 3k=1,500ks | 5k=2,500ks | 10k=5,000ks | 100k=49,000ks\n"
        "🎵 Views(ပြန်မကျ): 1k=1,000ks | 3k=2,500ks | 5k=4,500ks | 10k=9,000ks | 100k=85,000ks\n"
        "👑 Monetization Views: 1k=1,000ks | 5k=2,500ks | 10k=5,000ks\n"
        "👥 Followers: 100=4,000ks | 300=11,000ks | 500=19,000ks | 1,000=37,000ks\n"
        "💗 Favourites: 500=500ks | 1k=1,000ks | 10k=10,000ks\n"
        "📤 Shares: 500=800ks | 1k=1,500ks | 10k=13,000ks\n"
        "ဝန်ဆောင်မှုဝယ်ယူလိုပါက /start ကိုနှိပ်ပြီး ဝယ်ယူနိုင်ကြောင်း လမ်းညွှန်ပေးပါ။ "
        "TikTok Services တစ်ခုထက်ပိုပြီး တစ်ချိန်တည်းဝယ်ယူနိုင်ကြောင်းလည်း အသိပေးပါ။"
    )

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.7
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        data = response.json()
        logging.info(f"Groq response: {data}")
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            logging.error(f"Groq unexpected response: {data}")
            return fallback_reply()
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return fallback_reply()

def fallback_reply():
    return (
        "👋 ဟယ်လိုခင်ဗျာ! 𝗞𝗻𝗼𝘅 𝗗𝗶𝗴𝗶𝘁𝗮𝗹 𝗦𝘁𝗼𝗿𝗲 မှ ကြိုဆိုပါတယ်။ "
        "ဝန်ဆောင်မှုများ ဝယ်ယူရန် /start ကို နှိပ်ပြီး Menu ခလုတ်များမှတစ်ဆင့် ရွေးချယ်ပေးပါခင်ဗျာ။"
    )

# ================= MENU BUILDERS =================
def build_main_buy_menu():
    kb = []
    for code, cat in CATALOG.items():
        kb.append([InlineKeyboardButton(cat["title"], callback_data=f"cat_{code}")])
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="start")])
    return InlineKeyboardMarkup(kb)

def build_tt_service_menu():
    """TikTok multi-select service menu with checkboxes."""
    kb, row = [], []
    for code, item in CATALOG["TT"]["items"].items():
        if code not in ["JP", "PM"]:
            row.append(InlineKeyboardButton(
                f"{item['emoji']} {item['name']}",
                callback_data=f"ttsel_{code}"
            ))
            if len(row) == 2:
                kb.append(row)
                row = []
    if row:
        kb.append(row)
    # JP and PM as fixed items
    kb.append([
        InlineKeyboardButton("🇯🇵 Japan Region ACC - 8,000ks", callback_data="svc_JP"),
        InlineKeyboardButton("📹 Tiktok Promote 1$ - 8,000ks", callback_data="svc_PM"),
    ])
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="buy")])
    return InlineKeyboardMarkup(kb)

def build_tt_multiselect_menu(selected_items: dict):
    """
    Build multi-select TikTok menu.
    selected_items = {svc_code: qty, ...}
    """
    kb = []
    total = 0
    for code, item in CATALOG["TT"]["items"].items():
        if code in ["JP", "PM"]:
            continue
        emoji = item["emoji"]
        name = item["name"]
        if code in selected_items:
            qty = selected_items[code]
            price = item["tiers"].get(qty, 0)
            total += price
            label = f"✅ {emoji} {name} x{qty} ({price:,}ks)"
        else:
            label = f"➕ {emoji} {name}"
        row = [InlineKeyboardButton(label, callback_data=f"ttsel_{code}")]
        kb.append(row)

    # Total display row (non-clickable via summary text)
    if selected_items:
        kb.append([InlineKeyboardButton(
            f"🛒 ရွေးထားသည်: {len(selected_items)} မျိုး | စုစုပေါင်း: {total:,} ks",
            callback_data="tt_summary"
        )])
        kb.append([InlineKeyboardButton("✅ အတည်ပြုပြီး ဆက်လက်မည်", callback_data="tt_confirm_multi")])
        kb.append([InlineKeyboardButton("🗑️ အားလုံးပစ်မည်", callback_data="tt_clear")])
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="buy")])
    return InlineKeyboardMarkup(kb), total

def build_tt_qty_menu(svc_code: str, selected_items: dict):
    """Show quantity buttons for a specific TikTok service."""
    item = CATALOG["TT"]["items"][svc_code]
    kb = []
    row = []
    for qty, price in item["tiers"].items():
        qty_str = f"{qty//1000}k" if qty >= 1000 else str(qty)
        currently_selected = selected_items.get(svc_code) == qty
        tick = "✅ " if currently_selected else ""
        label = f"{tick}{qty_str} = {price:,}ks"
        row.append(InlineKeyboardButton(label, callback_data=f"ttqty_{svc_code}_{qty}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    # Remove if already selected
    if svc_code in selected_items:
        kb.append([InlineKeyboardButton("❌ ဤ Service ဖယ်ရှားမည်", callback_data=f"ttremove_{svc_code}")])
    kb.append([InlineKeyboardButton("🔙 Service list သို့ပြန်", callback_data="tt_back_multi")])
    return InlineKeyboardMarkup(kb)

def build_group_menu(cat_code):
    cat = CATALOG[cat_code]
    kb = []
    for grp_code, grp in cat["groups"].items():
        kb.append([InlineKeyboardButton(grp["title"], callback_data=f"grp_{cat_code}_{grp_code}")])
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="buy")])
    return InlineKeyboardMarkup(kb)

def build_item_buttons_rows(cat_code, grp_code, items):
    kb, row = [], []
    for code, item in items.items():
        label = f"{item['name']} - {item['price']:,}ks"
        row.append(InlineKeyboardButton(label, callback_data=f"item_{cat_code}_{grp_code}_{code}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    return kb

def get_item(cat_code, grp_code, item_code):
    cat = CATALOG[cat_code]
    if grp_code != "-" and "groups" in cat:
        return cat["groups"][grp_code]["items"][item_code]
    return cat["items"][item_code]

def build_price_text(cat_code):
    cat = CATALOG[cat_code]
    text = f"📋 <b>{cat['title']} ဈေးနှုန်းများ</b>\n\n"
    if cat_code == "TT":
        for code, item in cat["items"].items():
            text += f"💠 <b>{item['emoji']} {item['name']}</b>:\n"
            for qty, price in item["tiers"].items():
                if code in ["JP", "PM"]:
                    text += f"   🔹 Price = {price:,} ks\n"
                else:
                    qty_str = f"{qty//1000}k" if qty >= 10000 else str(qty)
                    text += f"   🔹 {qty_str} = {price:,} ks\n"
            text += "\n"
    elif "groups" in cat:
        for grp in cat["groups"].values():
            text += f"<b>{grp['title']}</b>\n"
            for item in grp["items"].values():
                text += f"  🔸 {item['name']} ➡️ {item['price']:,}ks\n"
            text += "\n"
    else:
        for item in cat["items"].values():
            text += f"🔸 {item['name']} ➡️ {item['price']:,}ks\n"
    if cat.get("note"):
        text += f"\n{cat['note']}\n"
    return text.strip()

def build_multiselect_summary(selected_items: dict) -> str:
    """Build a human-readable summary of selected TikTok items."""
    lines = ["🛒 <b>ရွေးချယ်ထားသော Services များ</b>\n"]
    total = 0
    for svc_code, qty in selected_items.items():
        item = CATALOG["TT"]["items"][svc_code]
        price = item["tiers"].get(qty, 0)
        total += price
        qty_str = f"{qty//1000}k" if qty >= 1000 else str(qty)
        lines.append(f"  {item['emoji']} {item['name']} x{qty_str} = <b>{price:,} ks</b>")
    lines.append(f"\n💰 <b>စုစုပေါင်း: {total:,} ks</b>")
    return "\n".join(lines)

# ================= START MENU =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user_id = update.effective_user.id
    USER_LIST.add(user_id)

    keyboard = [
        [InlineKeyboardButton("🛍️ ဝယ်ယူရန်", callback_data="buy"), InlineKeyboardButton("📊 ဈေးနှုန်းကြည့်ရန်", callback_data="price")],
        [InlineKeyboardButton("❓ FAQ (အမေး/အဖြေ)", callback_data="faq"), InlineKeyboardButton("🎁 ကံစမ်းမယ်", callback_data="lucky_menu")],
        [InlineKeyboardButton("💡 TikTok တင်နည်း Tips", callback_data="tiktok_tips")],
        [InlineKeyboardButton("🤖 AI Assistant နှင့် မေးမြန်းရန်", callback_data="ai_chat")],
        [InlineKeyboardButton("👨‍💻 Adminကို ဆက်သွယ်ရန်", url="https://t.me/just_knox")]
    ]
    welcome_text = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ <b>𝗞𝗻𝗼𝘅 𝗗𝗶𝗴𝗶𝘁𝗮𝗹 𝗦𝘁𝗼𝗿𝗲</b> မှ ကြိုဆိုပါတယ်! ✨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔒 <i>အကောင့်ပေးဝင်စရာမလို / 100% Safe</i>\n\n"
        "👑 <b>ဝယ်ယူနိုင်သော Products များ</b>\n"
        "┌────────────────────\n"
        "│ 📱 TikTok Boost Services (ပြန်မကျ)\n"
        "│ 🎮 PUBG UC & PASS\n"
        "│ 💎 Mlbb Diamond\n"
        "│ 🫟 Capcut Pro / Canva Pro\n"
        "│ ⭐ Telegram Premium & Account\n"
        "└────────────────────\n"
        "🔰 <b>Join Channel:</b> https://t.me/knox_zone\n"
        "✍️ <b>Review ပေးရန်:</b> <code>/review စာသားရိုက်မယ်</code>\n"
        "❓ <b>အသုံးပြုနည်း:</b> /help\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👾 <i>အောက်ပါ Menu ကိုနှိပ်ပြီး အသုံးပြုနိုင်ပါပြီ</i>\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )

    if update.callback_query:
        await update.callback_query.message.reply_photo(
            photo=WELCOME_IMAGE, caption=welcome_text,
            parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_photo(
            photo=WELCOME_IMAGE, caption=welcome_text,
            parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ================= /help COMMAND - TUTORIAL =================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tutorial_text = (
        "📖 <b>𝗞𝗻𝗼𝘅 𝗗𝗶𝗴𝗶𝘁𝗮𝗹 𝗦𝘁𝗼𝗿𝗲 - အသုံးပြုနည်း Tutorial</b>\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 <b>Bot Commands များ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "/start — Bot ကို စတင်ဖွင့်ရန် / Home Menu သို့ပြန်ရန်\n"
        "/help — ဤ Tutorial ကြည့်ရန်\n"
        "/review [စာသား] — ကျေနပ်မှု Review ပေးရန်\n"
        "   ဥပမာ: <code>/review Bot လေး အရမ်းကောင်းတယ်!</code>\n"
        "/bc [စာ] — (Admin သာ) User အားလုံးဆီ Broadcast ပို့ရန်\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "📱 <b>TikTok Services ဝယ်နည်း (Multi-Select)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "① /start နှိပ်ပါ → <b>ဝယ်ယူရန်</b> နှိပ်ပါ\n"
        "② <b>📱 TikTok Boost Services</b> ရွေးပါ\n"
        "③ ချင်သော Service ကို နှိပ်ပါ (ဥပမာ: ❤️ Likes)\n"
        "④ အရေအတွက် ရွေးပါ (ဥပမာ: 500)\n"
        "⑤ နောက်ထပ် Service တစ်ခုပါ ထပ်ရွေးနိုင်သည်\n"
        "   ဥပမာ: 🍀 Views 1000 ကိုပါ ထပ်ရွေး\n"
        "⑥ ဈေးပေါင်း Auto Calculate ဖြစ်ပြီး မြင်ရသည်\n"
        "   <i>Like 500 (2,000ks) + View 1,000 (500ks) = 2,500ks</i>\n"
        "⑦ <b>✅ အတည်ပြုပြီး ဆက်လက်မည်</b> နှိပ်ပါ\n"
        "⑧ TikTok Video/Profile Link ပို့ပါ\n"
        "⑨ ငွေလွှဲပြေစာ ဓာတ်ပုံ ပို့ပါ → Order ပြီးပါပြီ!\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎮 <b>PUBG / 💎 MLBB / 📱 Apps / ⭐ Telegram ဝယ်နည်း</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "① /start → <b>ဝယ်ယူရန်</b> → Category ရွေးပါ\n"
        "② လိုချင်သော Item ကို နှိပ်ပါ\n"
        "③ ID / Email / Username ပေးပါ\n"
        "④ ငွေလွှဲပြေစာ ဓာတ်ပုံ ပို့ပါ → Order ပြီးပါပြီ!\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 <b>AI Assistant အသုံးပြုနည်း</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "• Bot ကို မည်သည့်အရာမဆို တိုက်ရိုက် ရိုက်မေးနိုင်သည်\n"
        "• ဈေးနှုန်းမေးခြင်း, Services ရှင်းပြပေးခြင်း ပြုလုပ်သည်\n"
        "• ဥပမာ: <code>Likes 500 ဈေး ဘယ်လောက်လဲ?</code>\n"
        "• ဥပမာ: <code>Views ဝယ်ချင်တယ် ဘယ်လိုဝယ်ရမလဲ?</code>\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>ငွေပေးချေနည်း</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "• KPay / WavePay ဖြင့် ပေးချေပါ\n"
        "• ဖုန်းနံပါတ်: <code>09756068378</code>\n"
        "• Note တွင် Telegram Name ရေးပါ\n"
        "• ပြေစာ ဓာတ်ပုံ Bot ဆီ ပို့ပေးပါ\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ <b>ကြာချိန်</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "• TikTok Boost: 15 မိနစ် - ၂၄ နာရီ\n"
        "• Monetization Views: ၂၄ - ၇၂ နာရီ\n"
        "• PUBG / MLBB: ၃၀ မိနစ်\n\n"

        "🎁 <b>Lucky Draw</b> - ၂ ရက်တစ်ကြိမ် ကံစမ်းနိုင်သည်!\n"
        "👨‍💻 <b>Admin</b>: @just_knox\n"
        "📢 <b>Channel</b>: @knox_zone"
    )
    kb = [[InlineKeyboardButton("🏠 Home သို့ပြန်", callback_data="start")]]
    await update.message.reply_text(tutorial_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

# ================= SPECIAL COMMANDS =================
async def review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text(
            "❌ စာသားထည့်ရန် လိုအပ်ပါသည်။ ပုံစံ: <code>/review Bot လေး အရမ်းမိုက်တယ်ဗျာ</code>",
            parse_mode="HTML"
        )
        return
    review_text = " ".join(context.args)
    admin_msg = (
        f"⭐️ <b>Review အသစ် ရောက်ရှိလာပါပြီ</b> ⭐️\n\n"
        f"👤 <b>ပေးသူ:</b> {html.escape(user.full_name)} (ID: <code>{user.id}</code>)\n"
        f"✍️ <b>Review:</b> {html.escape(review_text)}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="HTML")
    await update.message.reply_text("💖 Review ပေးပေးတဲ့အတွက် ကျေးဇူးအများကြီးတင်ပါတယ်ခင်ဗျာ! Admin ထံ ပေးပို့လိုက်ပါပြီ။")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ သင်သည် Admin မဟုတ်သဖြင့် ဤ Command ကို သုံးခွင့်မရှိပါ။")
        return
    if not context.args:
        await update.message.reply_text(
            "❌ စာသားထည့်ရန် လိုအပ်ပါသည်။ ပုံစံ: <code>/bc စာသားရိုက်ရန်</code>",
            parse_mode="HTML"
        )
        return
    bc_msg = " ".join(context.args)
    count = 0
    await update.message.reply_text(f"📢 User {len(USER_LIST)} ယောက်ဆီ စာလှမ်းပို့နေပါပြီ...")
    for uid in list(USER_LIST):
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 <b>[Knox Zone Announcement]</b>\n\n{bc_msg}",
                parse_mode="HTML"
            )
            count += 1
        except Exception:
            continue
    await update.message.reply_text(f"✅ User {count} ယောက်ဆီ စာသား အောင်မြင်စွာ ပို့ပြီးပါပြီ။")

# ================= BUTTON HANDLER =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    USER_LIST.add(user_id)

    # ---------- HOME ----------
    if q.data == "start":
        await start(update, context)

    # ---------- AI CHAT INFO ----------
    elif q.data == "ai_chat":
        await q.message.reply_text(
            "🤖 <b>AI Assistant</b>\n\n"
            "ဤ Chat ထဲတွင် မည်သည့်အရာမဆို တိုက်ရိုက် ရိုက်မေးနိုင်ပါသည်!\n\n"
            "ဥပမာ:\n"
            "• <code>Likes 500 ဈေး ဘယ်လောက်လဲ?</code>\n"
            "• <code>TikTok Views ဘာကြောင့် ဝယ်ရတာ အသုံးဝင်လဲ?</code>\n"
            "• <code>MLBB Diamond ဘယ်လို ဝယ်ရမလဲ?</code>\n\n"
            "💬 ဘာပဲ ရိုက်ပါ - AI ဖြေပါမည်!",
            parse_mode="HTML"
        )

    # ---------- TOP LEVEL CATEGORY LIST ----------
    elif q.data == "buy":
        await q.message.edit_caption(
            caption="🛍️ <b>ဝယ်ယူလိုသော Category ကို ရွေးချယ်ပါ</b>",
            parse_mode="HTML",
            reply_markup=build_main_buy_menu()
        )

    # ---------- CATEGORY SELECTED ----------
    elif q.data.startswith("cat_"):
        cat_code = q.data.replace("cat_", "")
        cat = CATALOG[cat_code]

        if cat_code == "TT":
            # Initialize multi-select storage
            if "tt_selected" not in context.user_data:
                context.user_data["tt_selected"] = {}
            selected = context.user_data.get("tt_selected", {})
            markup, total = build_tt_multiselect_menu(selected)
            caption = (
                "📱 <b>TikTok Boost Services</b>\n\n"
                "✨ <b>Multi-Select Feature!</b> - Service များကို တစ်ချိန်တည်းမှာ အများကြီး ရွေးနိုင်ပါတယ်!\n\n"
                "📌 Service တစ်ခု နှိပ်ပြီး အရေအတွက် ရွေးပါ\n"
                "📌 ဈေးကို Auto တွက်ပေးပါမည်\n\n"
                f"{cat.get('note', '')}"
            )
            await q.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=markup)

        elif "groups" in cat:
            caption = f"📦 <b>{cat['title']}</b>\n\n"
            if cat.get("note"):
                caption += f"{cat['note']}\n\n"
            caption += "👇 အမျိုးအစား ရွေးချယ်ပါ"
            await q.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=build_group_menu(cat_code))
        else:
            kb = build_item_buttons_rows(cat_code, "-", cat["items"])
            kb.append([InlineKeyboardButton("🔙 Back", callback_data="buy")])
            caption = f"📦 <b>{cat['title']}</b>\n\n"
            if cat.get("note"):
                caption += f"{cat['note']}\n\n"
            caption += "👇 ပစ္စည်း ရွေးချယ်ပါ"
            await q.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

    # ---------- GROUP (SUB-CATEGORY) SELECTED ----------
    elif q.data.startswith("grp_"):
        _, cat_code, grp_code = q.data.split("_")
        cat = CATALOG[cat_code]
        grp = cat["groups"][grp_code]
        kb = build_item_buttons_rows(cat_code, grp_code, grp["items"])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data=f"cat_{cat_code}")])
        caption = f"📦 <b>{grp['title']}</b>\n\n"
        if cat.get("note"):
            caption += f"{cat['note']}\n\n"
        caption += "👇 ပစ္စည်း ရွေးချယ်ပါ"
        await q.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

    # ---------- TIKTOK MULTI-SELECT: Service နှိပ်ရင် Qty Menu ပြ ----------
    elif q.data.startswith("ttsel_"):
        svc_code = q.data.replace("ttsel_", "")
        if "tt_selected" not in context.user_data:
            context.user_data["tt_selected"] = {}
        selected = context.user_data["tt_selected"]
        item = CATALOG["TT"]["items"][svc_code]
        markup = build_tt_qty_menu(svc_code, selected)
        caption = (
            f"🔢 <b>{item['emoji']} {item['name']}</b> - အရေအတွက် ရွေးပါ\n\n"
        )
        # Show current selections
        if selected:
            caption += build_multiselect_summary(selected) + "\n\n"
        for qty, price in item["tiers"].items():
            qty_str = f"{qty//1000}k" if qty >= 1000 else str(qty)
            caption += f"🔸 {qty_str} = {price:,} ks\n"
        await q.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=markup)

    # ---------- TIKTOK MULTI-SELECT: Qty ရွေးပြီးသွားရင် ----------
    elif q.data.startswith("ttqty_"):
        parts = q.data.split("_")
        svc_code = parts[1]
        qty = int(parts[2])
        if "tt_selected" not in context.user_data:
            context.user_data["tt_selected"] = {}
        context.user_data["tt_selected"][svc_code] = qty
        selected = context.user_data["tt_selected"]
        markup, total = build_tt_multiselect_menu(selected)
        caption = (
            "📱 <b>TikTok Boost Services</b>\n\n"
            "✅ ရွေးချယ်မှု သိမ်းဆည်းပြီးပါပြီ!\n\n"
        )
        caption += build_multiselect_summary(selected)
        caption += "\n\n➕ ထပ်ဆောင်း Service ရွေးနိုင်သည် သို့မဟုတ် ✅ နှိပ်ပြီး ဆက်သွားပါ"
        await q.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=markup)

    # ---------- TIKTOK MULTI-SELECT: Service ဖယ်ရှား ----------
    elif q.data.startswith("ttremove_"):
        svc_code = q.data.replace("ttremove_", "")
        if "tt_selected" in context.user_data and svc_code in context.user_data["tt_selected"]:
            del context.user_data["tt_selected"][svc_code]
        selected = context.user_data.get("tt_selected", {})
        markup, total = build_tt_multiselect_menu(selected)
        caption = "📱 <b>TikTok Boost Services</b>\n\n❌ Service ဖယ်ရှားပြီးပါပြီ\n\n"
        if selected:
            caption += build_multiselect_summary(selected)
        else:
            caption += "📌 Service တစ်ခု နှိပ်ပြီး အရေအတွက် ရွေးပါ"
        await q.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=markup)

    # ---------- TIKTOK MULTI-SELECT: Clear all ----------
    elif q.data == "tt_clear":
        context.user_data["tt_selected"] = {}
        markup, _ = build_tt_multiselect_menu({})
        caption = "📱 <b>TikTok Boost Services</b>\n\n🗑️ အားလုံး ရှင်းလင်းပြီးပါပြီ\n\n📌 Service တစ်ခု နှိပ်ပြီး ထပ်ရွေးပါ"
        await q.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=markup)

    # ---------- TIKTOK MULTI-SELECT: Back to service list ----------
    elif q.data == "tt_back_multi":
        selected = context.user_data.get("tt_selected", {})
        markup, total = build_tt_multiselect_menu(selected)
        caption = "📱 <b>TikTok Boost Services</b>\n\n"
        if selected:
            caption += build_multiselect_summary(selected) + "\n\n"
        caption += "📌 ထပ်ဆောင်း Service ရွေးနိုင်သည် သို့မဟုတ် ✅ နှိပ်ပြီး ဆက်သွားပါ"
        await q.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=markup)

    # ---------- TIKTOK MULTI-SELECT: Summary display ----------
    elif q.data == "tt_summary":
        selected = context.user_data.get("tt_selected", {})
        if selected:
            text = build_multiselect_summary(selected)
            await q.answer(f"စုစုပေါင်း: {sum(CATALOG['TT']['items'][c]['tiers'].get(q2, 0) for c, q2 in selected.items()):,} ks", show_alert=True)
        else:
            await q.answer("မရွေးရသေးပါ", show_alert=True)

    # ---------- TIKTOK MULTI-SELECT: Confirm & proceed ----------
    elif q.data == "tt_confirm_multi":
        selected = context.user_data.get("tt_selected", {})
        if not selected:
            await q.answer("⚠️ Service တစ်ခုမျှ မရွေးရသေးပါ!", show_alert=True)
            return

        # Calculate total
        total = sum(
            CATALOG["TT"]["items"][svc_code]["tiers"].get(qty, 0)
            for svc_code, qty in selected.items()
        )

        # Store in user_data for order flow
        context.user_data["flow"] = "tiktok_multi"
        context.user_data["tt_total"] = total
        context.user_data["step"] = "tt_multi_link"

        summary = build_multiselect_summary(selected)
        await q.message.reply_text(
            f"✅ <b>Order အတည်ပြုပြီးပါပြီ!</b>\n\n"
            f"{summary}\n\n"
            f"🔗 <b>TikTok Video/Profile Link</b> ပို့ပေးပါခင်ဗျ\n"
            f"(Video သည် Public ဖြစ်ရပါမည်)",
            parse_mode="HTML"
        )

    # ---------- PRICE LIST ----------
    elif q.data == "price":
        kb = []
        for code, cat in CATALOG.items():
            kb.append([InlineKeyboardButton(cat["title"], callback_data=f"pricecat_{code}")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="start")])
        await q.message.reply_text(
            "📊 <b>ဈေးနှုန်းကြည့်လိုသော Category ကို ရွေးချယ်ပါ</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif q.data.startswith("pricecat_"):
        cat_code = q.data.replace("pricecat_", "")
        text = build_price_text(cat_code)
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="price")]]
        await q.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

    # ---------- FAQ ----------
    elif q.data == "faq":
        keyboard = [
            [InlineKeyboardButton("⏱️ တက်ချိန် ဘယ်လောက်ကြာလဲ။", callback_data="faq_time")],
            [InlineKeyboardButton("🔒 အကောင့် Password ပေးရမလား။", callback_data="faq_safe")],
            [InlineKeyboardButton("🛒 Multi-Select ဘယ်လိုသုံးရမလဲ", callback_data="faq_multi")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")]
        ]
        await q.message.reply_text(
            "❓ <b>သိလိုသော မေးခွန်းကို နှိပ်ပါခင်ဗျာ</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif q.data == "faq_time":
        await q.message.reply_text(
            "⏳ ဝန်ဆောင်မှု ကြာချိန်ကတော့ ပုံမှန်အားဖြင့် 15 မိနစ် ကနေ ၂၄ နာရီအတွင်း တက်ပါတယ်ခင်ဗျာ။\n"
            "Monetization View ကတော့ ၂၄ နာရီကနေ ၇၂ နာရီအထိ ကြာနိုင်ပါတယ်ခင်ဗျ။\n"
            "PUBG / MLBB Order များကို ၃၀ မိနစ်အတွင်း ပြီးစီးအောင် လုပ်ပေးပါသည်။"
        )

    elif q.data == "faq_safe":
        await q.message.reply_text(
            "🔒 လုံးဝ ပေးစရာမလိုပါဘူးခင်ဗျာ။ Password ပေးစရာမလိုဘဲ "
            "Target Link / Game ID တစ်ခုတည်းနဲ့တင် ၁၀၀% Safe ဖြစ်လို့ စိတ်ချနိုင်ပါတယ်။"
        )

    elif q.data == "faq_multi":
        await q.message.reply_text(
            "🛒 <b>TikTok Multi-Select အသုံးပြုနည်း</b>\n\n"
            "① ဝယ်ယူရန် → TikTok Boost Services\n"
            "② ချင်သော Service ကို နှိပ်ပါ\n"
            "③ အရေအတွက် ရွေးပါ → ဈေး auto တွက်သည်\n"
            "④ Service list သို့ပြန်ပြီး နောက်တစ်ခု ထပ်ရွေးပါ\n"
            "⑤ ပြီးရင် ✅ နှိပ်ပြီး Link ပို့ပါ\n\n"
            "ဥပမာ: Like 500 (2,000ks) + View 1,000 (500ks)\n= <b>စုစုပေါင်း 2,500ks</b> သာ ပေးရမည်",
            parse_mode="HTML"
        )

    # ---------- TIKTOK TIPS ----------
    elif q.data == "tiktok_tips":
        tip = random.choice(TIKTOK_TIPS)
        keyboard = [
            [InlineKeyboardButton("🔄 နောက်တစ်ခုကြည့်ရန်", callback_data="tiktok_tips")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")]
        ]
        await q.message.reply_text(tip, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    # ---------- LUCKY DRAW ----------
    elif q.data == "lucky_menu":
        current_time = datetime.now()
        if user_id in LUCKY_DRAW_COOLDOWN:
            next_allowed_time = LUCKY_DRAW_COOLDOWN[user_id] + timedelta(days=2)
            if current_time < next_allowed_time:
                remaining_time = next_allowed_time - current_time
                hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                await q.message.reply_text(
                    f"❌ <b>ကံစမ်းခွင့် မရှိသေးပါ!</b>\n\n"
                    f"🛑 လူကြီးမင်း မဲနှိပ်ထားတာ မကြာသေးပါဘူးခင်ဗျာ။ <b>၂ ရက်တစ်ခါ</b> သာ ကံစမ်းခွင့်ပြုထားပါတယ်။\n\n"
                    f"⏳ ထပ်မံကံစမ်းနိုင်ရန်: <b>{hours} နာရီ {minutes} မိနစ်</b> လိုပါသေးတယ်ဗျ။",
                    parse_mode="HTML"
                )
                return
        LUCKY_DRAW_COOLDOWN[user_id] = current_time
        prizes = [
            "🎁 1000 TikTok Views အခမဲ့",
            "🎁 300 TikTok Likes အခမဲ့",
            "🎁 အာဘွား အခါတစ်ရာယူ😘",
            "🎁 3000 Tiktok Views အခမဲ့",
            "❌ အရမ်းချစ်တယ် ထားမသွားဘူး(နောက်၂ရက်)နေမှပြန်ကြိုးစားပါ"
        ]
        result = random.choice(prizes)
        await q.message.reply_text(
            f"🎉 <b>Knox 2-Days Lucky Draw ရလဒ်</b> 🎉\n\n"
            f"✨ လူကြီးမင်း ကံစမ်းလိုက်တဲ့ ရလဒ်ကတော့ -\n\n"
            f"👉 <b>{result}</b> ဖြစ်ပါတယ်ခင်ဗျာ! ❤️\n\n"
            f"<i>(ဆုမဲပေါက်ပါက စခရင်ရှော့ရိုက်၍ Admin @just_knox ထံ လာရောက်ထုတ်ယူနိုင်ပါသည်)</i>",
            parse_mode="HTML"
        )

    # ---------- TIKTOK SINGLE SERVICE (JP / PM) ----------
    elif q.data.startswith("svc_"):
        svc_code = q.data.replace("svc_", "")
        service = SVC_LONG.get(svc_code)
        context.user_data.clear()
        context.user_data["flow"] = "tiktok"
        context.user_data["service"] = service
        context.user_data["svc_code"] = svc_code
        context.user_data["qty"] = 1
        context.user_data["price"] = PRICE_TABLE[service][1]
        context.user_data["step"] = "link"
        await q.message.reply_text(
            f"🔗 ဝယ်ယူမည့် <b>{service}</b> အတွက် Target TikTok Link ကို ပို့ပေးပါခင်ဗျာ။",
            parse_mode="HTML"
        )

    # ---------- FIXED-PRICE ITEM SELECTED ----------
    elif q.data.startswith("item_"):
        _, cat_code, grp_code, item_code = q.data.split("_")
        cat = CATALOG[cat_code]
        item = get_item(cat_code, grp_code, item_code)
        context.user_data.clear()
        context.user_data["flow"] = "fixed"
        context.user_data["cat_code"] = cat_code
        context.user_data["grp_code"] = grp_code
        context.user_data["item_code"] = item_code
        context.user_data["item_name"] = item["name"]
        context.user_data["price"] = item["price"]
        context.user_data["step"] = "info_fixed"
        ask_label = cat.get("ask_label", "🆔 လိုအပ်သော အချက်အလက်များကို ပို့ပေးပါခင်ဗျာ")
        await q.message.reply_text(
            f"🛒 <b>{item['name']}</b>\n💰 ဈေးနှုန်း: <b>{item['price']:,} ks</b>\n\n{ask_label}",
            parse_mode="HTML"
        )

    # ---------- TIKTOK ORDER CONFIRM / REJECT ----------
    elif q.data.startswith("cf_") or q.data.startswith("rj_"):
        parts = q.data.split("_")
        action = parts[0]
        svc_code = parts[1]
        qty = parts[2]
        target_user_id = int(parts[3])
        service_full = SVC_LONG.get(svc_code, svc_code)
        qty_display = "" if svc_code in ["JP", "PM"] else f" ({qty})"
        if action == "cf":
            confirm_caption = (
                f"❣️ လူကြီးမင်း၏ <b>{service_full}{qty_display}</b> ဝယ်ယူခြင်း အောင်မြင်ပါသည်။♥️\n\n"
                "❣️ ကြာချိန်ကတော့ ဝန်ဆောင်မှုအလိုက် စတင်လုပ်ဆောင်ပေးနေပါပြီ။💓\n\n"
                "❣️ Thank You So Much 🙏\n\n"
                "❣️ အားပေးမှုအတွက် ကျေးဇူးအထူးတင်ပါတယ်💞\n\n"
                "❣️ Owner - @just_knox\n\n"
                "❣️ နောက်အသစ်တစ်ခု ဝယ်ရန် /start ကိုနှိပ်ပါ"
            )
            try:
                await context.bot.send_photo(chat_id=target_user_id, photo=ORDER_CONFIRM_IMAGE, caption=confirm_caption, parse_mode="HTML")
                await q.message.edit_caption(caption=f"✅ {service_full}{qty_display} Order Confirmed!")
            except Exception:
                await q.message.reply_text("❌ User ဆီ စာပို့မရပါ။")
        else:
            try:
                await context.bot.send_message(chat_id=target_user_id, text=f"❌ စိတ်မကောင်းပါဘူး၊ သင်၏ {service_full}{qty_display} Order မှာ ငွေလွှဲအမှားရှိ၍ ငြင်းပယ်ခံရပါသည်။")
                await q.message.edit_caption(caption=f"❌ {service_full}{qty_display} Order Rejected!")
            except Exception:
                await q.message.reply_text("❌ User ဆီ စာပို့မရပါ။")

    # ---------- MULTI-SELECT TIKTOK ORDER CONFIRM / REJECT ----------
    elif q.data.startswith("cfm_") or q.data.startswith("rjm_"):
        parts = q.data.split("_")
        action = parts[0]
        target_user_id = int(parts[1])
        if action == "cfm":
            confirm_caption = (
                "❣️ လူကြီးမင်း၏ TikTok Multi-Service Order ဝယ်ယူခြင်း အောင်မြင်ပါသည်။♥️\n\n"
                "❣️ ကြာချိန်ကတော့ ဝန်ဆောင်မှုအလိုက် စတင်လုပ်ဆောင်ပေးနေပါပြီ။💓\n\n"
                "❣️ Thank You So Much 🙏\n\n"
                "❣️ Owner - @just_knox\n\n"
                "❣️ နောက်အသစ်တစ်ခု ဝယ်ရန် /start ကိုနှိပ်ပါ"
            )
            try:
                await context.bot.send_photo(chat_id=target_user_id, photo=ORDER_CONFIRM_IMAGE, caption=confirm_caption, parse_mode="HTML")
                await q.message.edit_caption(caption="✅ TikTok Multi-Service Order Confirmed!")
            except Exception:
                await q.message.reply_text("❌ User ဆီ စာပို့မရပါ။")
        else:
            try:
                await context.bot.send_message(chat_id=target_user_id, text="❌ စိတ်မကောင်းပါဘူး၊ သင်၏ TikTok Order မှာ ငွေလွှဲအမှားရှိ၍ ငြင်းပယ်ခံရပါသည်။")
                await q.message.edit_caption(caption="❌ TikTok Multi-Service Order Rejected!")
            except Exception:
                await q.message.reply_text("❌ User ဆီ စာပို့မရပါ။")

    # ---------- FIXED-PRICE ORDER CONFIRM / REJECT ----------
    elif q.data.startswith("cfx_") or q.data.startswith("rjx_"):
        parts = q.data.split("_")
        action = parts[0]
        cat_code, grp_code, item_code = parts[1], parts[2], parts[3]
        target_user_id = int(parts[4])
        item = get_item(cat_code, grp_code, item_code)
        item_name = item["name"]
        if action == "cfx":
            confirm_caption = (
                f"❣️ လူကြီးမင်း၏ <b>{item_name}</b> ဝယ်ယူခြင်း အောင်မြင်ပါသည်။♥️\n\n"
                "❣️ ကြာချိန်ကတော့ ဝန်ဆောင်မှုအလိုက် စတင်လုပ်ဆောင်ပေးနေပါပြီ။💓\n\n"
                "❣️ Thank You So Much 🙏\n\n"
                "❣️ Owner - @just_knox\n\n"
                "❣️ နောက်အသစ်တစ်ခု ဝယ်ရန် /start ကိုနှိပ်ပါ"
            )
            try:
                await context.bot.send_photo(chat_id=target_user_id, photo=ORDER_CONFIRM_IMAGE, caption=confirm_caption, parse_mode="HTML")
                await q.message.edit_caption(caption=f"✅ {item_name} Order Confirmed!")
            except Exception:
                await q.message.reply_text("❌ User ဆီ စာပို့မရပါ။")
        else:
            try:
                await context.bot.send_message(chat_id=target_user_id, text=f"❌ စိတ်မကောင်းပါဘူး၊ သင်၏ {item_name} Order မှာ ငွေလွှဲအမှားရှိ၍ ငြင်းပယ်ခံရပါသည်။")
                await q.message.edit_caption(caption=f"❌ {item_name} Order Rejected!")
            except Exception:
                await q.message.reply_text("❌ User ဆီ စာပို့မရပါ။")

# ================= MESSAGE HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    user_text = update.message.text
    user_id = update.effective_user.id
    USER_LIST.add(user_id)

    # ---- TikTok Multi-Select: Link step ----
    if step == "tt_multi_link":
        context.user_data["link"] = user_text
        context.user_data["step"] = "tt_multi_payment"
        await update.message.reply_text(PAYMENT_INFO, parse_mode="HTML")
        return

    # ---- Single TikTok qty step ----
    if step == "qty":
        service = context.user_data.get("service")
        if not user_text.isdigit() or int(user_text) not in PRICE_TABLE[service]:
            valid = ", ".join(str(k) for k in PRICE_TABLE[service].keys())
            await update.message.reply_text(f"❌ မှန်ကန်သော အရေအတွက် ရိုက်ထည့်ပါ\n📋 ရွေးနိုင်သောနံပါတ်များ: {valid}")
            return
        qty = int(user_text)
        context.user_data["qty"] = qty
        context.user_data["price"] = PRICE_TABLE[service][qty]
        context.user_data["step"] = "link"
        await update.message.reply_text(
            "🔗 <b>TikTok Video/Profile Link</b> ပို့ပေးပါခင်ဗျ\n(Video သည် Public ဖြစ်ရပါမည်)",
            parse_mode="HTML"
        )

    # ---- Single TikTok link step ----
    elif step == "link":
        context.user_data["link"] = user_text
        context.user_data["step"] = "payment"
        await update.message.reply_text(PAYMENT_INFO, parse_mode="HTML")

    # ---- Fixed-price info step ----
    elif step == "info_fixed":
        context.user_data["info_text"] = user_text
        context.user_data["step"] = "payment_fixed"
        await update.message.reply_text(PAYMENT_INFO, parse_mode="HTML")

    # ---- No step = AI Chat ----
    elif step is None:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        # Maintain conversation history (last 6 turns)
        if "ai_history" not in context.user_data:
            context.user_data["ai_history"] = []
        history = context.user_data["ai_history"]
        ai_reply = ask_ai(user_text, history)
        # Update history
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": ai_reply})
        # Keep only last 6 messages (3 turns)
        if len(history) > 6:
            context.user_data["ai_history"] = history[-6:]
        await update.message.reply_text(ai_reply)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_LIST.add(user_id)
    step = context.user_data.get("step")
    user = update.effective_user

    # ---------- TIKTOK MULTI-SELECT ORDER ----------
    if step == "tt_multi_payment":
        selected = context.user_data.get("tt_selected", {})
        total = context.user_data.get("tt_total", 0)
        link = context.user_data.get("link", "")

        # Build readable service list for admin
        service_lines = []
        for svc_code, qty in selected.items():
            item = CATALOG["TT"]["items"][svc_code]
            price = item["tiers"].get(qty, 0)
            qty_str = f"{qty//1000}k" if qty >= 1000 else str(qty)
            service_lines.append(f"  {item['emoji']} {item['name']} x{qty_str} = {price:,}ks")
        services_text = "\n".join(service_lines)

        pending_caption = (
            "⏳ Admin မှ စစ်ဆေးနေပါပြီ (Be patient)\n\n"
            "🌟 စစ်ပြီး Order တင်ပြီးပါက စာပြန်ပို့ပေးပါမည်\n\n"
            "🤖 @Atoko_9_bot ကို အသုံးပြုသည့်အတွက် ကျေးဇူးတင်ပါသည် 🎉\n\n"
            "(⏰ Admin လိုင်းပေါ်မှာရှိရင် မြန်ပါမယ်ခင်ဗျာ)"
        )
        await update.message.reply_photo(photo=ORDER_PENDING_IMAGE, caption=pending_caption)

        admin_text = (
            f"🔔 <b>TikTok Multi-Service Order အသစ်ရောက်ရှိပါပြီ</b>\n\n"
            f"👤 <b>Customer:</b> {html.escape(user.full_name)}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"📦 <b>Services:</b>\n{services_text}\n\n"
            f"💰 <b>Total Price:</b> {total:,} ks\n"
            f"🔗 <b>Target Link:</b> {html.escape(link)}"
        )
        keyboard = [
            [InlineKeyboardButton("👤 Profile", url=f"tg://user?id={user.id}")],
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"cfm_{user.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"rjm_{user.id}")
            ]
        ]
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=admin_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data.clear()

    # ---------- SINGLE TIKTOK ORDER ----------
    elif step == "payment":
        service = context.user_data.get("service")
        qty = context.user_data["qty"]
        price = context.user_data["price"]
        link = context.user_data["link"]
        svc_code = SVC_SHORT.get(service, "SVC")
        qty_display = "" if svc_code in ["JP", "PM"] else f" ({qty})"

        pending_caption = (
            "⏳ Admin မှ စစ်ဆေးနေပါပြီ (Be patient)\n\n"
            "🌟 စစ်ပြီး Order တင်ပြီးပါက စာပြန်ပို့ပေးပါမည်\n\n"
            "🤖 @Atoko_9_bot ကို အသုံးပြုသည့်အတွက် ကျေးဇူးတင်ပါသည် 🎉\n\n"
            "(⏰ Admin လိုင်းပေါ်မှာရှိရင် မြန်ပါမယ်ခင်ဗျာ)"
        )
        await update.message.reply_photo(photo=ORDER_PENDING_IMAGE, caption=pending_caption)

        admin_text = (
            f"🔔 <b>Order အသစ်ရောက်ရှိလာပါပြီ</b>\n\n"
            f"👤 <b>Customer:</b> {html.escape(user.full_name)}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"📦 <b>အမျိုးအစား:</b> {service}{qty_display}\n"
            f"💰 <b>Total Price:</b> {price:,} ks\n"
            f"🔗 <b>Target Link/Info:</b> {html.escape(link)}"
        )
        keyboard = [
            [InlineKeyboardButton("👤 Profile", url=f"tg://user?id={user.id}")],
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"cf_{svc_code}_{qty}_{user.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"rj_{svc_code}_{qty}_{user.id}")
            ]
        ]
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=admin_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data.clear()

    # ---------- FIXED-PRICE ORDER ----------
    elif step == "payment_fixed":
        cat_code = context.user_data["cat_code"]
        grp_code = context.user_data["grp_code"]
        item_code = context.user_data["item_code"]
        item_name = context.user_data["item_name"]
        price = context.user_data["price"]
        info_text = context.user_data["info_text"]
        cat = CATALOG[cat_code]

        pending_caption = (
            "⏳ Admin မှ စစ်ဆေးနေပါပြီ (Be patient)\n\n"
            "🌟 စစ်ပြီး Order တင်ပြီးပါက စာပြန်ပို့ပေးပါမည်\n\n"
            "🤖 𝗞𝗻𝗼𝘅 𝗗𝗶𝗴𝗶𝘁𝗮𝗹 𝗦𝘁𝗼𝗿𝗲 ကို အသုံးပြုသည့်အတွက် ကျေးဇူးတင်ပါသည် 🎉\n\n"
            "(⏰ Admin လိုင်းပေါ်မှာရှိရင် ပိုမြန်ပါမယ်ခင်ဗျာ)"
        )
        await update.message.reply_photo(photo=ORDER_PENDING_IMAGE, caption=pending_caption)

        admin_text = (
            f"🔔 <b>Order အသစ်ရောက်ရှိလာပါပြီ</b>\n\n"
            f"👤 <b>Customer:</b> {html.escape(user.full_name)}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"🗂 <b>Category:</b> {cat['title']}\n"
            f"📦 <b>Item:</b> {item_name}\n"
            f"💰 <b>Total Price:</b> {price:,} ks\n"
            f"🧾 <b>Info:</b> {html.escape(info_text)}"
        )
        keyboard = [
            [InlineKeyboardButton("👤 Profile", url=f"tg://user?id={user.id}")],
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"cfx_{cat_code}_{grp_code}_{item_code}_{user.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"rjx_{cat_code}_{grp_code}_{item_code}_{user.id}")
            ]
        ]
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=admin_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data.clear()

# ================= MAIN =================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("review", review))
    app.add_handler(CommandHandler("bc", broadcast))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    print("🚀 Knox All-in-One Shop Bot is running!")
    print("✅ Claude AI Assistant: Active")
    print("✅ TikTok Multi-Select: Active")
    print("✅ Auto Price Calculate: Active")
    print("✅ /help Tutorial: Active")
    app.run_polling()

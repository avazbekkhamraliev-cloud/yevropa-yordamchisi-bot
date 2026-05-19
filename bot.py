"""
YEVROPA YORDAMCHISI - TELEGRAM BOT
Yevropa muhojirlar uchun to'liq yordamchi
O'zbek va Rus tillarida
"""

import logging
import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

BOT_TOKEN = "8713538664:AAEIOzdev_JwPe8yw3jdNj-tLAyIU-NPFuA"
ADMIN_ID = 310823898
DB_FILE = "yevropa.db"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Holatlar
LANG, MENU, COUNTRY, QUESTION = range(4)

# Matnlar
TEXTS = {
    "uz": {
        "welcome": "Yevropa Yordamchisi ga xush kelibsiz!\n\nTilni tanlang:",
        "main_menu": "Bosh menyu — nima kerak?",
        "hujjat": "Hujjat va Visa",
        "ish": "Ish topish",
        "uy": "Uy-joy",
        "tarjimon": "Tarjimon",
        "jamiyat": "O'zbeklar tarmog'i",
        "savol": "Savol berish",
        "choose_country": "Qaysi mamlakat?",
        "ask_question": "Savolingizni yozing:",
        "question_sent": "Savolingiz adminga yuborildi! Tez orada javob beramiz.",
        "back": "Orqaga",
        "main_menu_btn": "Bosh menyu",
    },
    "ru": {
        "welcome": "Добро пожаловать в Европа Помощник!\n\nВыберите язык:",
        "main_menu": "Главное меню — что вам нужно?",
        "hujjat": "Документы и Виза",
        "ish": "Поиск работы",
        "uy": "Жильё",
        "tarjimon": "Переводчик",
        "jamiyat": "Сеть узбеков",
        "savol": "Задать вопрос",
        "choose_country": "Какая страна?",
        "ask_question": "Напишите ваш вопрос:",
        "question_sent": "Ваш вопрос отправлен администратору! Ответим скоро.",
        "back": "Назад",
        "main_menu_btn": "Главное меню",
    }
}

# Ma'lumotlar bazasi
MAMLAKAT_INFO = {
    "Germaniya": {
        "hujjat": """🇩🇪 GERMANIYA - HUJJATLAR

📋 Turar joy ruxsatnomasi (Aufenthaltstitel):
• Mehnat visa: D-Visa
• Ro'yxatdan o'tish: Anmeldung (kelgandan 2 hafta ichida)
• Xorijliklar idorasi: Ausländerbehörde

📞 Foydali raqamlar:
• Qo'ng'iroq markazi: 115
• Favqulodda: 110 (politsiya), 112 (tez yordam)

🌐 Saytlar:
• make-it-in-germany.com
• bamf.de""",

        "ish": """🇩🇪 GERMANIYA - ISH TOPISH

💼 Asosiy platformalar:
• indeed.de
• stepstone.de
• arbeitsagentur.de
• linkedin.com

📊 Eng ko'p talab qilinadigan kasblar:
• IT mutaxassislar
• Hamshiralar
• Qurilish ishchilari
• Oshpazlar

💰 O'rtacha oylik maosh: 2000-4000€
Minimal ish haqi: 12.41€/soat

📞 Ishga joylashish markazi:
Agentur für Arbeit - 0800 4 5555 00""",

        "uy": """🇩🇪 GERMANIYA - UY-JOY

🏠 Kvartira topish saytlari:
• immobilienscout24.de
• wg-gesucht.de (xona)
• ebay-kleinanzeigen.de

💰 O'rtacha narxlar (oyiga):
• Berlin: 800-1500€
• München: 1200-2000€
• Hamburg: 900-1600€

📋 Kerakli hujjatlar:
• Pasport
• Ish shartnomasi
• Schufa (kredit tarix)
• 3 oylik bank ko'chirma""",

        "tarjimon": """🇩🇪 GERMANIYA - TARJIMON

📱 Bepul ilovalar:
• DeepL (eng yaxshi!)
• Google Translate
• Dict.cc (lug'at)

👨‍💼 Rasmiy tarjimon:
• Adliya vazirligi ro'yxatidagi tarjimonlar
• bundessprachamt.de
• Narxi: 50-100€/soat

🏥 Tibbiy tarjimon:
• Ko'p kasalxonalarda bepul
• Sprach- und Integrationsmittler""",

        "jamiyat": """🇩🇪 GERMANIYA - O'ZBEKLAR

👥 Telegram guruhlar:
• @uzbeks_in_germany
• @uzbekistan_germany

🕌 Masjidlar:
• Berlin: DITIB masjidi
• Frankfurt: Fatih masjidi

🍽️ O'zbek restoranlar:
• Berlin: Navoi, Samarkand
• München: Tashkent"""
    },

    "Polsha": {
        "hujjat": """🇵🇱 POLSHA - HUJJATLAR

📋 Asosiy hujjatlar:
• Karta Pobytu (turar joy kartasi)
• PESEL raqami (shaxsiy raqam)
• Ro'yxatdan o'tish: Zameldowanie

📞 Foydali:
• Migratsiya idorasi: udsc.gov.pl
• Favqulodda: 112

⏱️ Muddatlar:
• Viza: 15-30 kun
• Karta Pobytu: 1-3 oy""",

        "ish": """🇵🇱 POLSHA - ISH TOPISH

💼 Platformalar:
• pracuj.pl
• olx.pl/praca
• linkedin.com

💰 O'rtacha maosh:
• Minimal: 4300 PLN/oy
• O'rtacha: 6000-8000 PLN
• 1 PLN ≈ 340 so'm

🔥 Talab qilinadigan:
• Qurilish, omborxona
• IT, dasturchilar
• Hamshiralar""",

        "uy": """🇵🇱 POLSHA - UY-JOY

🏠 Saytlar:
• otodom.pl
• olx.pl/nieruchomosci
• gratka.pl

💰 Narxlar (oyiga):
• Varshava: 2000-4000 PLN
• Krakov: 1500-3000 PLN
• Vrotslav: 1500-2800 PLN""",

        "tarjimon": """🇵🇱 POLSHA - TARJIMON

📱 Ilovalar:
• DeepL (eng yaxshi)
• Google Translate
• Linguee

👨‍💼 Rasmiy tarjimon:
• tepis.org.pl
• Narxi: 40-80€/soat""",

        "jamiyat": """🇵🇱 POLSHA - O'ZBEKLAR

👥 Telegram:
• @uzbeks_in_poland
• @tashkent_warsaw

🕌 Masjidlar:
• Varshava: Liga Muzulmańska
• Krakov: Islam markazi"""
    },

    "Chexiya": {
        "hujjat": """🇨🇿 CHEXIYA - HUJJATLAR

📋 Asosiy:
• Uzun muddatli visa (D)
• Yashash ruxsatnomasi
• Ro'yxatdan o'tish: 3 kun ichida

📞 Migratsiya idorasi:
• mvcr.cz
• Favqulodda: 112""",

        "ish": """🇨🇿 CHEXIYA - ISH TOPISH

💼 Saytlar:
• jobs.cz
• prace.cz
• linkedin.com

💰 Maosh:
• Minimal: 18 900 CZK
• O'rtacha: 35 000-45 000 CZK""",

        "uy": """🇨🇿 CHEXIYA - UY-JOY

🏠 Saytlar:
• sreality.cz
• bezrealitky.cz

💰 Praga narxlari:
• 1 xona: 15 000-25 000 CZK/oy""",

        "tarjimon": """🇨🇿 CHEXIYA - TARJIMON

📱 DeepL, Google Translate
👨‍💼 justtranslate.cz""",

        "jamiyat": """🇨🇿 CHEXIYA - O'ZBEKLAR

👥 Telegram: @uzbeks_czech
🕌 Praha Islam markazi"""
    }
}

def init_db():
    con = sqlite3.connect(DB_FILE)
    con.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        lang TEXT DEFAULT 'uz',
        country TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question TEXT,
        answer TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    con.commit()
    con.close()

def db_get_user(uid):
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone()
    con.close()
    return row

def db_set_lang(uid, lang):
    con = sqlite3.connect(DB_FILE)
    con.execute("""INSERT INTO users(user_id, lang) VALUES(?,?)
                   ON CONFLICT(user_id) DO UPDATE SET lang=?""", (uid, lang, lang))
    con.commit()
    con.close()

def t(lang, key):
    return TEXTS.get(lang, TEXTS["uz"]).get(key, key)

def main_menu_kb(lang):
    kb = [
        [InlineKeyboardButton(t(lang,"hujjat"), callback_data="cat_hujjat")],
        [InlineKeyboardButton(t(lang,"ish"), callback_data="cat_ish")],
        [InlineKeyboardButton(t(lang,"uy"), callback_data="cat_uy")],
        [InlineKeyboardButton(t(lang,"tarjimon"), callback_data="cat_tarjimon")],
        [InlineKeyboardButton(t(lang,"jamiyat"), callback_data="cat_jamiyat")],
        [InlineKeyboardButton(t(lang,"savol"), callback_data="cat_savol")],
    ]
    return InlineKeyboardMarkup(kb)

def country_kb():
    kb = [
        [InlineKeyboardButton("🇩🇪 Germaniya", callback_data="country_Germaniya")],
        [InlineKeyboardButton("🇵🇱 Polsha", callback_data="country_Polsha")],
        [InlineKeyboardButton("🇨🇿 Chexiya", callback_data="country_Chexiya")],
        [InlineKeyboardButton("🇦🇹 Avstriya", callback_data="country_Avstriya")],
        [InlineKeyboardButton("🇳🇱 Niderlandiya", callback_data="country_Niderlandiya")],
        [InlineKeyboardButton("🇧🇪 Belgiya", callback_data="country_Belgiya")],
        [InlineKeyboardButton("🇸🇪 Shvetsiya", callback_data="country_Shvetsiya")],
        [InlineKeyboardButton("🇳🇴 Norvegiya", callback_data="country_Norvegiya")],
    ]
    return InlineKeyboardMarkup(kb)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("O'zbek", callback_data="lang_uz"),
        InlineKeyboardButton("Русский", callback_data="lang_ru")
    ]])
    if update.message:
        await update.message.reply_text(TEXTS["uz"]["welcome"], reply_markup=kb)
    elif update.callback_query:
        await update.callback_query.edit_message_text(TEXTS["uz"]["welcome"], reply_markup=kb)
    return LANG

async def choose_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    db_set_lang(q.from_user.id, lang)
    ctx.user_data["lang"] = lang
    await q.edit_message_text(t(lang, "main_menu"), reply_markup=main_menu_kb(lang))
    return MENU

async def main_menu_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user = db_get_user(q.from_user.id)
    lang = user["lang"] if user else ctx.user_data.get("lang", "uz")
    ctx.user_data["lang"] = lang

    if data == "cat_savol":
        await q.edit_message_text(t(lang, "ask_question"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(t(lang,"back"), callback_data="back_menu")
            ]]))
        ctx.user_data["waiting_question"] = True
        return QUESTION

    if data == "back_menu":
        await q.edit_message_text(t(lang, "main_menu"), reply_markup=main_menu_kb(lang))
        return MENU

    # Kategoriya tanlandi - mamlakat tanlash
    ctx.user_data["category"] = data.replace("cat_", "")
    await q.edit_message_text(t(lang, "choose_country"), reply_markup=country_kb())
    return COUNTRY

async def country_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = ctx.user_data.get("lang", "uz")

    if q.data == "back_menu":
        await q.edit_message_text(t(lang, "main_menu"), reply_markup=main_menu_kb(lang))
        return MENU

    country = q.data.replace("country_", "")
    category = ctx.user_data.get("category", "hujjat")

    # Ma'lumot olish
    country_data = MAMLAKAT_INFO.get(country, {})
    info = country_data.get(category)

    if info:
        back_kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(t(lang,"back"), callback_data="back_menu")
        ]])
        await q.edit_message_text(info, reply_markup=back_kb)
    else:
        # Ma'lumot yo'q - umumiy javob
        back_kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(t(lang,"back"), callback_data="back_menu")
        ]])
        msg = (f"Bu mamlakat haqida ma'lumot tez orada qo'shiladi!\n\n"
               f"Savol berish uchun /savol yozing." if lang=="uz" else
               f"Информация об этой стране скоро будет добавлена!\n\n"
               f"Для вопроса напишите /savol")
        await q.edit_message_text(msg, reply_markup=back_kb)

    return MENU

async def question_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.user_data.get("waiting_question"):
        return MENU

    uid = update.effective_user.id
    lang = ctx.user_data.get("lang", "uz")
    question = update.message.text

    # Savolni bazaga saqlash
    con = sqlite3.connect(DB_FILE)
    con.execute("INSERT INTO questions(user_id, question) VALUES(?,?)", (uid, question))
    con.commit()
    con.close()

    # Adminga yuborish
    user = update.effective_user
    try:
        await ctx.bot.send_message(
            ADMIN_ID,
            f"YANGI SAVOL!\n\n"
            f"Foydalanuvchi: {user.full_name}\n"
            f"ID: {uid}\n"
            f"Savol: {question}"
        )
    except Exception as e:
        logger.error(f"Admin xabar xato: {e}")

    ctx.user_data["waiting_question"] = False
    await update.message.reply_text(
        t(lang, "question_sent"),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(t(lang,"main_menu_btn"), callback_data="back_menu")
        ]])
    )
    return MENU

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = db_get_user(update.effective_user.id)
    lang = user["lang"] if user else "uz"
    await update.message.reply_text(
        t(lang, "main_menu"),
        reply_markup=main_menu_kb(lang)
    )
    return MENU

async def stats_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    users = con.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    questions = con.execute("SELECT COUNT(*) as c FROM questions").fetchone()["c"]
    con.close()
    await update.message.reply_text(
        f"STATISTIKA:\n"
        f"Foydalanuvchilar: {users}\n"
        f"Savollar: {questions}"
    )

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(main_menu_handler, pattern="^back_menu$")
        ],
        states={
            LANG: [CallbackQueryHandler(choose_lang, pattern="^lang_")],
            MENU: [
                CallbackQueryHandler(main_menu_handler, pattern="^cat_"),
                CallbackQueryHandler(main_menu_handler, pattern="^back_menu$"),
                CallbackQueryHandler(country_handler, pattern="^country_"),
            ],
            COUNTRY: [
                CallbackQueryHandler(country_handler, pattern="^country_"),
                CallbackQueryHandler(main_menu_handler, pattern="^back_menu$"),
            ],
            QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, question_handler),
                CallbackQueryHandler(main_menu_handler, pattern="^back_menu$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("stats", stats_cmd))

    logger.info("Yevropa Yordamchisi ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

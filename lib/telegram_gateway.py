import asyncio, webbrowser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

import config
from lib import memory, envstore, nim

ROSTER = [
    ("scout", "🕵️", "Scout"), ("triage", "🔍", "Triage"), ("sentinel", "🛡️", "Sentinel"),
    ("scribe", "📝", "Scribe"), ("tester", "🧪", "Tester"), ("medic", "🚑", "Medic"),
    ("release", "📦", "Release"), ("bridge", "🔌", "Bridge"), ("herald", "📣", "Herald"),
    ("diplomat", "🕊️", "Diplomat"),
]

HELP_TEXT = ("<b>Perintah:</b>\n/status — papan hidup 10 agen\n/patrol — kirim Scout sekarang\n"
             "/reports — daftar laporan\n/report &lt;id&gt; — baca laporan\n/model — otak aktif\n"
             "/approve — setujui draft Sayap C\n/help — bantuan ini")

def _menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Status", callback_data="status"),
         InlineKeyboardButton("🕵️ Patroli", callback_data="patrol")],
        [InlineKeyboardButton("📚 Laporan", callback_data="reports"),
         InlineKeyboardButton("🧠 Model", callback_data="model")],
        [InlineKeyboardButton("❓ Bantuan", callback_data="help")],
    ])

def _escape(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _board() -> str:
    states = {s["agent"]: s for s in memory.get_all_agent_states()}
    lines = ["<b>🏛️ RUANG KERJA ZCP2O — papan hidup</b>", ""]
    for aid, emo, name in ROSTER:
        s = states.get(aid)
        if s:
            lines.append(f"{emo} <b>{name}</b>: {s['state']} · {s['action']}")
        else:
            lines.append(f"{emo} <b>{name}</b>: offline · tidur 💤")
    lines.append("")
    lines.append(f"🧠 Otak: <code>{config.SCOUT_MODEL}</code>")
    return "\n".join(lines)

def _reports_text() -> str:
    evs = [e for e in memory.recent_events(30) if (e["report_id"] or 0) > 0]
    if not evs:
        return "📚 Belum ada laporan tersimpan."
    lines = ["<b>📚 Laporan terakhir:</b>"]
    for e in evs[:8]:
        lines.append(f"• <code>/report {e['report_id']}</code> — {e['agent']} · {e['bubble']}")
    return "\n".join(lines)

async def _send_long(chat_id, raw, context):
    text = _escape(raw)
    if len(text) <= 4000:
        await context.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
        return
    for i in range(0, len(text), 4000):
        await context.bot.send_message(chat_id, text[i:i+4000])

async def cmd_start(update, context):
    await update.message.reply_text(
        "<b>⚔️ ZCP2O Maintainer Bot</b>\nKru sepuluh jiwa siap melayani.\n"
        "Tekan tombol di bawah atau ketik perintah.",
        parse_mode=ParseMode.HTML, reply_markup=_menu())

async def cmd_status(update, context):
    await update.message.reply_text(_board(), parse_mode=ParseMode.HTML, reply_markup=_menu())

async def cmd_patrol(update, context):
    msg = await update.message.reply_text("🕵️ Scout berangkat patroli…")
    from agents import scout
    result = await asyncio.to_thread(scout.patrol)
    await msg.delete()
    await _send_long(update.effective_chat.id, result, context)

async def cmd_reports(update, context):
    await update.message.reply_text(_reports_text(), parse_mode=ParseMode.HTML)

async def cmd_report(update, context):
    if not context.args:
        await update.message.reply_text("Pakai: /report <id>")
        return
    f = config.REPORTS_DIR / f"report_{int(context.args[0])}.md"
    if not f.exists():
        await update.message.reply_text("Laporan tidak ditemukan.")
        return
    await _send_long(update.effective_chat.id, f.read_text(encoding="utf-8"), context)

async def cmd_model(update, context):
    await update.message.reply_text(
        f"🧠 Model aktif: <code>{config.SCOUT_MODEL}</code>\nGanti lewat menu → 🧠 Model",
        parse_mode=ParseMode.HTML)

async def cmd_approve(update, context):
    await update.message.reply_text("🕊️ Belum ada draft Sayap C yang menunggu persetujuan.")

async def cmd_help(update, context):
    await update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)

async def on_button(update, context):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == "status":
        await q.edit_message_text(_board(), parse_mode=ParseMode.HTML, reply_markup=_menu())
    elif data == "patrol":
        await q.edit_message_text("🕵️ Scout berangkat patroli…")
        from agents import scout
        result = await asyncio.to_thread(scout.patrol)
        await _send_long(q.message.chat_id, result, context)
    elif data == "reports":
        await q.edit_message_text(_reports_text(), parse_mode=ParseMode.HTML, reply_markup=_menu())
    elif data == "model":
        ids = await asyncio.to_thread(nim.list_models)
        pref = [i for i in sorted(ids) if any(k in i for k in ("instruct", "chat", "r1", "v3"))][:8]
        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton(i, callback_data="modelset:" + i)] for i in pref])
        await q.edit_message_text("🧠 Pilih otak:", reply_markup=kb)
    elif data.startswith("modelset:"):
        pick = data.split(":", 1)[1]
        envstore.set_value("SCOUT_MODEL", pick)
        config.SCOUT_MODEL = pick
        await q.edit_message_text(f"✅ Otak kini: <code>{pick}</code>",
                                  parse_mode=ParseMode.HTML, reply_markup=_menu())
    elif data == "help":
        await q.edit_message_text(HELP_TEXT, parse_mode=ParseMode.HTML, reply_markup=_menu())

def ensure_token() -> str:
    tok = config.TELEGRAM_BOT_TOKEN
    if tok:
        return tok
    print("\n📡 MULUT: saya butuh token bot Telegram untuk bisa bicara.")
    print("   Membuka BotFather di browser…")
    webbrowser.open("https://t.me/BotFather")
    print("   Ketik /newbot → beri nama → copy token")
    tok = input("   Tempel token di sini: ").strip()
    if not tok:
        raise SystemExit("❌ Token kosong — ulangi: python main.py telegram")
    envstore.set_value("TELEGRAM_BOT_TOKEN", tok)
    config.TELEGRAM_BOT_TOKEN = tok
    return tok

def run():
    tok = ensure_token()
    app = Application.builder().token(tok).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("patrol", cmd_patrol))
    app.add_handler(CommandHandler("reports", cmd_reports))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("model", cmd_model))
    app.add_handler(CommandHandler("approve", cmd_approve))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(on_button))
    print("📡 Bot hidup. Buka Telegram Anda dan ketik /start.")
    app.run_polling()
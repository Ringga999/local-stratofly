import asyncio, webbrowser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

import config
from lib import memory, provider_hub

ROSTER = [
    ("scout", "🕵️", "Scout"), ("triage", "🔍", "Triage"), ("sentinel", "🛡️", "Sentinel"),
    ("scribe", "📝", "Scribe"), ("tester", "🧪", "Tester"), ("medic", "🚑", "Medic"),
    ("release", "📦", "Release"), ("bridge", "🔌", "Bridge"), ("herald", "📣", "Herald"),
    ("diplomat", "🕊️", "Diplomat"),
]

HELP_TEXT = ("<b>Commands:</b>\n/status — live board of the 10 agents\n/patrol — send Scout now\n"
             "/reports — list reports\n/report &lt;id&gt; — read a report\n"
             "/brains — provider hub status\n/approve — approve a Wing-C draft\n/help — this help")

def _menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Status", callback_data="status"),
         InlineKeyboardButton("🕵️ Patrol", callback_data="patrol")],
        [InlineKeyboardButton("📚 Reports", callback_data="reports"),
         InlineKeyboardButton("🧠 Brains", callback_data="brains")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ])

def _escape(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _board() -> str:
    states = {s["agent"]: s for s in memory.get_all_agent_states()}
    lines = ["<b>🏛️ ZCP2O WORKROOM — live board</b>", ""]
    for aid, emo, name in ROSTER:
        s = states.get(aid)
        if s:
            lines.append(f"{emo} <b>{name}</b>: {s['state']} · {s['action']}")
        else:
            lines.append(f"{emo} <b>{name}</b>: offline · asleep 💤")
    lines.append("")
    avail = provider_hub.available_providers()
    lines.append(f"🧠 Providers with keys: {', '.join(avail) if avail else 'none'}")
    return "\n".join(lines)

def _reports_text() -> str:
    evs = [e for e in memory.recent_events(30) if (e["report_id"] or 0) > 0]
    if not evs:
        return "📚 No reports stored yet."
    lines = ["<b>📚 Latest reports:</b>"]
    for e in evs[:8]:
        lines.append(f"• <code>/report {e['report_id']}</code> — {e['agent']} · {e['bubble']}")
    return "\n".join(lines)

def _brains_text() -> str:
    lines = ["<b>🧠 PROVIDER HUB</b>"]
    for name, chain in provider_hub.describe():
        lines.append(f"<b>{name}</b>:")
        lines.extend(chain)
    lines.append("")
    lines.append("To add providers later, put keys in .env "
                 "(GROQ_API_KEY, OPENROUTER_API_KEY, …) and restart.")
    return "\n".join(lines)

async def _send_long(chat_id, raw, context):
    text = _escape(raw)
    if len(text) <= 4000:
        await context.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
        return
    for i in range(0, len(text), 4000):
        await context.bot.send_message(chat_id, text[i:i+4000])

async def cmd_start(update, context):
    memory.set_kv("tg_owner", str(update.effective_chat.id))
    await update.message.reply_text(
        "<b>⚔️ ZCP2O Maintainer Bot</b>\nTen souls ready to serve.\n"
        "Use the buttons below or type a command.",
        parse_mode=ParseMode.HTML, reply_markup=_menu())

async def cmd_status(update, context):
    await update.message.reply_text(_board(), parse_mode=ParseMode.HTML, reply_markup=_menu())

async def cmd_patrol(update, context):
    msg = await update.message.reply_text("🕵️ Scout is heading out on patrol…")
    from agents import scout
    result = await asyncio.to_thread(scout.patrol)
    await msg.delete()
    await _send_long(update.effective_chat.id, result, context)

async def cmd_reports(update, context):
    await update.message.reply_text(_reports_text(), parse_mode=ParseMode.HTML)

async def cmd_report(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /report <id>")
        return
    try:
        rid = int(context.args[0])
    except Exception:
        await update.message.reply_text("Invalid id.")
        return
    f = config.REPORTS_DIR / f"report_{rid}.md"
    if not f.exists():
        await update.message.reply_text("Report not found.")
        return
    await _send_long(update.effective_chat.id, f.read_text(encoding="utf-8"), context)

async def cmd_brains(update, context):
    await update.message.reply_text(_brains_text(), parse_mode=ParseMode.HTML)

async def cmd_approve(update, context):
    await update.message.reply_text("🕊️ No Wing-C drafts waiting for approval yet.")

async def cmd_help(update, context):
    await update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)

async def on_button(update, context):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == "status":
        await q.edit_message_text(_board(), parse_mode=ParseMode.HTML, reply_markup=_menu())
    elif data == "patrol":
        await q.edit_message_text("🕵️ Scout is heading out on patrol…")
        from agents import scout
        result = await asyncio.to_thread(scout.patrol)
        await _send_long(q.message.chat_id, result, context)
    elif data == "reports":
        await q.edit_message_text(_reports_text(), parse_mode=ParseMode.HTML, reply_markup=_menu())
    elif data == "brains":
        await q.edit_message_text(_brains_text(), parse_mode=ParseMode.HTML, reply_markup=_menu())
    elif data == "help":
        await q.edit_message_text(HELP_TEXT, parse_mode=ParseMode.HTML, reply_markup=_menu())

async def _deliver(context):
    owner = memory.get_kv("tg_owner")
    if not owner:
        return
    pend = memory.pending_notifications()
    if not pend:
        return
    for n in pend:
        icon = {"warn": "⚠️", "crit": "🚨"}.get(n["severity"], "ℹ️")
        text = f"{icon} <b>{_escape(n['title'])}</b>\n{_escape(n['body'])}"
        await context.bot.send_message(int(owner), text, parse_mode=ParseMode.HTML)
    memory.mark_notifications_delivered([n["id"] for n in pend])

def ensure_token() -> str:
    tok = config.TELEGRAM_BOT_TOKEN
    if tok:
        return tok
    print("\n📡 MOUTH: I need a Telegram bot token to speak.")
    print("   Opening BotFather in your browser…")
    webbrowser.open("https://t.me/BotFather")
    print("   Send /newbot → give a name → copy the token")
    tok = input("   Paste the token here: ").strip()
    if not tok:
        raise SystemExit("❌ Empty token — run again: python main.py telegram")
    from lib import envstore
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
    app.add_handler(CommandHandler("brains", cmd_brains))
    app.add_handler(CommandHandler("approve", cmd_approve))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(on_button))
    app.job_queue.run_repeating(_deliver, interval=10, first=5)
    print("📡 Bot alive. Open Telegram and send /start.")
    app.run_polling()
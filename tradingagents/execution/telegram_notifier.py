"""
Limitless AI — Telegram Notifier
Sends trade signal alerts to Sam's Telegram via OpenClaw bot.
"""
import requests
from loguru import logger

TELEGRAM_BOT_TOKEN = "8022194851:AAEvMKbyv0lHiTutM-GnzbIiZqIZyQXcoU8"
TELEGRAM_CHAT_ID = "8694352076"


def send_telegram(message: str) -> bool:
    """Send a message to Sam's Telegram. Returns True on success."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        if resp.status_code == 200:
            logger.info("Telegram notification sent.")
            return True
        else:
            logger.warning(f"Telegram notification failed: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.warning(f"Telegram notification error: {e}")
        return False


def notify_cron_pending(symbol, direction, limit_price, stop_loss_price,
                        quantity, confidence_score, mirofish_output, trade_id):
    """Alert Sam when a BUY/SELL signal fires during a cron run."""
    mf_str = ""
    if mirofish_output:
        mf_label = mirofish_output.get("label", "N/A")
        mf_score = mirofish_output.get("sentiment_score", "N/A")
        mf_agents = mirofish_output.get("agent_count", "N/A")
        mf_str = f"\n🐟 <b>MiroFish:</b> {mf_label} ({mf_score}) — {mf_agents} agents"

    msg = (
        f"🚨 <b>LIMITLESS AI — SIGNAL DETECTED</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Asset:</b> {symbol}\n"
        f"{'🟢' if direction.upper() == 'BUY' else '🔴'} <b>Signal:</b> {direction.upper()}\n"
        f"💰 <b>Entry Price:</b> ${limit_price:,.2f}\n"
        f"🛑 <b>Stop-Loss:</b> ${stop_loss_price:,.2f}\n"
        f"📦 <b>Quantity:</b> {quantity}\n"
        f"🎯 <b>Confidence:</b> {confidence_score}/100"
        f"{mf_str}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ Trade logged as <b>CRON_PENDING</b> — no order placed.\n"
        f"▶️ Run pipeline manually to confirm or reject:\n"
        f"<code>cd /root/limitless-ai && source TradingAgents/venv/bin/activate && python run_paper_trade.py</code>\n"
        f"🆔 Trade ID: <code>{trade_id}</code>"
    )
    return send_telegram(msg)


def notify_hold(symbol, price, confidence, mirofish_label=None):
    """Periodic HOLD summary — send every 6th cron run to avoid spam."""
    mf_str = f" | MiroFish: {mirofish_label}" if mirofish_label else ""
    msg = (
        f"✅ <b>LIMITLESS AI — HOLD</b>\n"
        f"{symbol} @ ${price:,.2f} | Confidence: {confidence}/100{mf_str}"
    )
    return send_telegram(msg)

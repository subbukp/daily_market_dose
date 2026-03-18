#!/usr/bin/env python3
"""
RPi Market Notifier — Daily market data push notifications.

Fetches market data from TickerTape APIs and sends reports via
Telegram and Email.

Usage:
    python main.py              # Run once (manual / test)
    python main.py --test       # Dry run — print report without sending
"""

import sys
import os
import argparse
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.fetcher import fetch_all_data
from data.formatter import format_telegram_report, format_email_report
from notifications.telegram_notifier import send_telegram
from notifications.email_notifier import send_email
from healthcheck import save_run_status, run_health_check, print_health_report, send_heartbeat_telegram
from config.settings import CHANNEL_TELEGRAM, CHANNEL_EMAIL
from data.sources import fetch_mmi, fetch_secondary_bonds

app = FastAPI(title="Market data", version="1.0.0")

def daily_job(dry_run: bool = False):
    """Fetch market data and send notifications."""
    print("📡 Fetching market data from TickerTape APIs...")
    print(f"📢 Channels: Telegram={'ON' if CHANNEL_TELEGRAM else 'OFF'} | Email={'ON' if CHANNEL_EMAIL else 'OFF'}")
    errors = []
    sent_channels = []

    try:
        data = fetch_all_data()
    except Exception as e:
        save_run_status(success=False, details=f"Data fetch crashed: {e}")
        print(f"❌ Data fetch crashed: {e}")
        return

    mmi = data.get("mmi")
    quotes = data.get("quotes", [])

    if not mmi and not quotes:
        save_run_status(success=False, details="No data fetched from any source")
        print("⚠️  No data fetched from any source. Aborting.")
        return

    print(f"✅ Fetched MMI: {'Yes' if mmi else 'No'} | Quotes: {len(quotes)} stocks")

    # Generate reports
    tg_report = format_telegram_report(data)
    email_report = format_email_report(data)

    if dry_run:
        print("\n" + "=" * 50)
        print("🧪 DRY RUN — Telegram Report Preview:")
        print("=" * 50)
        print(tg_report)
        print("\n" + "=" * 50)
        print("🧪 DRY RUN — Email report generated (HTML, not printed)")
        print("=" * 50)
        save_run_status(success=True, details="Dry run completed")
        return

    # ── Send via Telegram ──
    if CHANNEL_TELEGRAM:
        try:
            send_telegram(tg_report)
            print("✅ Telegram notification sent!")
            sent_channels.append("Telegram")
        except Exception as e:
            errors.append(f"Telegram: {e}")
            print(f"❌ Telegram failed: {e}")
    else:
        print("⏭️  Telegram skipped (CHANNEL_TELEGRAM=false)")

    # ── Send via Email ──
    if CHANNEL_EMAIL:
        try:
            send_email("📊 Daily Market Report", email_report)
            print("✅ Email notification sent!")
            sent_channels.append("Email")
        except Exception as e:
            errors.append(f"Email: {e}")
            print(f"❌ Email failed: {e}")
    else:
        print("⏭️  Email skipped (CHANNEL_EMAIL=false)")

    # ── Save run status ──
    if errors:
        save_run_status(success=False, details=" | ".join(errors))
    else:
        channels_str = ", ".join(sent_channels) if sent_channels else "No channels"
        save_run_status(success=True, details=f"MMI + {len(quotes)} quotes → {channels_str}")


def main():
    parser = argparse.ArgumentParser(description="RPi Market Notifier")
    parser.add_argument(
        "--test", "--dry-run",
        action="store_true",
        help="Dry run — fetch data and print report without sending notifications",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Run health check and display status",
    )
    parser.add_argument(
        "--heartbeat",
        action="store_true",
        help="Send a heartbeat to Telegram now",
    )
    args = parser.parse_args()

    if args.health:
        report = run_health_check()
        print_health_report(report)
        return

    if args.heartbeat:
        send_heartbeat_telegram()
        return

    daily_job(dry_run=args.test)
    
    
@app.get('/market') 
def root():
    return {"message": "Hello world!"}

#@app.get('/mmi', operation_id="get_mood_indicator", summary="Get the Market Mood Index")
@app.get('/market/mmi')
def mood_indicator():
    return fetch_mmi()
    
#@app.get('/bonds', operation_id="get_investable_bonds", summary="Get investable secondary bonds")
@app.get('/market/bonds')
def investable_bonds():
    return fetch_secondary_bonds()
    
    
@app.get('/market/send-mail')
def send_mail():
    main()
    return({'Message': 'method called'})
    
mcp = FastApiMCP(app)
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)


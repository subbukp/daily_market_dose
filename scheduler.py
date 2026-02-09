#!/usr/bin/env python3
"""
RPi Market Scheduler — Runs the daily market notification job on a schedule.

Uses APScheduler with cron trigger to run at the configured time.
Includes periodic health checks and optional HTTP health endpoint.
Designed to be run as a system service (systemd) or in a terminal.

Usage:
    python scheduler.py                  # Run scheduler only
    python scheduler.py --with-health    # Run scheduler + HTTP health endpoint
    python scheduler.py --port 9090      # Custom health endpoint port
"""

import sys
import os
import argparse
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from main import daily_job
from healthcheck import run_health_check, send_heartbeat_telegram, start_health_server
from config.settings import (
    NOTIFY_HOUR, NOTIFY_MINUTE, TIMEZONE,
    HEARTBEAT_INTERVAL_HOURS, HEARTBEAT_ENABLED,
)


def periodic_health_check():
    """Run a periodic health check and log results."""
    report = run_health_check()
    status = report["status"].upper()
    failed = [c["name"] for c in report["checks"] if c["status"] == "fail"]
    if failed:
        print(f"🏥 Health: {status} — Failed: {', '.join(failed)}")
    else:
        print(f"🏥 Health: {status} — All checks passed")


def start_scheduler(with_health_server: bool = False, health_port: int = 8080):
    scheduler = BlockingScheduler()

    # ── Daily market report job (Mon–Fri) ──
    scheduler.add_job(
        daily_job,
        trigger=CronTrigger(
            hour=NOTIFY_HOUR,
            minute=NOTIFY_MINUTE,
            day_of_week="mon-fri",
            timezone=TIMEZONE,
        ),
        id="daily_market_report",
        name="Daily Market Report",
        replace_existing=True,
    )

    # ── Hourly Telegram heartbeat ──
    if HEARTBEAT_ENABLED:
        scheduler.add_job(
            send_heartbeat_telegram,
            trigger=IntervalTrigger(hours=HEARTBEAT_INTERVAL_HOURS),
            id="telegram_heartbeat",
            name="Telegram Heartbeat",
            replace_existing=True,
        )

    print(f"⏰ Market Notifier Scheduler started!")
    print(f"   📅 Report:    Mon–Fri at {NOTIFY_HOUR:02d}:{NOTIFY_MINUTE:02d} {TIMEZONE}")
    if HEARTBEAT_ENABLED:
        print(f"   💓 Heartbeat: Every {HEARTBEAT_INTERVAL_HOURS}h → Telegram")
    else:
        print(f"   💓 Heartbeat: Disabled")

    # ── Optional HTTP health endpoint in a background thread ──
    if with_health_server:
        health_thread = threading.Thread(
            target=start_health_server,
            kwargs={"port": health_port},
            daemon=True,
        )
        health_thread.start()
        print(f"   🌐 HTTP:      http://0.0.0.0:{health_port}/health")

    print(f"   Press Ctrl+C to stop.\n")

    # Send initial heartbeat on startup
    print("📡 Running startup heartbeat...")
    send_heartbeat_telegram()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Scheduler stopped.")
        scheduler.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RPi Market Scheduler")
    parser.add_argument(
        "--with-health",
        action="store_true",
        help="Start HTTP health endpoint alongside scheduler",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP health endpoint (default: 8080)",
    )
    args = parser.parse_args()
    start_scheduler(with_health_server=args.with_health, health_port=args.port)


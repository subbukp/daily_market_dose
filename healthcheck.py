#!/usr/bin/env python3
"""
RPi Market — Health Check Module

Checks:
  ✓ API connectivity (MMI + Quotes endpoints)
  ✓ Telegram bot configuration & reachability
  ✓ Email SMTP configuration & reachability
  ✓ Last successful run status
  ✓ System info (uptime, memory, disk)

Usage:
    python healthcheck.py              # Run full health check
    python healthcheck.py --serve      # Start HTTP health endpoint on port 8080
    python healthcheck.py --port 9090  # Custom port for HTTP endpoint
"""

import sys
import os
import json
import time
import socket
import smtplib
import argparse
import platform
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from config.settings import (
    MMI_API,
    QUOTES_API,
    IPO_API,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    EMAIL_SENDER,
    EMAIL_PASSWORD,
    SMTP_SERVER,
    SMTP_PORT,
    HEARTBEAT_ENABLED,
)

# ─── Constants ───
PROJECT_ROOT = Path(__file__).parent
STATUS_FILE = PROJECT_ROOT / "data" / ".last_run_status.json"


class Status(Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


# ─── Status Persistence ───

def save_run_status(success: bool, details: str = ""):
    """Save the last run status to a JSON file."""
    status = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "details": details,
    }
    try:
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATUS_FILE.write_text(json.dumps(status, indent=2))
    except Exception as e:
        print(f"⚠️  Could not save run status: {e}")


def load_run_status() -> Dict[str, Any]:
    """Load the last run status."""
    try:
        if STATUS_FILE.exists():
            return json.loads(STATUS_FILE.read_text())
    except Exception:
        pass
    return {"success": None, "timestamp": None, "details": "No previous run recorded"}


# ─── Individual Checks ───

def check_api_mmi() -> Dict[str, Any]:
    """Check if MMI API is reachable and returning valid data."""
    if not MMI_API:
        return {"name": "MMI API", "status": Status.SKIP.value, "detail": "Not configured (MMI_API not set in .env)"}
    try:
        start = time.time()
        resp = requests.get(MMI_API, timeout=10, headers={
            "User-Agent": "RPi_market/healthcheck"
        })
        latency_ms = round((time.time() - start) * 1000)
        resp.raise_for_status()
        data = resp.json()

        if data.get("success"):
            return {
                "name": "MMI API",
                "status": Status.OK.value,
                "latency_ms": latency_ms,
                "detail": f"MMI={data['data']['currentValue']:.1f}, Nifty={data['data']['nifty']}",
            }
        return {
            "name": "MMI API",
            "status": Status.WARN.value,
            "latency_ms": latency_ms,
            "detail": "API returned success=false",
        }
    except requests.Timeout:
        return {"name": "MMI API", "status": Status.FAIL.value, "detail": "Timeout (>10s)"}
    except Exception as e:
        return {"name": "MMI API", "status": Status.FAIL.value, "detail": str(e)}


def check_api_quotes() -> Dict[str, Any]:
    """Check if Quotes API is reachable with a test ticker."""
    if not QUOTES_API:
        return {"name": "Quotes API", "status": Status.SKIP.value, "detail": "Not configured (QUOTES_API not set in .env)"}
    try:
        start = time.time()
        resp = requests.get(QUOTES_API, params={"sids": "RELI"}, timeout=10, headers={
            "User-Agent": "RPi_market/healthcheck"
        })
        latency_ms = round((time.time() - start) * 1000)
        resp.raise_for_status()
        data = resp.json()

        quotes = data.get("data", [])
        if quotes:
            q = quotes[0]
            return {
                "name": "Quotes API",
                "status": Status.OK.value,
                "latency_ms": latency_ms,
                "detail": f"RELI=₹{q.get('price', 'N/A')}",
            }
        return {
            "name": "Quotes API",
            "status": Status.WARN.value,
            "latency_ms": latency_ms,
            "detail": "API returned empty data",
        }
    except requests.Timeout:
        return {"name": "Quotes API", "status": Status.FAIL.value, "detail": "Timeout (>10s)"}
    except Exception as e:
        return {"name": "Quotes API", "status": Status.FAIL.value, "detail": str(e)}


def check_telegram() -> Dict[str, Any]:
    """Check Telegram bot token validity and chat reachability."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            "name": "Telegram",
            "status": Status.SKIP.value,
            "detail": "Not configured (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing in .env)",
        }
    if TELEGRAM_BOT_TOKEN == "your_bot_token_here":
        return {
            "name": "Telegram",
            "status": Status.WARN.value,
            "detail": "Still using placeholder token — update .env",
        }
    try:
        start = time.time()
        resp = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe",
            timeout=10,
        )
        latency_ms = round((time.time() - start) * 1000)
        data = resp.json()

        if data.get("ok"):
            bot_name = data["result"].get("username", "unknown")
            return {
                "name": "Telegram",
                "status": Status.OK.value,
                "latency_ms": latency_ms,
                "detail": f"Bot @{bot_name} is active, chat_id={TELEGRAM_CHAT_ID}",
            }
        return {
            "name": "Telegram",
            "status": Status.FAIL.value,
            "latency_ms": latency_ms,
            "detail": f"Bot token invalid: {data.get('description', 'unknown error')}",
        }
    except Exception as e:
        return {"name": "Telegram", "status": Status.FAIL.value, "detail": str(e)}


def check_email() -> Dict[str, Any]:
    """Check SMTP server connectivity."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return {
            "name": "Email (SMTP)",
            "status": Status.SKIP.value,
            "detail": "Not configured (EMAIL_SENDER / EMAIL_PASSWORD missing in .env)",
        }
    if EMAIL_PASSWORD == "your_gmail_app_password":
        return {
            "name": "Email (SMTP)",
            "status": Status.WARN.value,
            "detail": "Still using placeholder password — update .env",
        }
    try:
        start = time.time()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        latency_ms = round((time.time() - start) * 1000)
        return {
            "name": "Email (SMTP)",
            "status": Status.OK.value,
            "latency_ms": latency_ms,
            "detail": f"SMTP login OK — {EMAIL_SENDER} via {SMTP_SERVER}:{SMTP_PORT}",
        }
    except smtplib.SMTPAuthenticationError:
        return {
            "name": "Email (SMTP)",
            "status": Status.FAIL.value,
            "detail": "Authentication failed — check EMAIL_PASSWORD (use Gmail App Password)",
        }
    except socket.timeout:
        return {"name": "Email (SMTP)", "status": Status.FAIL.value, "detail": f"Timeout connecting to {SMTP_SERVER}:{SMTP_PORT}"}
    except Exception as e:
        return {"name": "Email (SMTP)", "status": Status.FAIL.value, "detail": str(e)}


def check_last_run() -> Dict[str, Any]:
    """Check the last successful run status."""
    status = load_run_status()

    if status["timestamp"] is None:
        return {
            "name": "Last Run",
            "status": Status.WARN.value,
            "detail": "No previous run recorded — run `python main.py --test` first",
        }

    try:
        last_run = datetime.fromisoformat(status["timestamp"])
        age_hours = (datetime.now() - last_run).total_seconds() / 3600

        if not status["success"]:
            return {
                "name": "Last Run",
                "status": Status.FAIL.value,
                "detail": f"Last run FAILED at {status['timestamp']} — {status.get('details', '')}",
            }

        if age_hours > 26:  # More than 26 hours (missed a day)
            return {
                "name": "Last Run",
                "status": Status.WARN.value,
                "detail": f"Last success {age_hours:.0f}h ago ({status['timestamp']}) — may have missed a run",
            }

        return {
            "name": "Last Run",
            "status": Status.OK.value,
            "detail": f"Last success {age_hours:.1f}h ago ({status['timestamp']})",
        }
    except Exception as e:
        return {"name": "Last Run", "status": Status.WARN.value, "detail": str(e)}


def check_system() -> Dict[str, Any]:
    """Basic system health info."""
    try:
        import shutil
        disk = shutil.disk_usage("/")
        disk_free_gb = disk.free / (1024**3)
        disk_pct = (disk.used / disk.total) * 100

        info = (
            f"Python {platform.python_version()} | "
            f"{platform.system()} {platform.machine()} | "
            f"Disk: {disk_free_gb:.1f}GB free ({disk_pct:.0f}% used)"
        )

        status = Status.OK.value
        if disk_pct > 90:
            status = Status.WARN.value
            info += " ⚠️ LOW DISK"

        return {"name": "System", "status": status, "detail": info}
    except Exception as e:
        return {"name": "System", "status": Status.WARN.value, "detail": str(e)}


# ─── Full Health Check ───

def run_health_check() -> Dict[str, Any]:
    """Run all health checks and return a structured report."""
    checks = [
        check_api_mmi(),
        check_api_quotes(),
        check_telegram(),
        check_email(),
        check_last_run(),
        check_system(),
    ]

    # Overall status
    statuses = [c["status"] for c in checks]
    if Status.FAIL.value in statuses:
        overall = Status.FAIL.value
    elif Status.WARN.value in statuses:
        overall = Status.WARN.value
    else:
        overall = Status.OK.value

    return {
        "status": overall,
        "timestamp": datetime.now().isoformat(),
        "service": "RPi Market Notifier",
        "checks": checks,
    }


def print_health_report(report: Dict[str, Any]):
    """Pretty-print health check results to terminal."""
    icons = {
        "ok": "✅",
        "warn": "⚠️ ",
        "fail": "❌",
        "skip": "⏭️ ",
    }

    print()
    print("╔══════════════════════════════════════════╗")
    print("║    🏥  RPi Market — Health Check         ║")
    print("╚══════════════════════════════════════════╝")
    print()

    for check in report["checks"]:
        icon = icons.get(check["status"], "❓")
        latency = f" ({check['latency_ms']}ms)" if "latency_ms" in check else ""
        print(f"  {icon} {check['name']}{latency}")
        print(f"     └─ {check['detail']}")
        print()

    overall_icon = icons.get(report["status"], "❓")
    print(f"  ─────────────────────────────────────")
    print(f"  {overall_icon} Overall: {report['status'].upper()}")
    print(f"  🕐 {report['timestamp']}")
    print()


# ─── Telegram Heartbeat ───

def format_heartbeat_message(report: Dict[str, Any]) -> str:
    """Format a compact heartbeat message for Telegram."""
    icons = {"ok": "✅", "warn": "⚠️", "fail": "❌", "skip": "⏭️"}
    overall_icon = icons.get(report["status"], "❓")

    ts = datetime.now().strftime("%H:%M:%S")
    date_str = datetime.now().strftime("%d %b %Y")

    lines = [
        f"💓 *Heartbeat* — {date_str} {ts}",
        f"{overall_icon} Status: *{report['status'].upper()}*",
        "",
    ]

    for check in report["checks"]:
        icon = icons.get(check["status"], "❓")
        latency = f" `{check['latency_ms']}ms`" if "latency_ms" in check else ""
        lines.append(f"{icon} {check['name']}{latency}: {check['detail']}")

    # Add last run info inline
    last_run = load_run_status()
    if last_run["timestamp"]:
        try:
            lr_time = datetime.fromisoformat(last_run["timestamp"])
            age_h = (datetime.now() - lr_time).total_seconds() / 3600
            lr_status = "✅" if last_run["success"] else "❌"
            lines.append("")
            lines.append(f"📋 Last report: {lr_status} {age_h:.1f}h ago")
        except Exception:
            pass

    lines.append("")
    lines.append(f"🤖 _RPi Market Notifier_")

    return "\n".join(lines)


def send_heartbeat_telegram():
    """Run health check and send heartbeat to Telegram."""
    if not HEARTBEAT_ENABLED:
        print("💓 Heartbeat disabled in settings.")
        return

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("💓 Heartbeat skipped — Telegram not configured.")
        return

    try:
        report = run_health_check()
        message = format_heartbeat_message(report)

        from notifications.telegram_notifier import send_telegram
        send_telegram(message)

        status = report["status"].upper()
        print(f"💓 Heartbeat sent to Telegram — {status}")
    except Exception as e:
        print(f"💓 Heartbeat failed: {e}")


# ─── HTTP Health Endpoint ───

class HealthHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for /health endpoint."""

    def do_GET(self):
        if self.path in ("/health", "/", "/healthz", "/status"):
            report = run_health_check()
            status_code = 200 if report["status"] != Status.FAIL.value else 503
            body = json.dumps(report, indent=2).encode()

            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.write(body)
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found. Use /health"}).encode())

    def write(self, body: bytes):
        self.wfile.write(body)

    def log_message(self, format, *args):
        """Suppress default logging; use custom format."""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] {args[0]}")


def start_health_server(port: int = 8080):
    """Start the HTTP health check server."""
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"🏥 Health check server running on http://0.0.0.0:{port}/health")
    print(f"   Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Health server stopped.")
        server.server_close()


# ─── CLI ───

def main():
    parser = argparse.ArgumentParser(description="RPi Market — Health Check")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start HTTP health endpoint server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP health server (default: 8080)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output health report as JSON",
    )
    args = parser.parse_args()

    if args.serve:
        start_health_server(port=args.port)
    else:
        report = run_health_check()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_health_report(report)
        # Exit code: 0 = ok, 1 = fail, 2 = warn
        if report["status"] == Status.FAIL.value:
            sys.exit(1)
        elif report["status"] == Status.WARN.value:
            sys.exit(2)


if __name__ == "__main__":
    main()


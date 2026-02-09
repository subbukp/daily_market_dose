from datetime import datetime
from typing import Dict


def _arrow(val: float) -> str:
    """Return colored arrow indicator for a percentage value."""
    if val > 0:
        return f"🟢 +{val}%"
    elif val < 0:
        return f"🔴 {val}%"
    return "⚪ 0%"


def _format_volume(vol: int) -> str:
    """Format volume in Indian numbering (Cr / L / K)."""
    if vol >= 1_00_00_000:   # 1 Crore
        return f"{vol / 1_00_00_000:.2f} Cr"
    elif vol >= 1_00_000:    # 1 Lakh
        return f"{vol / 1_00_000:.2f} L"
    elif vol >= 1000:
        return f"{vol / 1000:.1f}K"
    return str(vol)


def _format_turnover(turnover: float) -> str:
    """Format turnover in readable units."""
    if turnover >= 1_00_00_00_000:   # 100 Cr
        return f"₹{turnover / 1_00_00_00_000:.2f} Cr"
    elif turnover >= 1_00_00_000:     # 1 Cr
        return f"₹{turnover / 1_00_00_000:.2f} Cr"
    elif turnover >= 1_00_000:        # 1 Lakh
        return f"₹{turnover / 1_00_000:.2f} L"
    return f"₹{turnover:,.0f}"


def _format_fii(fii: float) -> str:
    """Format FII flow (API value is in lakhs)."""
    cr = fii / 100
    if cr < 0:
        return f"🔴 ₹{abs(cr):,.0f} Cr (outflow)"
    return f"🟢 ₹{cr:,.0f} Cr (inflow)"


def format_telegram_report(data: Dict) -> str:
    """Format a rich Telegram message with market data."""
    mmi = data["mmi"]
    quotes = data["quotes"]
    ts = data["timestamp"]
    lines = []

    lines.append("📊 *Daily Market Report*")
    lines.append(f"📅 {datetime.now().strftime('%A, %B %d %Y')}")
    lines.append("")

    # ─── MMI Section ───
    if mmi:
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append(f"🧭 *Market Mood Index*: {mmi.mood}")
        lines.append(f"   Value: *{mmi.value}* / 100")
        day_delta = mmi.day_change
        arrow = "🟢 +" if day_delta >= 0 else "🔴 "
        lines.append(f"   Day Δ: {arrow}{day_delta} pts")
        lines.append(f"   Nifty: {mmi.nifty:,.2f}  |  VIX: {mmi.vix}")
        lines.append(f"   FII: {_format_fii(mmi.fii)}")
        lines.append(f"   Gold: ₹{mmi.gold:,}")
        lines.append("")
        lines.append(f"   📆 Last Week MMI: {mmi.last_week_value}")
        lines.append(f"   📆 Last Month MMI: {mmi.last_month_value}")
        lines.append(f"   📆 Last Year MMI: {mmi.last_year_value}")
        lines.append("")

    # ─── Quotes Section ───
    if quotes:
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("📈 *Stock Quotes*")
        lines.append("")

        for q in quotes:
            lines.append(f"*{q.name}* (`{q.sid}`)")
            lines.append(f"  💰 ₹{q.price:,.2f}  ({_arrow(q.day_change_pct)})")
            lines.append(f"  📊 Vol: {_format_volume(q.volume)} | TO: {_format_turnover(q.turnover)}")
            lines.append(f"  🔼 H: ₹{q.high:,.2f} | 🔽 L: ₹{q.low:,.2f}")
            lines.append(f"  📅 Wk: {_arrow(q.week_change_pct)} | Mo: {_arrow(q.month_change_pct)}")
            lines.append(f"  📐 52W: ₹{q.low_52w:,} — ₹{q.high_52w:,} ({q.away_52w_high:.1f}% from high)")
            lines.append("")

    # ─── IPO Section ───
    ipos = data.get("ipos", [])
    open_ipos = [i for i in ipos if i.is_open]
    upcoming_ipos = [i for i in ipos if i.is_upcoming]

    if open_ipos or upcoming_ipos:
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("🏷️ *IPO Watch*")
        lines.append("")

        if open_ipos:
            lines.append("🟢 *Open Now*")
            for ipo in open_ipos:
                lines.append(f"  *{ipo.company}*")
                lines.append(f"  💰 ₹{ipo.price_range} | Size: ₹{ipo.issue_size_cr} Cr")
                lines.append(f"  📅 {ipo.open_date} → {ipo.close_date}")
                lines.append(f"  🏛️ {ipo.listing_at} | Listing: {ipo.listing_date}")
                lines.append("")

        if upcoming_ipos:
            lines.append("🔜 *Upcoming*")
            for ipo in upcoming_ipos:
                lines.append(f"  *{ipo.company}*")
                lines.append(f"  💰 ₹{ipo.price_range} | Size: ₹{ipo.issue_size_cr} Cr")
                lines.append(f"  📅 Opens: {ipo.open_date}")
                lines.append(f"  🏛️ {ipo.listing_at}")
                lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append(f"⏰ _Generated at {ts}_")

    return "\n".join(lines)


def format_email_report(data: Dict) -> str:
    """Format an HTML email with market data."""
    mmi = data["mmi"]
    quotes = data["quotes"]
    ts = data["timestamp"]

    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background: #f9f9f9; }}
    .container {{ max-width: 700px; margin: 0 auto; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    h2 {{ color: #1a1a2e; border-bottom: 2px solid #e94560; padding-bottom: 8px; }}
    h3 {{ color: #16213e; margin-top: 24px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
    th {{ background: #16213e; color: white; padding: 10px 8px; text-align: left; font-size: 13px; }}
    td {{ padding: 8px; border-bottom: 1px solid #eee; font-size: 13px; }}
    tr:hover {{ background: #f5f5f5; }}
    .green {{ color: #27ae60; font-weight: bold; }}
    .red {{ color: #e74c3c; font-weight: bold; }}
    .footer {{ color: #999; font-size: 11px; margin-top: 20px; text-align: center; }}
    .mmi-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-weight: bold; }}
</style>
</head>
<body>
<div class="container">
    <h2>📊 Daily Market Report — {datetime.now().strftime('%A, %B %d %Y')}</h2>
"""

    if mmi:
        mood_color = "#e74c3c" if mmi.value < 40 else "#27ae60" if mmi.value > 60 else "#f39c12"
        html += f"""
    <h3>🧭 Market Mood Index</h3>
    <p><span class="mmi-badge" style="background:{mood_color}20; color:{mood_color};">{mmi.mood} — {mmi.value}/100</span></p>
    <table>
        <tr><td><b>Nifty</b></td><td>{mmi.nifty:,.2f}</td><td><b>VIX</b></td><td>{mmi.vix}</td></tr>
        <tr><td><b>FII Flow</b></td><td>{_format_fii(mmi.fii)}</td><td><b>Gold</b></td><td>₹{mmi.gold:,}</td></tr>
        <tr><td><b>Yesterday</b></td><td>{mmi.last_day_value}</td><td><b>Last Week</b></td><td>{mmi.last_week_value}</td></tr>
        <tr><td><b>Last Month</b></td><td>{mmi.last_month_value}</td><td><b>Last Year</b></td><td>{mmi.last_year_value}</td></tr>
    </table>
"""

    if quotes:
        html += """
    <h3>📈 Stock Quotes</h3>
    <table>
    <tr>
        <th>Stock</th><th>Price (₹)</th><th>Day %</th>
        <th>Week %</th><th>Month %</th><th>Volume</th><th>52W Range</th>
    </tr>
"""
        for q in quotes:
            css_class = "green" if q.day_change_pct >= 0 else "red"
            wk_class = "green" if q.week_change_pct >= 0 else "red"
            mn_class = "green" if q.month_change_pct >= 0 else "red"
            html += f"""
    <tr>
        <td><b>{q.name}</b><br><small style="color:#999">{q.sid}</small></td>
        <td>₹{q.price:,.2f}</td>
        <td class="{css_class}">{q.day_change_pct:+.2f}%</td>
        <td class="{wk_class}">{q.week_change_pct:+.2f}%</td>
        <td class="{mn_class}">{q.month_change_pct:+.2f}%</td>
        <td>{_format_volume(q.volume)}</td>
        <td>₹{q.low_52w:,} — ₹{q.high_52w:,}</td>
    </tr>
"""
        html += "    </table>"

    # ─── IPO Section ───
    ipos = data.get("ipos", [])
    open_ipos = [i for i in ipos if i.is_open]
    upcoming_ipos = [i for i in ipos if i.is_upcoming]

    if open_ipos or upcoming_ipos:
        html += """
    <h3>🏷️ IPO Watch</h3>
    <table>
    <tr>
        <th>Status</th><th>Company</th><th>Price (₹)</th>
        <th>Size (Cr)</th><th>Open</th><th>Close</th><th>Listing</th><th>Exchange</th>
    </tr>
"""
        for ipo in open_ipos + upcoming_ipos:
            status_badge = (
                '<span style="color:#27ae60;font-weight:bold">🟢 Open</span>'
                if ipo.is_open
                else '<span style="color:#f39c12;font-weight:bold">🔜 Upcoming</span>'
            )
            html += f"""
    <tr>
        <td>{status_badge}</td>
        <td><b>{ipo.company}</b></td>
        <td>₹{ipo.price_range}</td>
        <td>₹{ipo.issue_size_cr}</td>
        <td>{ipo.open_date}</td>
        <td>{ipo.close_date}</td>
        <td>{ipo.listing_date}</td>
        <td>{ipo.listing_at}</td>
    </tr>
"""
        html += "    </table>"

    html += f"""
    <p class="footer">⏰ Generated at {ts} | RPi Market Notifier</p>
</div>
</body>
</html>"""

    return html



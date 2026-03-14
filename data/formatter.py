from datetime import datetime
from typing import Dict

from data.summary import generate_summary


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

    # ─── Summary / Insights ───
    insights = generate_summary(data)
    if insights:
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("🧠 *Market Insights*")
        lines.append("")
        for insight in insights:
            lines.append(f"• {insight}")
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

    # ─── US Fear & Greed ───
    us_fg = data.get("us_fg")
    if us_fg:
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append(f"🇺🇸 *US Fear & Greed*: {us_fg.mood}")
        lines.append(f"   Value: *{us_fg.score:.0f}* / 100")
        day_delta = us_fg.day_change
        arrow = "🟢 +" if day_delta >= 0 else "🔴 "
        lines.append(f"   Day Δ: {arrow}{day_delta} pts")
        lines.append("")

        # Sub-indicators (compact)
        for name, ind in us_fg.sub_indicators:
            lines.append(f"   {ind.emoji} {name}: {ind.score:.0f}")
        lines.append("")

        lines.append(f"   📆 Last Week: {us_fg.previous_1_week:.0f}")
        lines.append(f"   📆 Last Month: {us_fg.previous_1_month:.0f}")
        lines.append(f"   📆 Last Year: {us_fg.previous_1_year:.0f}")
        lines.append("")

    # ─── Precious Metals Section ───
    metals = data.get("metals")
    if metals:
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("🪙 *Precious Metals*")
        lines.append("")

        for m in metals.metals:
            sign = "+" if m.change >= 0 else ""
            lines.append(f"  {m.direction_emoji} *{m.commodity}*: ${m.price:,.2f} ({sign}{m.change_pct:.2f}%)")

        # Gold/Silver ratio
        ratio = metals.gold_silver_ratio
        if ratio:
            signal = metals.gold_silver_signal
            lines.append("")
            lines.append(f"  ⚖️ *Au/Ag Ratio*: {ratio:.1f} {signal}")

        lines.append("")

    # ─── Quotes Section ───
    if quotes:
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("📈 *Stock Quotes*")
        lines.append("")

        for q in quotes:
            lines.append(f"*{q.name}* (`{q.sid}`)")
            lines.append(f"  💰 ₹{q.price:,.2f}  ({_arrow(q.day_change_pct)})")
            lines.append(f"  📅 Wk: {_arrow(q.week_change_pct)} | Mo: {_arrow(q.month_change_pct)}")
            lines.append(f"  📐 52W: ₹{q.low_52w:,} — ₹{q.high_52w:,} ({q.away_52w_high:.1f}% from high)")
            lines.append("")

    # ─── IPO Section ───
    ipos = data.get("ipos", [])
    if ipos:
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("🏷️ *IPO Watch*")
        lines.append("")

        for ipo in ipos:
            lines.append(f"{ipo.status_emoji} *{ipo.company}* ({ipo.category})")
            lines.append(f"  📊 GMP: {ipo.gmp_display} | {ipo.fire_display}")
            lines.append(f"  💰 ₹{ipo.price} | Size: ₹{ipo.issue_size_cr} Cr | Lot: {ipo.lot_size}")
            lines.append(f"  📅 {ipo.open_date} → {ipo.close_date} | List: {ipo.listing_date}")
            sub_str = f"Sub: {ipo.subscription}" if ipo.subscription and ipo.subscription != "-" else ""
            pe_str = f"P/E: {ipo.pe_ratio}" if ipo.pe_ratio != "N/A" else ""
            anchor_str = f"Anchor: {ipo.anchor_display}"
            extra = " | ".join(filter(None, [sub_str, pe_str, anchor_str]))
            if extra:
                lines.append(f"  📋 {extra}")
            lines.append("")

    # ─── NCD IPO Section ───
    ncds = data.get("ncds", [])
    if ncds:
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("📜 *NCD IPO Watch*")
        lines.append("")

        for ncd in ncds:
            lines.append(f"🟢 *{ncd.company}*")
            lines.append(f"  ⭐ {ncd.credit_rating} | Closes: {ncd.close_date}")
            lines.append(f"  📈 Best Yield: *{ncd.best_yield:.2f}%*")
            lines.append("")

            for s in ncd.series[:4]:
                sec_label = "🔒" if s.secured else "🔓"
                if s.coupon_rate > 0:
                    lines.append(f"    {sec_label} Series {s.series}: {s.yield_pct:.2f}% | {s.coupon_rate:.2f}% coupon | {s.tenure_display} | {s.interest_freq}")
                else:
                    lines.append(f"    {sec_label} Series {s.series}: {s.yield_pct:.2f}% | {s.tenure_display} | Cumulative")
            if len(ncd.series) > 4:
                lines.append(f"    ... +{len(ncd.series) - 4} more series")
            lines.append("")

    # ─── Secondary Bonds Section ───
    bonds = data.get("bonds", [])
    if bonds:
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("🏦 *Secondary Bond Market*")
        lines.append(f"Top {len(bonds)} by yield:")
        lines.append("")

        for b in bonds:
            sec = "🔒" if b.secured else "🔓"
            lines.append(f"  *{b.name}*")
            lines.append(f"  📈 Yield: *{b.yield_display}* | Coupon: {b.coupon_display}")
            lines.append(f"  ⭐ {b.credit_rating} | {b.interest_freq} | {sec} | Mat: {b.maturity_date}")
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

    # ─── Summary / Insights ───
    insights = generate_summary(data)
    if insights:
        html += """
    <div style="background:#f0f8ff; border-left:4px solid #2196F3; padding:12px 16px; margin:12px 0; border-radius:4px;">
    <h3 style="margin:0 0 8px 0; color:#1565C0;">🧠 Market Insights</h3>
    <ul style="margin:0; padding-left:20px; line-height:1.8;">
"""
        for insight in insights:
            # Strip markdown bold for HTML
            clean = insight.replace("*", "<b>", 1).replace("*", "</b>", 1)
            while "*" in clean:
                clean = clean.replace("*", "<b>", 1).replace("*", "</b>", 1)
            html += f"    <li>{clean}</li>\n"
        html += """    </ul>
    </div>
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

    # ─── US Fear & Greed ───
    us_fg = data.get("us_fg")
    if us_fg:
        us_color = "#e74c3c" if us_fg.score < 40 else "#27ae60" if us_fg.score > 60 else "#f39c12"
        html += f"""
    <h3>🇺🇸 US Fear & Greed Index</h3>
    <p><span class="mmi-badge" style="background:{us_color}20; color:{us_color};">{us_fg.mood} — {us_fg.score:.0f}/100</span></p>
    <table>
        <tr><th>Indicator</th><th>Score</th><th>Sentiment</th></tr>
"""
        for name, ind in us_fg.sub_indicators:
            ind_color = "#e74c3c" if ind.score < 40 else "#27ae60" if ind.score > 60 else "#f39c12"
            html += f"""
        <tr><td>{name}</td><td style="color:{ind_color};font-weight:bold">{ind.score:.0f}</td><td>{ind.emoji} {ind.rating.title()}</td></tr>
"""
        html += f"""
    </table>
    <small>📆 Prev Close: {us_fg.previous_close:.0f} | Week: {us_fg.previous_1_week:.0f} | Month: {us_fg.previous_1_month:.0f} | Year: {us_fg.previous_1_year:.0f}</small>
"""

    # ─── Precious Metals Section ───
    metals = data.get("metals")
    if metals:
        ratio = metals.gold_silver_ratio
        signal = metals.gold_silver_signal
        html += """
    <h3>🪙 Precious Metals</h3>
    <table>
    <tr><th>Metal</th><th>Price (USD)</th><th>Change</th><th>Trade</th><th>USD Effect</th></tr>
"""
        for m in metals.metals:
            chg_color = "green" if m.change_pct >= 0 else "red"
            sign = "+" if m.change >= 0 else ""
            html += f"""
    <tr>
        <td><b>{m.commodity}</b></td>
        <td>${m.price:,.2f}</td>
        <td class="{chg_color}">{sign}{m.change_pct:.2f}% (${sign}{m.change:.2f})</td>
        <td>{'+' if m.change_trade >= 0 else ''}{m.change_trade_pct:.2f}%</td>
        <td>{'+' if m.change_usd >= 0 else ''}{m.change_usd_pct:.2f}%</td>
    </tr>
"""
        html += "    </table>"
        if ratio:
            html += f"""
    <p style="margin-top:8px;">⚖️ <b>Gold/Silver Ratio</b>: {ratio:.1f} — {signal}</p>
"""

    if quotes:
        html += """
    <h3>📈 Stock Quotes</h3>
    <table>
    <tr>
        <th>Stock</th><th>Price (₹)</th><th>Day %</th>
        <th>Week %</th><th>Month %</th><th>52W Range</th>
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
        <td>₹{q.low_52w:,} — ₹{q.high_52w:,}</td>
    </tr>
"""
        html += "    </table>"

    # ─── IPO Section ───
    ipos = data.get("ipos", [])
    if ipos:
        html += """
    <h3>🏷️ IPO Watch</h3>
    <table>
    <tr>
        <th>Status</th><th>Company</th><th>GMP</th><th>Rating</th>
        <th>Price (₹)</th><th>Size (Cr)</th><th>Sub</th><th>P/E</th>
        <th>Open</th><th>Close</th><th>Listing</th><th>Anchor</th>
    </tr>
"""
        for ipo in ipos:
            status_badge = (
                '<span style="color:#27ae60;font-weight:bold">🟢 Open</span>'
                if ipo.is_open
                else '<span style="color:#f39c12;font-weight:bold">🔜 Upcoming</span>'
                if ipo.is_upcoming
                else '<span style="color:#999">Closed</span>'
            )
            gmp_color = "#27ae60" if ipo.gmp_percent >= 20 else ("#f39c12" if ipo.gmp_percent > 0 else "#e74c3c")
            html += f"""
    <tr>
        <td>{status_badge}</td>
        <td><b>{ipo.company}</b><br><small style="color:#999">{ipo.category}</small></td>
        <td style="color:{gmp_color};font-weight:bold">{ipo.gmp_percent:+.1f}%<br><small>₹{ipo.gmp_value}</small></td>
        <td>{ipo.fire_display}</td>
        <td>₹{ipo.price}</td>
        <td>₹{ipo.issue_size_cr}</td>
        <td>{ipo.subscription}</td>
        <td>{ipo.pe_ratio}</td>
        <td>{ipo.open_date}</td>
        <td>{ipo.close_date}</td>
        <td>{ipo.listing_date}</td>
        <td>{ipo.anchor_display}</td>
    </tr>
"""
        html += "    </table>"

    # ─── NCD IPO Section ───
    ncds = data.get("ncds", [])
    if ncds:
        html += """
    <h3>📜 NCD IPO Watch</h3>
"""
        for ncd in ncds:
            html += f"""
    <p><b>{ncd.company}</b> — {ncd.credit_rating} | Closes: {ncd.close_date}<br>
    <small>📈 Best Yield: <b style="color:#27ae60">{ncd.best_yield:.2f}%</b></small></p>
    <table>
    <tr>
        <th>Series</th><th>Yield</th><th>Coupon</th>
        <th>Tenure</th><th>Freq</th><th>Secured</th>
    </tr>
"""
            for s in ncd.series:
                html += f"""
    <tr>
        <td><b>{s.series}</b></td>
        <td style="color:green;font-weight:bold">{s.yield_pct:.2f}%</td>
        <td>{f'{s.coupon_rate:.2f}%' if s.coupon_rate > 0 else '—'}</td>
        <td>{s.tenure_display}</td>
        <td>{s.interest_freq}</td>
        <td>{'🔒 Yes' if s.secured else '🔓 No'}</td>
    </tr>
"""
            html += "    </table>"

    # ─── Secondary Bonds Section ───
    bonds = data.get("bonds", [])
    if bonds:
        html += f"""
    <h3>🏦 Secondary Bond Market (Top {len(bonds)} by Yield)</h3>
    <table>
    <tr>
        <th>Issuer</th><th>Yield</th><th>Coupon</th>
        <th>Rating</th><th>Freq</th><th>Secured</th><th>Maturity</th>
    </tr>
"""
        for b in bonds:
            yield_color = "green" if b.yield_pct >= 10 else "inherit"
            html += f"""
    <tr>
        <td><b>{b.name}</b></td>
        <td style="color:{yield_color};font-weight:bold">{b.yield_display}</td>
        <td>{b.coupon_display}</td>
        <td>{b.credit_rating}</td>
        <td>{b.interest_freq}</td>
        <td>{'🔒 Yes' if b.secured else '🔓 No'}</td>
        <td>{b.maturity_date}</td>
    </tr>
"""
        html += "    </table>"

    html += f"""
    <p class="footer">⏰ Generated at {ts} | RPi Market Notifier</p>
</div>
</body>
</html>"""

    return html



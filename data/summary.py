"""
Market Summary — AI-like insights generated from all data sources.

Analyzes MMI, Gold/Silver ratio, bond yields, stock positions, FII flows
and generates actionable summary points.
"""

from typing import Dict, List
from datetime import datetime


def generate_summary(data: Dict) -> List[str]:
    """Generate smart summary insights from all market data."""
    insights = []

    mmi = data.get("mmi")
    metals = data.get("metals")
    quotes = data.get("quotes", [])
    bonds = data.get("bonds", [])
    ncds = data.get("ncds", [])
    ipos = data.get("ipos", [])

    # ─── 1. MMI-based Market Stance ───
    if mmi:
        v = mmi.value
        delta = mmi.day_change

        if v <= 20:
            insights.append(
                "🟢 *Extreme Fear* (MMI {:.0f}) — Strong accumulation zone. "
                "Markets are deeply fearful — historically the best time to buy quality stocks aggressively.".format(v)
            )
        elif v <= 32:
            insights.append(
                "🟢 *Fear Zone* (MMI {:.0f}) — Good time to add positions. "
                "Consider deploying cash into large-caps and index funds in a staggered manner.".format(v)
            )
        elif v <= 45:
            insights.append(
                "🟡 *Cautious Zone* (MMI {:.0f}) — Selective buying. "
                "Market recovering from fear — pick quality stocks but don't go all in.".format(v)
            )
        elif v <= 55:
            insights.append(
                "⚪ *Neutral* (MMI {:.0f}) — Market fairly valued. "
                "Hold current positions, add only on dips. No extreme action needed.".format(v)
            )
        elif v <= 65:
            insights.append(
                "🟡 *Mild Greed* (MMI {:.0f}) — Start getting cautious. "
                "Book partial profits on risky/momentum stocks. Avoid FOMO buying.".format(v)
            )
        elif v <= 75:
            insights.append(
                "🔴 *Greed Zone* (MMI {:.0f}) — Reduce risky positions. "
                "Markets are overheated — shift towards defensives, gold, or fixed income.".format(v)
            )
        else:
            insights.append(
                "🔴 *Extreme Greed* (MMI {:.0f}) — High risk of correction. "
                "Strongly consider booking profits and moving to cash/debt. Don't chase rallies.".format(v)
            )

        # MMI momentum
        if abs(delta) >= 10:
            direction = "surging up ↑" if delta > 0 else "dropping fast ↓"
            insights.append(
                f"⚡ MMI moved {delta:+.1f} pts today — sentiment {direction}. Watch for reversal."
            )

        # VIX signal
        if mmi.vix:
            vix = abs(mmi.vix)
            if vix > 20:
                insights.append("📊 VIX is elevated ({:.1f}) — expect higher volatility. Use limit orders.".format(vix))
            elif vix < 12:
                insights.append("📊 VIX is low ({:.1f}) — calm markets, good for systematic investing.".format(vix))

        # FII signal
        if mmi.fii:
            fii_cr = mmi.fii / 100
            if fii_cr < -1000:
                insights.append(
                    "💸 Heavy FII selling (₹{:,.0f} Cr outflow) — could create buying opportunities for long-term investors.".format(abs(fii_cr))
                )
            elif fii_cr > 500:
                insights.append(
                    "💰 Strong FII buying (₹{:,.0f} Cr inflow) — positive for market momentum.".format(fii_cr)
                )

    # ─── 1b. US Fear & Greed ───
    us_fg = data.get("us_fg")
    if us_fg:
        v = us_fg.score
        if v <= 25:
            insights.append(
                "🇺🇸 *US Extreme Fear* (F&G {:.0f}) — US markets deeply fearful. "
                "Could signal global risk-off — watch for contagion to Indian markets.".format(v)
            )
        elif v <= 40:
            insights.append(
                "🇺🇸 *US Fear* (F&G {:.0f}) — Cautious sentiment in US markets. "
                "May impact FII flows to India.".format(v)
            )
        elif v >= 75:
            insights.append(
                "🇺🇸 *US Extreme Greed* (F&G {:.0f}) — US markets overheated. "
                "Correction risk could spill over globally.".format(v)
            )

        # Divergence between India and US
        if mmi and abs(mmi.value - v) >= 25:
            if mmi.value > v:
                insights.append(
                    "⚡ India ({:.0f}) vs US ({:.0f}) sentiment divergence — India more greedy than US. Watch for convergence.".format(mmi.value, v)
                )
            else:
                insights.append(
                    "⚡ India ({:.0f}) vs US ({:.0f}) sentiment divergence — India more fearful than US. Could be a local buying opportunity.".format(mmi.value, v)
                )

    # ─── 2. Gold/Silver Ratio ───
    if metals:
        ratio = metals.gold_silver_ratio
        if ratio:
            if ratio >= 85:
                insights.append(
                    "🪙 Au/Ag ratio at *{:.1f}* — Silver is *highly undervalued*. "
                    "Consider allocating to silver (SGB/ETF). Historically this ratio mean-reverts.".format(ratio)
                )
            elif ratio >= 70:
                insights.append(
                    "🪙 Au/Ag ratio at *{:.1f}* — Silver is undervalued relative to gold. "
                    "Silver could outperform in the near term.".format(ratio)
                )
            elif ratio <= 50:
                insights.append(
                    "🪙 Au/Ag ratio at *{:.1f}* — Gold is undervalued vs silver. "
                    "Consider adding gold (SGB/Gold ETF) over silver.".format(ratio)
                )
            elif ratio <= 55:
                insights.append(
                    "🪙 Au/Ag ratio at *{:.1f}* — Silver is slightly overvalued. "
                    "Gold may be the better precious metals play right now.".format(ratio)
                )

        # Gold momentum
        gold = metals.gold
        if gold and gold.change_pct >= 2:
            insights.append(
                "⚠️ Gold surging +{:.1f}% today — risk-off sentiment. Be cautious on equities.".format(gold.change_pct)
            )

    # ─── 3. Fixed Income Opportunities ───
    if bonds:
        top_bond = bonds[0]
        if top_bond.yield_pct >= 11.4:
            insights.append(
                "🏦 *High yield alert*: {name} at *{y:.2f}%* yield ({rating}). "
                "Consider for fixed income allocation — attractive risk-adjusted return.".format(
                    name=top_bond.name, y=top_bond.yield_pct, rating=top_bond.credit_rating
                )
            )
        elif top_bond.yield_pct >= 10.5:
            insights.append(
                "🏦 Top secondary bond yield: *{:.2f}%* ({}) — decent fixed income opportunity.".format(
                    top_bond.yield_pct, top_bond.name
                )
            )

    if ncds:
        best_ncd = ncds[0]
        if best_ncd.best_yield >= 11:
            insights.append(
                "📜 *NCD IPO alert*: {name} offering *{y:.2f}%* yield ({rating}). "
                "Worth considering for debt portfolio.".format(
                    name=best_ncd.company, y=best_ncd.best_yield, rating=best_ncd.credit_rating
                )
            )

    # ─── 4. Stock-specific signals ───
    if quotes:
        # Stocks near 52-week low (within 10%)
        near_low = [q for q in quotes if q.away_52w_low <= 10 and q.away_52w_low > 0]
        if near_low:
            names = ", ".join(q.name for q in near_low)
            insights.append(
                f"📉 Near 52W low: *{names}* — potential value opportunity if fundamentals are intact."
            )

        # Stocks near 52-week high (within 5%)
        near_high = [q for q in quotes if q.away_52w_high <= 5]
        if near_high:
            names = ", ".join(q.name for q in near_high)
            insights.append(
                f"📈 Near 52W high: *{names}* — consider booking partial profits."
            )

        # Biggest day movers
        big_gainers = [q for q in quotes if q.day_change_pct >= 3]
        big_losers = [q for q in quotes if q.day_change_pct <= -3]
        if big_gainers:
            for q in big_gainers:
                insights.append(f"🚀 *{q.name}* up {q.day_change_pct:+.1f}% today — momentum play, watch for follow-through.")
        if big_losers:
            for q in big_losers:
                insights.append(f"💥 *{q.name}* down {q.day_change_pct:+.1f}% today — check for news before buying the dip.")

    # ─── 5. IPO signals ───
    if ipos:
        today = datetime.now()
        def _is_open(close_str: str) -> bool:
            try:
                close_dt = datetime.strptime(close_str, "%d-%b").replace(year=today.year)
                return close_dt >= today.replace(hour=0, minute=0, second=0, microsecond=0)
            except (ValueError, TypeError):
                return False
        hot_ipos = [i for i in ipos if i.gmp_percent >= 20 and _is_open(i.close_date)]
        if hot_ipos:
            names = ", ".join(i.company for i in hot_ipos)
            insights.append(f"🔥 Hot IPOs with 20%+ GMP: *{names}* — strong listing expected.")

    # ─── 6. Combined signals ───
    if mmi and metals:
        # Fear + Gold rally = classic risk-off
        gold = metals.gold
        if mmi.value < 35 and gold and gold.change_pct > 1:
            insights.append(
                "⚠️ Fear + Gold rally = classic risk-off. Stay defensive but watch for contrarian entry points."
            )
        # Greed + high VIX = potential top
        if mmi.value > 65 and mmi.vix and abs(mmi.vix) > 18:
            insights.append(
                "⚠️ Greed + elevated VIX = unstable rally. High chance of sharp pullback."
            )

    # Fallback
    if not insights:
        insights.append("📊 Markets are steady — no strong signals today. Continue with your investment plan.")

    return insights





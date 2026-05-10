import type { Metal } from "@/types/market";

const ICONS: Record<string, string> = {
  Gold: "🥇",
  Silver: "🥈",
  Platinum: "⚪",
};

export default function MetalsCard({ metals }: { metals: Metal[] }) {
  return (
    <div className="rounded-xl bg-white border border-slate-200 shadow-sm overflow-hidden">
      <div className="border-b border-slate-100 bg-slate-50 px-5 py-3 flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">Precious Metals</h2>
        {metals[0] && (
          <span className="text-xs text-slate-400">{metals[0].time} · {metals[0].currency}</span>
        )}
      </div>
      <div className="divide-y divide-slate-50">
        {metals.map((m) => {
          const isUp = m.change_pct >= 0;
          return (
            <div key={m.commodity} className="flex items-center justify-between px-5 py-4">
              <div className="flex items-center gap-3">
                <span className="text-xl">{ICONS[m.commodity] ?? "🔘"}</span>
                <div>
                  <p className="font-semibold text-slate-900">{m.commodity}</p>
                  <p className="text-xs text-slate-400">
                    {isUp ? "▲" : "▼"} {Math.abs(m.change_usd).toFixed(2)} USD ({Math.abs(m.change_usd_pct).toFixed(2)}%)
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-slate-900">
                  ₹{m.price.toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                </p>
                <p className={`text-sm font-semibold ${isUp ? "text-emerald-600" : "text-red-500"}`}>
                  {isUp ? "+" : ""}{m.change_pct.toFixed(2)}%
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

import type { Ipo } from "@/types/market";

const statusStyles: Record<string, string> = {
  O: "bg-emerald-100 text-emerald-700",
  U: "bg-amber-100 text-amber-700",
  C: "bg-slate-100 text-slate-500",
};

const statusLabel: Record<string, string> = {
  O: "Open",
  U: "Upcoming",
  C: "Closed",
};

export default function IpoTable({ ipos }: { ipos: Ipo[] }) {
  if (!ipos.length) {
    return (
      <div className="rounded-xl bg-white border border-slate-200 p-10 text-center text-sm text-slate-400 shadow-sm">
        No IPOs match the current filters (GMP ≥ 20%, rating ≥ 🔥🔥, open only).
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl bg-white shadow-sm border border-slate-200">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            {[
              "Company",
              "Category",
              "Status",
              "Price (₹)",
              "GMP",
              "Subscription",
              "Rating",
              "Open",
              "Close",
              "Listing",
              "Size (₹ Cr)",
              "Lot",
              "P/E",
              "Anchor",
            ].map((h) => (
              <th
                key={h}
                className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 whitespace-nowrap"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ipos.map((ipo, i) => (
            <tr
              key={`${ipo.company}-${ipo.open_date}`}
              className={`border-b border-slate-50 transition-colors hover:bg-slate-50 ${
                i % 2 === 0 ? "bg-white" : "bg-slate-50/40"
              }`}
            >
              <td className="px-4 py-3.5 font-medium text-slate-900 max-w-[200px]">
                <span className="line-clamp-1" title={ipo.company}>{ipo.company}</span>
              </td>
              <td className="px-4 py-3.5">
                <span className="rounded-full bg-violet-50 px-2.5 py-0.5 text-xs font-semibold text-violet-700">
                  {ipo.category}
                </span>
              </td>
              <td className="px-4 py-3.5">
                <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${statusStyles[ipo.status] ?? statusStyles.C}`}>
                  {statusLabel[ipo.status] ?? ipo.status}
                </span>
              </td>
              <td className="px-4 py-3.5 font-medium text-slate-800">{ipo.price}</td>
              <td className="px-4 py-3.5 whitespace-nowrap">
                <span className={ipo.gmp_percent > 0 ? "text-emerald-600 font-semibold" : ipo.gmp_percent < 0 ? "text-red-500 font-semibold" : "text-slate-400"}>
                  {ipo.gmp_percent > 0 ? "+" : ""}{ipo.gmp_percent.toFixed(1)}%
                </span>
                <span className="ml-1 text-xs text-slate-400">(₹{ipo.gmp_value})</span>
              </td>
              <td className="px-4 py-3.5 text-slate-700">{ipo.subscription}</td>
              <td className="px-4 py-3.5">{ipo.fire_display || "—"}</td>
              <td className="px-4 py-3.5 text-slate-600 whitespace-nowrap">{ipo.open_date}</td>
              <td className="px-4 py-3.5 text-slate-600 whitespace-nowrap">{ipo.close_date}</td>
              <td className="px-4 py-3.5 text-slate-600 whitespace-nowrap">{ipo.listing_date}</td>
              <td className="px-4 py-3.5 text-slate-700">{ipo.issue_size_cr}</td>
              <td className="px-4 py-3.5 text-slate-700">{ipo.lot_size}</td>
              <td className="px-4 py-3.5 text-slate-700">{ipo.pe_ratio}</td>
              <td className="px-4 py-3.5 text-center">
                {ipo.has_anchor ? (
                  <span className="text-emerald-500 font-bold">✓</span>
                ) : (
                  <span className="text-slate-300">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

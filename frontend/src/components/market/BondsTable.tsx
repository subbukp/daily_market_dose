import type { Bond } from "@/types/market";

export default function BondsTable({ bonds }: { bonds: Bond[] }) {
  if (!bonds.length) {
    return (
      <div className="rounded-xl bg-white border border-slate-200 p-10 text-center text-sm text-slate-400 shadow-sm">
        No bonds data available.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl bg-white shadow-sm border border-slate-200">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            {["Issuer", "ISIN", "Rating", "Yield", "Coupon", "Price (₹)", "Maturity", "Frequency", "Secured"].map(
              (h) => (
                <th
                  key={h}
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 whitespace-nowrap"
                >
                  {h}
                </th>
              )
            )}
          </tr>
        </thead>
        <tbody>
          {bonds.map((bond, i) => (
            <tr
              key={bond.isin}
              className={`border-b border-slate-50 transition-colors hover:bg-slate-50 ${
                i % 2 === 0 ? "bg-white" : "bg-slate-50/40"
              }`}
            >
              <td className="px-4 py-3.5 font-medium text-slate-900 max-w-[220px]">
                <span className="line-clamp-1" title={bond.name}>{bond.name}</span>
              </td>
              <td className="px-4 py-3.5 font-mono text-xs text-slate-400">{bond.isin}</td>
              <td className="px-4 py-3.5">
                <span className="inline-flex items-center rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 whitespace-nowrap">
                  {bond.credit_rating}
                </span>
              </td>
              <td className="px-4 py-3.5 text-right">
                <span className="font-bold text-emerald-600">{bond.yield_display}</span>
              </td>
              <td className="px-4 py-3.5 text-right text-slate-600">{bond.coupon_display}</td>
              <td className="px-4 py-3.5 text-right text-slate-700">
                {bond.price.toLocaleString("en-IN")}
              </td>
              <td className="px-4 py-3.5 text-slate-600 whitespace-nowrap">{bond.maturity_date}</td>
              <td className="px-4 py-3.5 text-slate-600">{bond.interest_freq}</td>
              <td className="px-4 py-3.5">
                <span
                  className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                    bond.secured
                      ? "bg-emerald-50 text-emerald-700"
                      : "bg-amber-50 text-amber-700"
                  }`}
                >
                  {bond.secured ? "Secured" : "Unsecured"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

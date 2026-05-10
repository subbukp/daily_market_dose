// eslint-disable-next-line @typescript-eslint/no-explicit-any
export default function CompanyHeader({ companyId, details, price }: { companyId: number; details: any; price: any }) {
  const name: string = details?.companyName ?? details?.name ?? `Company #${companyId}`;
  const sector: string = details?.sectorName ?? details?.sector ?? "";
  const industry: string = details?.industryName ?? details?.industry ?? "";

  const lastPrice: number | null = price?.lastClosingPrice ?? price?.lastPrice ?? price?.price ?? null;
  const change: number | null = price?.change ?? null;
  const changePct: number | null = price?.changePercent ?? price?.changePct ?? null;

  const isPositive = changePct !== null && changePct >= 0;

  return (
    <div className="rounded-xl bg-white border border-slate-200 shadow-sm px-6 py-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 className="text-xl font-bold text-slate-900">{name}</h1>
        {(sector || industry) && (
          <p className="mt-1 text-sm text-slate-500">
            {[sector, industry].filter(Boolean).join(" · ")}
          </p>
        )}
      </div>

      {lastPrice !== null && (
        <div className="text-right">
          <p className="text-2xl font-bold text-slate-900">
            ₹{lastPrice.toLocaleString("en-IN")}
          </p>
          {changePct !== null && (
            <p className={`text-sm font-semibold mt-0.5 ${isPositive ? "text-emerald-600" : "text-red-500"}`}>
              {isPositive ? "▲" : "▼"} {Math.abs(changePct).toFixed(2)}%
              {change !== null && (
                <span className="ml-1 font-normal text-slate-400">
                  ({isPositive ? "+" : ""}{change.toFixed(2)})
                </span>
              )}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

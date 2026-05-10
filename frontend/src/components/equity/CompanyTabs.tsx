"use client";

import { useState } from "react";
import DataPanel from "./DataPanel";

const TABS = [
  { key: "overview",    label: "Overview",      endpoints: ["company_details", "about"] },
  { key: "financials",  label: "Financials",    endpoints: ["quaterly_result", "yearly_result"] },
  { key: "balance",     label: "Balance Sheet", endpoints: ["balance_sheet", "cash_flow"] },
  { key: "ratios",      label: "Ratios",        endpoints: ["financial_ratio", "pnl_ratio", "growth_ratio", "valuation_ratio"] },
  { key: "ownership",   label: "Ownership",     endpoints: ["shareholders", "fund_house"] },
  { key: "news",        label: "News",          endpoints: ["latest_news", "corporate_news", "report"] },
  { key: "related",     label: "Related",       endpoints: ["related_companies", "dividend"] },
] as const;

export default function CompanyTabs({ companyId }: { companyId: number }) {
  const [active, setActive] = useState<string>(TABS[0].key);

  const currentTab = TABS.find((t) => t.key === active)!;

  return (
    <div className="space-y-4">
      {/* Tab bar */}
      <div className="flex gap-1 overflow-x-auto rounded-xl bg-white border border-slate-200 shadow-sm p-1">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActive(tab.key)}
            className={`shrink-0 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              active === tab.key
                ? "bg-slate-900 text-white shadow"
                : "text-slate-500 hover:text-slate-800 hover:bg-slate-100"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Panel */}
      <DataPanel key={active} companyId={companyId} endpoints={currentTab.endpoints as unknown as string[]} />
    </div>
  );
}

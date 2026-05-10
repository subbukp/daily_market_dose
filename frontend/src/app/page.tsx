import Link from "next/link";
import { getMetals } from "@/lib/api";
import MetalsCard from "@/components/market/MetalsCard";
import type { Metal } from "@/types/market";

export const revalidate = 300;

const navCards = [
  {
    href: "/bonds",
    label: "Secondary Bonds",
    desc: "Top-rated bonds with yield ≥ 10%, A− and above",
    icon: "📈",
    accent: "border-l-emerald-500",
  },
  {
    href: "/ipo",
    label: "IPO Listings",
    desc: "Upcoming and active IPO opportunities",
    icon: "🏢",
    accent: "border-l-violet-500",
  },
];

export default async function Home() {
  let metals: Metal[] = [];
  try {
    const res = await getMetals();
    metals = res.metals;
  } catch {
    // silently skip if backend is down
  }

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-700 px-8 py-12 text-white shadow-lg">
        <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-emerald-400">
          Indian Markets
        </p>
        <h1 className="text-4xl font-extrabold tracking-tight mb-3">
          RPi Market Dashboard
        </h1>
        <p className="max-w-xl text-slate-300 text-base leading-relaxed">
          Real-time aggregation of secondary bonds, IPOs, precious metals
          and equity fundamentals — all in one place.
        </p>
      </section>

      {/* Metals + nav cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Metals — takes 1 col */}
        <div className="lg:col-span-1">
          {metals.length > 0 ? (
            <MetalsCard metals={metals} />
          ) : (
            <div className="rounded-xl bg-white border border-slate-200 shadow-sm p-6 text-sm text-slate-400">
              Metals data unavailable
            </div>
          )}
        </div>

        {/* Nav cards — take 2 cols */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-500">Explore</h2>
          {navCards.map((c) => (
            <Link
              key={c.href}
              href={c.href}
              className={`group rounded-xl bg-white shadow-sm border border-slate-200 border-l-4 ${c.accent} p-5 flex gap-4 items-start hover:shadow-md transition-shadow`}
            >
              <span className="text-2xl">{c.icon}</span>
              <div>
                <p className="font-semibold text-slate-900 group-hover:text-emerald-600 transition-colors">
                  {c.label}
                </p>
                <p className="text-sm text-slate-500 mt-0.5">{c.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

import { getBonds } from "@/lib/api";
import BondsTable from "@/components/market/BondsTable";
import type { Bond } from "@/types/market";

export const revalidate = 300;

export default async function BondsPage() {
  let bonds: Bond[] = [];
  let error: string | null = null;

  try {
    bonds = await getBonds();
  } catch (e) {
    error = (e as Error).message;
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Secondary Bonds</h1>
          <p className="mt-1 text-sm text-slate-500">
            A− and above · min yield ≥ 10% · sorted by yield · refreshes every 5 min
          </p>
        </div>
        <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
          {bonds.length} bonds
        </span>
      </div>

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 shadow-sm">
          ⚠ {error}
        </div>
      ) : (
        <BondsTable bonds={bonds} />
      )}
    </div>
  );
}

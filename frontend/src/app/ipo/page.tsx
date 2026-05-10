import { getIpos } from "@/lib/api";
import IpoTable from "@/components/market/IpoTable";
import type { Ipo } from "@/types/market";

export const revalidate = 300;

export default async function IpoPage() {
  let ipos: Ipo[] = [];
  let error: string | null = null;

  try {
    ipos = await getIpos();
  } catch (e) {
    error = (e as Error).message;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">IPO Listings</h1>
          <p className="mt-1 text-sm text-slate-500">
            Open IPOs · GMP ≥ 20% · rating ≥ 🔥🔥 · sorted by GMP · refreshes every 5 min
          </p>
        </div>
        <span className="rounded-full bg-violet-100 px-3 py-1 text-xs font-semibold text-violet-700">
          {ipos.length} IPOs
        </span>
      </div>

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 shadow-sm">
          ⚠ {error}
        </div>
      ) : (
        <IpoTable ipos={ipos} />
      )}
    </div>
  );
}

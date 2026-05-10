"use client";

import { useEffect, useState } from "react";

interface Props {
  companyId: number;
  endpoints: string[];
}

export default function DataPanel({ companyId, endpoints }: Props) {
  const [data, setData] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    setLoading(true);
    setData({});
    setErrors({});

    const base = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8005";

    Promise.all(
      endpoints.map(async (ep) => {
        try {
          const res = await fetch(`${base}/market/equity/${ep}/${companyId}`, { cache: "no-store" });
          if (!res.ok) throw new Error(`${res.status}`);
          const json = await res.json();
          return { ep, data: json, error: null };
        } catch (e) {
          return { ep, data: null, error: (e as Error).message };
        }
      })
    ).then((results) => {
      const nextData: Record<string, unknown> = {};
      const nextErrors: Record<string, string> = {};
      for (const r of results) {
        if (r.error) nextErrors[r.ep] = r.error;
        else nextData[r.ep] = r.data;
      }
      setData(nextData);
      setErrors(nextErrors);
      setLoading(false);
    });
  }, [companyId, endpoints]);

  if (loading) {
    return (
      <div className="space-y-3">
        {endpoints.map((ep) => (
          <div key={ep} className="h-28 rounded-xl bg-white border border-slate-200 animate-pulse shadow-sm" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {endpoints.map((ep) => (
        <div key={ep} className="rounded-xl bg-white border border-slate-200 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-5 py-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              {ep.replace(/_/g, " ")}
            </h3>
          </div>
          <div className="p-5">
            {errors[ep] ? (
              <p className="text-sm text-red-500">⚠ {errors[ep]}</p>
            ) : (
              <JsonView data={data[ep]} />
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function isPrimitive(v: unknown): v is string | number | boolean | null | undefined {
  return v === null || v === undefined || typeof v !== "object";
}

function JsonView({ data }: { data: unknown }) {
  if (data === null || data === undefined)
    return <p className="text-sm text-slate-400">No data</p>;

  // ── Array ──
  if (Array.isArray(data)) {
    if (data.length === 0)
      return <p className="text-sm text-slate-400">Empty</p>;

    // Array of primitives → comma list
    if (isPrimitive(data[0]))
      return <p className="text-sm text-slate-700">{data.map(String).join(", ")}</p>;

    // Array of objects → table
    const keys = Object.keys(data[0] as object);
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full text-xs">
          <thead>
            <tr className="border-b border-slate-100">
              {keys.map((k) => (
                <th key={k} className="pb-2 pr-5 text-left font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">
                  {k}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} className="border-b border-slate-50 last:border-0">
                {keys.map((k) => {
                  const cell = (row as Record<string, unknown>)[k];
                  return (
                    <td key={k} className="py-2 pr-5 text-slate-700 whitespace-nowrap">
                      {isPrimitive(cell) ? String(cell ?? "—") : <JsonView data={cell} />}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // ── Object ──
  if (typeof data === "object") {
    const entries = Object.entries(data as Record<string, unknown>);

    // If every value is primitive → compact key-value grid
    if (entries.every(([, v]) => isPrimitive(v))) {
      return (
        <dl className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-3">
          {entries.map(([k, v]) => (
            <div key={k}>
              <dt className="text-xs font-medium text-slate-400 uppercase tracking-wide truncate">{k}</dt>
              <dd className="mt-0.5 text-sm font-semibold text-slate-800" title={String(v)}>
                {String(v ?? "—")}
              </dd>
            </div>
          ))}
        </dl>
      );
    }

    // Mixed object — render each value with its label, recurse complex values
    return (
      <div className="space-y-4">
        {entries.map(([k, v]) => (
          <div key={k}>
            {!isPrimitive(v) && (
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">{k}</p>
            )}
            {isPrimitive(v) ? (
              <dl className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-2">
                <div>
                  <dt className="text-xs font-medium text-slate-400 uppercase tracking-wide">{k}</dt>
                  <dd className="mt-0.5 text-sm font-semibold text-slate-800">{String(v ?? "—")}</dd>
                </div>
              </dl>
            ) : (
              <JsonView data={v} />
            )}
          </div>
        ))}
      </div>
    );
  }

  return <p className="text-sm text-slate-700">{String(data)}</p>;
}

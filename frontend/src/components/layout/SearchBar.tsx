"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // Debounced search — fires after 3 chars with 350ms debounce
  useEffect(() => {
    if (query.length < 3) {
      setResults({});
      setOpen(false);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const base = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8005";
        const res = await fetch(`${base}/market/searchString/${encodeURIComponent(query)}`, { cache: "no-store" });
        if (res.ok) {
          const data: Record<string, number> = await res.json();
          const startsWithPattern = new RegExp(`^${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`, "i");
          const filtered = Object.fromEntries(
            Object.entries(data).filter(([name]) => startsWithPattern.test(name))
          );
          setResults(filtered);
          setOpen(Object.keys(filtered).length > 0);
        }
      } catch {
        // silently fail
      } finally {
        setLoading(false);
      }
    }, 350);
    return () => clearTimeout(timer);
  }, [query]);

  function handleSelect(name: string, id: number) {
    setQuery(name);
    setOpen(false);
    router.push(`/equity/${id}`);
  }

  const entries = Object.entries(results);

  return (
    <div ref={containerRef} className="relative w-64">
      <div className="flex items-center rounded-lg bg-slate-700 px-3 py-1.5 gap-2">
        <svg className="h-3.5 w-3.5 shrink-0 text-slate-400" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search company…"
          className="w-full bg-transparent text-sm text-white placeholder-slate-400 outline-none"
        />
        {loading && (
          <svg className="h-3.5 w-3.5 shrink-0 animate-spin text-slate-400" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
        )}
      </div>

      {open && entries.length > 0 && (
        <ul className="absolute left-0 top-full z-50 mt-1.5 w-full overflow-hidden rounded-lg border border-slate-200 bg-white shadow-xl">
          {entries.slice(0, 8).map(([name, id]) => (
            <li key={id}>
              <button
                onMouseDown={() => handleSelect(name, id)}
                className="flex w-full items-center justify-between px-4 py-2.5 text-left text-sm hover:bg-slate-50 transition-colors"
              >
                <span className="font-medium text-slate-800 truncate">{name}</span>
                <span className="ml-2 shrink-0 text-xs text-slate-400">#{id}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

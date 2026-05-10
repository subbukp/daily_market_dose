import type { Bond, Mmi, UsIndex, MetalsResponse, Ipo } from "@/types/market";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8005";

export async function getMmi(): Promise<Mmi> {
  const res = await fetch(`${BASE}/market/mmi`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error("Failed to fetch MMI");
  return res.json();
}

export async function getUsIndex(): Promise<UsIndex> {
  const res = await fetch(`${BASE}/market/us-index`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error("Failed to fetch US index");
  return res.json();
}

export async function getMetals(): Promise<MetalsResponse> {
  const res = await fetch(`${BASE}/market/metals`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error("Failed to fetch metals");
  return res.json();
}

export async function getBonds(): Promise<Bond[]> {
  const res = await fetch(`${BASE}/market/bonds`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error("Failed to fetch bonds");
  return res.json();
}

export async function getIpos(): Promise<Ipo[]> {
  const res = await fetch(`${BASE}/market/ipo`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error("Failed to fetch IPOs");
  return res.json();
}

export async function getEquity(path: string, companyId: number): Promise<unknown> {
  const res = await fetch(`${BASE}/market/equity/${path}/${companyId}`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error(`Failed to fetch equity/${path}`);
  return res.json();
}

export async function searchCompanies(query: string): Promise<Record<string, number>> {
  const res = await fetch(`${BASE}/market/searchString/${encodeURIComponent(query)}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}

import Link from "next/link";
import SearchBar from "./SearchBar";

const links = [
  { href: "/market/bonds", label: "Bonds" },
  { href: "/market/ipo", label: "IPO" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-10 bg-slate-900 shadow-lg">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-emerald-500 text-white font-bold text-sm">
            ₹
          </div>
          <span className="text-base font-bold text-white tracking-tight">
            RPi Market
          </span>
        </Link>
        <div className="flex items-center gap-3">
          <SearchBar />
          <nav className="flex items-center gap-1">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className="rounded-md px-3 py-1.5 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-700 hover:text-white"
              >
                {l.label}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}

import { useMemo, useState, type ReactNode } from "react";
import { fieldClass } from "./ui";

interface Column<T> {
  key: string;
  label: string;
  render?: (row: T) => ReactNode;
}

export function DataTable<T extends Record<string, unknown>>({
  rows,
  columns,
  searchKeys,
  filterKey,
  expand,
}: {
  rows: T[];
  columns: Column<T>[];
  searchKeys: string[];
  filterKey?: string;
  expand?: (row: T) => ReactNode;
}) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("All");
  const [sortKey, setSortKey] = useState(columns[0]?.key || "");
  const [dir, setDir] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(0);
  const pageSize = 20;

  const filters = useMemo(() => {
    if (!filterKey) return [];
    return Array.from(new Set(rows.map((row) => String(row[filterKey] ?? "")).filter(Boolean))).sort();
  }, [rows, filterKey]);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    let next = rows.filter((row) => {
      const matchesQuery = !q || searchKeys.some((key) => String(row[key] ?? "").toLowerCase().includes(q));
      const matchesFilter = !filterKey || filter === "All" || String(row[filterKey] ?? "") === filter;
      return matchesQuery && matchesFilter;
    });
    next = [...next].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      const an = Number(av);
      const bn = Number(bv);
      const cmp = Number.isFinite(an) && Number.isFinite(bn) ? an - bn : String(av ?? "").localeCompare(String(bv ?? ""));
      return dir === "asc" ? cmp : -cmp;
    });
    return next;
  }, [rows, query, filter, filterKey, searchKeys, sortKey, dir]);

  const pages = Math.max(1, Math.ceil(visible.length / pageSize));
  const slice = visible.slice(page * pageSize, page * pageSize + pageSize);

  return (
    <div>
      <div className="mb-3 flex flex-col gap-2 sm:flex-row">
        <input className={fieldClass} placeholder="Search" value={query} onChange={(e) => { setQuery(e.target.value); setPage(0); }} />
        {filterKey && (
          <select className={fieldClass} value={filter} onChange={(e) => { setFilter(e.target.value); setPage(0); }}>
            <option>All</option>
            {filters.map((item) => <option key={item}>{item}</option>)}
          </select>
        )}
      </div>
      <div className="max-h-[70vh] overflow-auto rounded-2xl border border-slate-200 dark:border-white/10">
        <table className="min-w-full text-left text-sm text-[#0b1f3a] dark:text-[#e7f0fa]">
          <thead className="sticky top-0 bg-[#e7f1fb] text-[#0b1f3a] dark:bg-[#16345c] dark:text-white">
            <tr>
              {columns.map((column) => (
                <th key={column.key} className="px-3 py-2 font-semibold">
                  <button
                    className="inline-flex items-center gap-1"
                    onClick={() => {
                      if (sortKey === column.key) setDir(dir === "asc" ? "desc" : "asc");
                      else { setSortKey(column.key); setDir("asc"); }
                    }}
                  >
                    {column.label}{sortKey === column.key ? (dir === "asc" ? " ↑" : " ↓") : ""}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {slice.length === 0 && (
              <tr><td className="px-3 py-6 text-slate-500" colSpan={columns.length}>No matching rows.</td></tr>
            )}
            {slice.map((row, index) => (
              <tr key={index} className="border-t border-slate-200 align-top dark:border-white/10">
                {expand ? (
                  <td className="px-3 py-3" colSpan={columns.length}>
                    <div className="grid gap-2 md:grid-cols-2">
                      {columns.map((column) => (
                        <div key={column.key}><span className="font-semibold">{column.label}: </span>{column.render ? column.render(row) : String(row[column.key] ?? "")}</div>
                      ))}
                    </div>
                    <div className="mt-2 text-slate-600 dark:text-slate-300">{expand(row)}</div>
                  </td>
                ) : columns.map((column) => (
                  <td key={column.key} className="px-3 py-2">{column.render ? column.render(row) : String(row[column.key] ?? "")}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-sm text-[#0b1f3a] dark:text-[#e7f0fa]">
        <span>{visible.length} rows. Scroll the table, or use the pages.</span>
        <div className="flex gap-2">
          <button className="rounded-full border border-[#c5d7ea] px-3 py-1 disabled:opacity-40 dark:border-white/20" disabled={page === 0} onClick={() => setPage((p) => Math.max(0, p - 1))}>Previous</button>
          <span className="self-center">{page + 1} / {pages}</span>
          <button className="rounded-full border border-[#c5d7ea] px-3 py-1 disabled:opacity-40 dark:border-white/20" disabled={page + 1 >= pages} onClick={() => setPage((p) => p + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}

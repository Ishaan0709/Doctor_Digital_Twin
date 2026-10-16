import { useEffect, useState, type ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { Menu, Moon, Sun, X } from "lucide-react";
import { useAppStore } from "../store/useAppStore";
import { cn } from "../lib/utils";

const groups = [
  {
    label: "Start",
    items: [
      ["/", "Home"],
      ["/consultation", "Consultation Portal"],
      ["/patient", "Patient Analysis"],
    ],
  },
  {
    label: "Consult",
    items: [
      ["/generic", "GPT vs Twin"],
      ["/twin", "Vimlesh Twin"],
      ["/compare", "GPT Twin Comparison"],
    ],
  },
  {
    label: "Evidence",
    items: [
      ["/evidence", "Evidence Panel"],
      ["/cases", "Historical Cases"],
      ["/graph", "Graph Intelligence"],
      ["/insights", "Comparison Insights"],
      ["/why", "Why This Recommendation"],
      ["/explain", "Explainability"],
    ],
  },
  { label: "Data", items: [["/admin", "Admin / Dataset"]] },
];

const steps = [
  ["/patient", "Intake"],
  ["/generic", "Generic"],
  ["/twin", "Twin"],
  ["/compare", "Difference"],
  ["/cases", "Cases"],
  ["/graph", "Graph"],
  ["/insights", "Insights"],
  ["/why", "Why"],
  ["/admin", "Admin"],
  ["/explain", "Explain"],
];

export function Layout({ children }: { children: ReactNode }) {
  const theme = useAppStore((s) => s.theme);
  const setTheme = useAppStore((s) => s.setTheme);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  const nav = (
    <nav className="space-y-5">
      {groups.map((group) => (
        <div key={group.label}>
          <p className="px-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">{group.label}</p>
          <div className="mt-2 space-y-1">
            {group.items.map(([to, label]) => (
              <NavLink
                key={label}
                to={to.trim()}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  cn(
                    "block rounded-xl px-3 py-2 text-sm transition",
                    isActive ? "bg-sky-500/15 font-semibold text-sky-700 dark:text-sky-200" : "text-slate-600 hover:bg-slate-200/70 dark:text-slate-300 dark:hover:bg-white/5",
                  )
                }
              >
                {label}
              </NavLink>
            ))}
          </div>
        </div>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen md:grid md:grid-cols-[270px_1fr]">
      <aside className="hidden border-r border-slate-200/70 bg-white/50 p-4 backdrop-blur dark:border-white/10 dark:bg-white/[0.03] md:block">
        <div className="mb-6 flex items-center gap-3 px-2">
          <img src="/logo.png" alt="CardioTwin logo" className="h-10 w-10 rounded-xl object-cover" />
          <div>
            <p className="font-semibold">CardioTwin AI</p>
            <p className="text-xs text-slate-500">Elite cardiology reasoning</p>
          </div>
        </div>
        {nav}
      </aside>
      {open && (
        <div className="fixed inset-0 z-40 bg-slate-950/50 md:hidden" onClick={() => setOpen(false)}>
          <aside className="h-full w-[280px] overflow-y-auto bg-white p-4 dark:bg-[#0b1220]" onClick={(event) => event.stopPropagation()}>
            <div className="mb-4 flex items-center justify-between">
              <p className="font-semibold">CardioTwin AI</p>
              <button aria-label="Close menu" onClick={() => setOpen(false)}>
                <X size={18} />
              </button>
            </div>
            {nav}
          </aside>
        </div>
      )}
      <div className="min-w-0">
        <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/75 backdrop-blur dark:border-white/10 dark:bg-[#070b14]/80">
          <div className="flex items-center gap-3 px-4 py-3">
            <button className="md:hidden" aria-label="Open menu" onClick={() => setOpen(true)}>
              <Menu size={20} />
            </button>
            <div className="hidden flex-1 gap-2 overflow-x-auto lg:flex">
              {steps.map(([to, label]) => (
                <NavLink key={label} to={to} className={({ isActive }) => cn("shrink-0 rounded-full border px-3 py-1 text-xs", isActive ? "border-sky-400 bg-sky-500/15" : "border-slate-300/70 dark:border-white/10")}>
                  {label}
                </NavLink>
              ))}
            </div>
            <button
              className="ml-auto inline-flex items-center gap-2 rounded-full border border-slate-300 px-3 py-1.5 text-xs dark:border-white/15"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? <Sun size={14} /> : <Moon size={14} />}
              {theme === "dark" ? "Light" : "Dark"}
            </button>
          </div>
        </header>
        <main className="mx-auto w-full max-w-6xl px-4 py-6 md:px-8">{children}</main>
        <footer className="px-4 pb-8 text-center text-xs text-slate-500 md:px-8">
          Clinical decision support only. Not a substitute for a real doctor or emergency care.
        </footer>
      </div>
    </div>
  );
}

import { useEffect, useState, type ReactNode } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { Menu, Moon, Sun, X } from "lucide-react";
import { useAppStore } from "../store/useAppStore";
import { cn } from "../lib/utils";

const studioPaths = ["/studio", "/generic", "/twin", "/compare", "/insights", "/graph", "/why", "/explain", "/evidence", "/cases", "/admin"];

const studioLinks = [
  ["/generic", "Generic GPT"],
  ["/twin", "Doctor's Twin"],
  ["/compare", "Side by side"],
  ["/graph", "Graph"],
  ["/why", "Why"],
  ["/insights", "Scores"],
];

function LinkItem({ to, label, onClick }: { to: string; label: string; onClick?: () => void }) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        cn(
          "rounded-full px-3 py-2 text-sm",
          isActive ? "bg-[#123a6b] font-semibold text-white" : "text-[#1a1a1a] hover:bg-[#e7f1fb] dark:text-[#f4f7fb] dark:hover:bg-white/5",
        )
      }
    >
      {label}
    </NavLink>
  );
}

export function Layout({ children }: { children: ReactNode }) {
  const theme = useAppStore((s) => s.theme);
  const setTheme = useAppStore((s) => s.setTheme);
  const doctorView = useAppStore((s) => s.portal.view) === "Doctor";
  const patch = useAppStore((s) => s.patchPortal);
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const studio = studioPaths.some((path) => pathname === path);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    document.body.classList.toggle("studio", studio);
  }, [theme, studio]);

  const close = () => setOpen(false);

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-[#d5e4f2] bg-white/95 backdrop-blur dark:border-white/10 dark:bg-[#071422]/95">
        <div className="mx-auto flex w-full max-w-[1440px] flex-wrap items-center gap-2 px-3 py-3 sm:gap-3 sm:px-6">
          <NavLink to="/" aria-label="Home" className="flex items-center gap-3" onClick={close}>
            <img src="/logo.png?v=2" alt="" className="h-10 w-10 rounded-2xl object-cover" />
            <span>
              <span className="block font-display text-lg leading-none">CardioTwin</span>
              <span className="text-xs text-[#123a6b] dark:text-[#8eb8e8]">{studio ? "Compare the answers" : "Dr. Vimlesh Pandey"}</span>
            </span>
          </NavLink>
          <nav className="ml-auto hidden items-center gap-1 md:flex">
            {studio ? (
              <>
                <LinkItem to="/" label="Back to the visit" />
                {studioLinks.map(([to, label]) => (
                  <LinkItem key={to} to={to} label={label} />
                ))}
              </>
            ) : (
              <LinkItem to="/consultation" label="Consultation" />
            )}
          </nav>
          <button
            className="ml-auto rounded-full bg-[#123a6b] px-3 py-1.5 text-xs font-semibold text-white"
            onClick={() => {
              patch({ view: doctorView && pathname === "/consultation" ? "Patient" : "Doctor" });
              if (pathname !== "/consultation") navigate("/consultation");
            }}
          >
            {doctorView && pathname === "/consultation" ? "Patient view" : "Doctor's view"}
          </button>
          <button
            className="inline-flex items-center gap-2 rounded-full border border-[#c5d7ea] px-3 py-1.5 text-xs text-[#0b1f3a] dark:border-white/30 dark:text-white"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <Sun size={14} /> : <Moon size={14} />}
            {theme === "dark" ? "Light" : "Dark"}
          </button>
          <button className="md:hidden" aria-label="Open menu" onClick={() => setOpen(true)}>
            <Menu size={20} />
          </button>
        </div>
      </header>
      {open && (
        <div className="fixed inset-0 z-40 bg-[#1a1a1a]/40 md:hidden" onClick={close}>
          <aside className="h-full w-[280px] bg-white p-4 dark:bg-[#071422]" onClick={(event) => event.stopPropagation()}>
            <div className="mb-4 flex items-center justify-between">
              <p className="font-display text-lg">CardioTwin</p>
              <button aria-label="Close menu" onClick={close}><X size={18} /></button>
            </div>
            <div className="flex flex-col gap-1">
              {studio ? (
                <>
                  <LinkItem to="/" label="Back to the visit" onClick={close} />
                  {studioLinks.map(([to, label]) => (
                    <LinkItem key={to} to={to} label={label} onClick={close} />
                  ))}
                </>
              ) : (
                <>
                  <LinkItem to="/" label="Home" onClick={close} />
                  <LinkItem to="/consultation" label="Consultation" onClick={close} />
                  <LinkItem to="/studio" label="Which is stronger" onClick={close} />
                </>
              )}
            </div>
          </aside>
        </div>
      )}
      <main className="mx-auto w-full max-w-[1440px] flex-1 px-3 py-6 sm:px-6 sm:py-8">{children}</main>
      <footer className="border-t border-[#d5e4f2] px-4 py-6 text-center text-sm text-[#2c4060] dark:border-white/10 dark:text-[#d5e4f0]">
        Clinical decision support for when Dr. Pandey is not in the room. Pain at rest, fainting, or severe breathlessness needs emergency care.
      </footer>
    </div>
  );
}

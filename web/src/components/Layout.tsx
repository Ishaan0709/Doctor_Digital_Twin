import { useEffect, useState, type ReactNode } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { Menu, Moon, Sun, X } from "lucide-react";
import { useAppStore } from "../store/useAppStore";
import { ModelNote } from "./ui";
import { cn } from "../lib/utils";

const links = [
  ["/", "Home"],
  ["/consultation", "Consultation"],
  ["/records", "Records"],
  ["/compare", "Compare"],
];

function LinkItem({ to, label, onClick }: { to: string; label: string; onClick?: () => void }) {
  return (
    <NavLink
      to={to}
      end={to === "/"}
      onClick={onClick}
      className={({ isActive }) =>
        cn(
          "rounded-full px-3.5 py-2 text-sm transition",
          isActive ? "bg-[#172033] font-medium text-[#f7f4ef] dark:bg-[#f3eadf] dark:text-[#172033]" : "text-[#3c4658] hover:bg-white dark:text-[#f4efe8] dark:hover:bg-white/5",
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
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-[#eadfd2]/80 bg-[#f7f4ef]/80 backdrop-blur-xl dark:border-white/10 dark:bg-[#0b1220]/80">
        <div className="mx-auto flex w-full max-w-6xl items-center gap-3 px-4 py-3">
          <NavLink to="/" aria-label="Home" className="flex items-center gap-3" onClick={close}>
            <img src="/logo.png?v=2" alt="" className="h-11 w-11 rounded-2xl object-cover shadow-sm" />
            <span>
              <span className="block font-display text-xl leading-none text-[#172033] dark:text-[#f7f4ef]">CardioTwin</span>
              <ModelNote />
            </span>
          </NavLink>
          <nav className="ml-auto hidden items-center gap-1 md:flex">
            {links.map(([to, label]) => (
              <LinkItem key={to} to={to} label={label} />
            ))}
          </nav>
          <button
            className="rounded-full border border-[#172033] bg-[#172033] px-3 py-1.5 text-xs font-medium text-[#f7f4ef] transition hover:-translate-y-0.5 dark:border-[#f3eadf] dark:bg-[#f3eadf] dark:text-[#172033]"
            onClick={() => {
              patch({ view: doctorView && pathname === "/consultation" ? "Patient" : "Doctor" });
              if (pathname !== "/consultation") navigate("/consultation");
            }}
          >
            {doctorView && pathname === "/consultation" ? "Patient view" : "Doctor's view"}
          </button>
          <button
            className="inline-flex items-center gap-2 rounded-full border border-[#eadfd2] bg-white/70 px-3 py-1.5 text-xs text-[#172033] dark:border-white/15 dark:bg-white/5 dark:text-[#f7f4ef]"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <Sun size={14} /> : <Moon size={14} />}
          </button>
          <button className="md:hidden" aria-label="Open menu" onClick={() => setOpen(true)}>
            <Menu size={20} />
          </button>
        </div>
      </header>
      {open && (
        <div className="fixed inset-0 z-40 bg-[#172033]/40 md:hidden" onClick={close}>
          <aside className="h-full w-[280px] bg-[#f7f4ef] p-5 dark:bg-[#0b1220]" onClick={(event) => event.stopPropagation()}>
            <div className="mb-6 flex items-center justify-between">
              <p className="font-display text-2xl">CardioTwin</p>
              <button aria-label="Close menu" onClick={close}><X size={18} /></button>
            </div>
            <div className="flex flex-col gap-1">
              {links.map(([to, label]) => (
                <LinkItem key={to} to={to} label={label} onClick={close} />
              ))}
            </div>
          </aside>
        </div>
      )}
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:py-10">{children}</main>
      <footer className="border-t border-[#eadfd2] px-4 py-8 text-center text-sm text-[#5c5348] dark:border-white/10 dark:text-[#d9d0c5]">
        Decision support for when Dr. Pandey is not in the room. Pain at rest, fainting, or severe breathlessness needs emergency care.
      </footer>
    </div>
  );
}

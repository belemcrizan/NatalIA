import {
  BookOpen,
  ClipboardPen,
  FlaskConical,
  HeartPulse,
  History,
  Home,
  Scale,
  Sigma,
} from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

import { HealthDot } from "@/components/HealthDot";
import { cn } from "@/lib/utils";

const items = [
  { to: "/", label: "Home", icon: Home, end: true },
  { to: "/library", label: "Examples", icon: BookOpen },
  { to: "/builder", label: "Claim builder", icon: ClipboardPen },
  { to: "/history", label: "History", icon: History },
  { to: "/benchmark", label: "Benchmark", icon: Sigma },
  { to: "/trust", label: "Trust", icon: Scale },
  { to: "/diagnostics", label: "Diagnostics", icon: HeartPulse },
];

export function AppShell() {
  return (
    <div className="min-h-screen bg-bg text-ink">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <div className="mx-auto flex min-h-screen max-w-[1400px]">
        <aside className="sticky top-0 flex h-screen w-16 flex-col border-r border-line bg-surface md:w-56">
          <div className="flex items-center gap-2 px-3 py-4">
            <FlaskConical className="h-6 w-6 text-accent" aria-hidden />
            <div className="hidden md:block">
              <p className="text-sm font-semibold">NatalIA</p>
              <p className="text-xs text-muted">Scientific workspace</p>
            </div>
          </div>
          <nav aria-label="Primary" className="flex flex-1 flex-col gap-1 px-2">
            {items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                aria-label={item.label}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-2 rounded-md px-2 py-2 text-sm text-muted hover:bg-accent-soft hover:text-ink",
                    isActive && "bg-accent-soft font-medium text-ink",
                  )
                }
              >
                <item.icon className="h-4 w-4 shrink-0" aria-hidden />
                <span className="hidden md:inline">{item.label}</span>
              </NavLink>
            ))}
          </nav>
          <div className="border-t border-line p-3">
            <HealthDot />
          </div>
        </aside>
        <div className="min-w-0 flex-1">
          <main id="main" className="px-4 py-6 md:px-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}

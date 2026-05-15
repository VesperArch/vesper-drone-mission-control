import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  PlusCircle,
  Radio,
  ScrollText,
  Crosshair,
} from "lucide-react";

const nav = [
  { to: "/dashboard",      icon: LayoutDashboard, label: "Dashboard"        },
  { to: "/create-mission", icon: PlusCircle,       label: "New Mission"      },
  { to: "/missions",       icon: Radio,            label: "Active Missions"  },
  { to: "/logs",           icon: ScrollText,       label: "Mission Logs"     },
];

export default function Sidebar() {
  return (
    <aside className="w-60 bg-vesper-surface border-r border-vesper-border flex flex-col shrink-0">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-vesper-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-vesper-cyan/20 border border-vesper-cyan/40 flex items-center justify-center">
            <Crosshair size={16} className="text-vesper-cyan" />
          </div>
          <div>
            <div className="text-white font-semibold text-sm tracking-wide">VESPER</div>
            <div className="text-vesper-muted text-xs font-mono">Mission Control</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {nav.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150 ${
                isActive
                  ? "bg-vesper-cyan/10 text-vesper-cyan border border-vesper-cyan/20"
                  : "text-vesper-muted hover:text-vesper-text hover:bg-vesper-border/40"
              }`
            }
          >
            <Icon size={16} />
            <span className="font-medium">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer badge */}
      <div className="px-4 py-4 border-t border-vesper-border">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-vesper-green animate-pulse-slow" />
          <span className="text-xs text-vesper-muted font-mono">SYSTEM ONLINE</span>
        </div>
        <div className="text-xs text-vesper-muted/60 mt-1 font-mono">Maricá / RJ — Brazil</div>
      </div>
    </aside>
  );
}

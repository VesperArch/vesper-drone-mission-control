import { useLocation } from "react-router-dom";
import { Bell, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchStatus } from "../../api/system";

const titles = {
  "/dashboard":      "Operational Dashboard",
  "/create-mission": "New Mission",
  "/missions":       "Active Missions",
  "/logs":           "Mission Logs",
};

export default function TopBar() {
  const { pathname } = useLocation();
  const [time, setTime] = useState(new Date());
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    fetchStatus().then((d) => setStats(d.statistics)).catch(() => {});
    const interval = setInterval(() => {
      fetchStatus().then((d) => setStats(d.statistics)).catch(() => {});
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-14 border-b border-vesper-border bg-vesper-surface flex items-center px-6 gap-4 shrink-0">
      <h1 className="text-white font-semibold text-base tracking-tight flex-1">
        {titles[pathname] ?? "Vesper"}
      </h1>

      {stats && (
        <div className="hidden md:flex items-center gap-5 text-xs font-mono text-vesper-muted">
          <span>
            <span className="text-vesper-green font-medium">{stats.active_drones}</span> drones active
          </span>
          <span>
            <span className="text-vesper-cyan font-medium">{stats.active_missions}</span> missions live
          </span>
          <span>
            <span className="text-vesper-amber font-medium">{stats.total_events_fired}</span> events
          </span>
        </div>
      )}

      <div className="text-xs font-mono text-vesper-muted hidden sm:block">
        {time.toLocaleTimeString("pt-BR", { timeZone: "America/Sao_Paulo" })}
        <span className="text-vesper-muted/50 ml-1">BRT</span>
      </div>

      <button className="p-2 rounded-lg hover:bg-vesper-border/40 text-vesper-muted hover:text-vesper-text transition-colors">
        <Bell size={16} />
      </button>
    </header>
  );
}

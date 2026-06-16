import { useEffect, useState } from "react";
import { fetchLogs } from "../api/missions";
import { RefreshCw, AlertTriangle, CheckCircle, Info, Zap, Cloud, WifiOff } from "lucide-react";

const EVENT_CFG = {
  MISSION_STARTED:    { icon: Info,          color: "text-vesper-cyan",  bg: "bg-vesper-cyan/5",  label: "STARTED"    },
  MISSION_COMPLETED:  { icon: CheckCircle,   color: "text-vesper-green", bg: "bg-vesper-green/5", label: "COMPLETED"  },
  LOW_BATTERY:        { icon: Zap,           color: "text-vesper-amber", bg: "bg-vesper-amber/5", label: "LOW BATT"   },
  BAD_WEATHER:        { icon: Cloud,         color: "text-vesper-amber", bg: "bg-vesper-amber/5", label: "WEATHER"    },
  SIGNAL_LOST:        { icon: WifiOff,       color: "text-vesper-red",   bg: "bg-vesper-red/5",   label: "SIGNAL"     },
  MISSION_FAILED:     { icon: AlertTriangle, color: "text-vesper-red",   bg: "bg-vesper-red/5",   label: "FAILED"     },
  OBSTACLE_DETECTED:  { icon: AlertTriangle, color: "text-vesper-amber", bg: "bg-vesper-amber/5", label: "OBSTACLE"   },
  RETURN_TO_BASE:     { icon: Info,          color: "text-vesper-muted", bg: "bg-vesper-muted/5", label: "RETURN"     },
};

const SEVERITY_COLOR = { INFO: "text-vesper-cyan", WARNING: "text-vesper-amber", ALERT: "text-vesper-red", SUCCESS: "text-vesper-green" };

export default function MissionLogs() {
  const [logs, setLogs]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter]   = useState("ALL");

  const load = () => {
    setLoading(true);
    fetchLogs().then(setLogs).finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 10_000);
    return () => clearInterval(id);
  }, []);

  const eventTypes = ["ALL", ...new Set(logs.map((l) => l.event_type))];
  const filtered   = filter === "ALL" ? logs : logs.filter((l) => l.event_type === filter);

  return (
    <div className="max-w-screen-lg space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex gap-2 flex-wrap">
          {eventTypes.map((t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`badge cursor-pointer transition-all ${
                filter === t
                  ? "bg-vesper-cyan/20 text-vesper-cyan border border-vesper-cyan/30"
                  : "bg-vesper-border/40 text-vesper-muted border border-transparent hover:border-vesper-border"
              }`}
            >
              {t === "ALL" ? "ALL" : (EVENT_CFG[t]?.label ?? t)}
            </button>
          ))}
        </div>
        <button onClick={load} className="p-1.5 rounded-lg hover:bg-vesper-border/40 text-vesper-muted hover:text-vesper-text transition-colors">
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      <div className="card p-0 overflow-hidden">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-vesper-border">
              {["Time", "Event", "Severity", "Mission ID", "Message"].map((h) => (
                <th key={h} className="text-left px-4 py-3 text-vesper-muted font-medium uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={5} className="text-center text-vesper-muted py-12">No log entries</td></tr>
            )}
            {filtered.map((log, i) => {
              const cfg = EVENT_CFG[log.event_type] ?? EVENT_CFG.MISSION_STARTED;
              const Icon = cfg.icon;
              return (
                <tr key={log.id ?? i} className={`border-b border-vesper-border/30 last:border-0 hover:${cfg.bg} transition-colors`}>
                  <td className="px-4 py-3 font-mono text-vesper-muted whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" })}
                  </td>
                  <td className="px-4 py-3">
                    <div className={`flex items-center gap-1.5 font-mono font-medium ${cfg.color}`}>
                      <Icon size={11} />
                      {cfg.label ?? log.event_type}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`font-mono ${SEVERITY_COLOR[log.severity] ?? "text-vesper-muted"}`}>
                      {log.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-vesper-muted/70">
                    {String(log.mission).slice(0, 8)}…
                  </td>
                  <td className="px-4 py-3 text-vesper-text/80 max-w-xs truncate">{log.message}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

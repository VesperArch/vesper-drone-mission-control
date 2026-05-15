import { useEffect, useState } from "react";
import { fetchStatus } from "../../api/system";
import { Server, Cpu, Radio, Activity } from "lucide-react";

function Row({ icon: Icon, label, value, valueClass = "text-vesper-text" }) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-vesper-border/50 last:border-0">
      <Icon size={13} className="text-vesper-muted shrink-0" />
      <span className="text-xs text-vesper-muted flex-1">{label}</span>
      <span className={`text-xs font-mono font-medium ${valueClass}`}>{value}</span>
    </div>
  );
}

export default function SystemStatus() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const load = () => fetchStatus().then((d) => setStats(d.statistics)).catch(() => {});
    load();
    const id = setInterval(load, 10000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <span className="w-2 h-2 rounded-full bg-vesper-green animate-pulse-slow" />
        <span className="section-title">System Health</span>
      </div>
      {stats ? (
        <div>
          <Row icon={Radio}    label="Active Drones"       value={stats.active_drones}          valueClass="text-vesper-cyan"  />
          <Row icon={Cpu}      label="Idle Drones"         value={stats.idle_drones}             valueClass="text-vesper-green" />
          <Row icon={Activity} label="Active Missions"     value={stats.active_missions}         valueClass="text-vesper-amber" />
          <Row icon={Server}   label="Total Missions"      value={stats.total_missions}          />
          <Row icon={Server}   label="Events Fired"        value={stats.total_events_fired}      valueClass="text-vesper-muted" />
        </div>
      ) : (
        <div className="text-vesper-muted text-xs text-center py-4">Loading…</div>
      )}
    </div>
  );
}

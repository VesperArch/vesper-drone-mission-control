import { useEffect, useState, useRef } from "react";
import { fetchStatus } from "../../api/system";
import { AlertTriangle, CheckCircle, Info, WifiOff, Zap, Cloud } from "lucide-react";

const EVENT_CONFIG = {
  MISSION_STARTED:    { icon: Info,          color: "text-vesper-cyan",  bg: "bg-vesper-cyan/10"  },
  MISSION_COMPLETED:  { icon: CheckCircle,   color: "text-vesper-green", bg: "bg-vesper-green/10" },
  LOW_BATTERY:        { icon: Zap,           color: "text-vesper-amber", bg: "bg-vesper-amber/10" },
  BAD_WEATHER:        { icon: Cloud,         color: "text-vesper-amber", bg: "bg-vesper-amber/10" },
  SIGNAL_LOST:        { icon: WifiOff,       color: "text-vesper-red",   bg: "bg-vesper-red/10"   },
  MISSION_FAILED:     { icon: AlertTriangle, color: "text-vesper-red",   bg: "bg-vesper-red/10"   },
  RETURN_TO_BASE:     { icon: Info,          color: "text-vesper-muted", bg: "bg-vesper-muted/10" },
  OBSTACLE_DETECTED:  { icon: AlertTriangle, color: "text-vesper-amber", bg: "bg-vesper-amber/10" },
};

function fmt(iso) {
  return new Date(iso).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export default function EventFeed() {
  const [events, setEvents] = useState([]);
  const listRef = useRef(null);

  useEffect(() => {
    const load = () => {
      fetchStatus()
        .then((d) => setEvents(d.recent_events || []))
        .catch(() => {});
    };
    load();
    const id = setInterval(load, 8000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <span className="section-title">Live Event Feed</span>
        <span className="badge bg-vesper-cyan/10 text-vesper-cyan border border-vesper-cyan/20">
          {events.length} events
        </span>
      </div>
      <div ref={listRef} className="flex-1 overflow-y-auto space-y-2 pr-1">
        {events.length === 0 && (
          <div className="text-vesper-muted text-sm text-center py-8">No events yet</div>
        )}
        {events.map((ev, i) => {
          const cfg = EVENT_CONFIG[ev.event_type] ?? EVENT_CONFIG.MISSION_STARTED;
          const Icon = cfg.icon;
          return (
            <div key={i} className={`flex items-start gap-3 p-2.5 rounded-lg ${cfg.bg} animate-slide-up`}>
              <Icon size={14} className={`${cfg.color} shrink-0 mt-0.5`} />
              <div className="flex-1 min-w-0">
                <div className={`text-xs font-mono font-medium ${cfg.color}`}>{ev.event_type}</div>
                <div className="text-xs text-vesper-text/80 mt-0.5 truncate">{ev.message}</div>
              </div>
              <div className="text-xs font-mono text-vesper-muted shrink-0">{fmt(ev.timestamp)}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

import { CheckCircle, AlertTriangle, Info, Zap, Cloud, WifiOff } from "lucide-react";

const EVENT_CONFIG = {
  MISSION_STARTED:   { icon: Info,          color: "text-vesper-cyan",  label: "Started"         },
  MISSION_COMPLETED: { icon: CheckCircle,   color: "text-vesper-green", label: "Completed"       },
  LOW_BATTERY:       { icon: Zap,           color: "text-vesper-amber", label: "Low Battery"     },
  BAD_WEATHER:       { icon: Cloud,         color: "text-vesper-amber", label: "Bad Weather"     },
  SIGNAL_LOST:       { icon: WifiOff,       color: "text-vesper-red",   label: "Signal Lost"     },
  MISSION_FAILED:    { icon: AlertTriangle, color: "text-vesper-red",   label: "Failed"          },
  RETURN_TO_BASE:    { icon: Info,          color: "text-vesper-muted", label: "Return to Base"  },
  OBSTACLE_DETECTED: { icon: AlertTriangle, color: "text-vesper-amber", label: "Obstacle"        },
};

export default function MissionTimeline({ events = [] }) {
  if (!events.length) return (
    <div className="text-vesper-muted text-sm text-center py-6">No events recorded</div>
  );

  return (
    <div className="relative pl-4">
      {/* vertical line */}
      <div className="absolute left-[7px] top-2 bottom-2 w-px bg-vesper-border" />

      <div className="space-y-3">
        {[...events].reverse().map((ev, i) => {
          const cfg = EVENT_CONFIG[ev.event_type] ?? EVENT_CONFIG.MISSION_STARTED;
          const Icon = cfg.icon;
          return (
            <div key={ev.id ?? i} className="flex items-start gap-3 relative">
              <div className={`w-3.5 h-3.5 rounded-full border-2 border-vesper-bg shrink-0 mt-0.5 flex items-center justify-center ${cfg.color.replace("text-", "bg-").replace("-500", "-400")}`}>
                <span className="w-1 h-1 rounded-full bg-vesper-bg" />
              </div>
              <div className="flex-1">
                <div className={`text-xs font-mono font-medium ${cfg.color}`}>{cfg.label}</div>
                <div className="text-xs text-vesper-text/70 mt-0.5">{ev.message}</div>
              </div>
              <div className="text-xs font-mono text-vesper-muted shrink-0">
                {new Date(ev.timestamp).toLocaleTimeString("pt-BR")}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

import { MapPin, Zap, Clock, Activity, Timer } from "lucide-react";
import { useLiveTimer } from "../../hooks/useLiveTimer";

const STATUS_STYLES = {
  ACTIVE:    "badge bg-vesper-cyan/10 text-vesper-cyan border border-vesper-cyan/30",
  COMPLETED: "badge bg-vesper-green/10 text-vesper-green border border-vesper-green/30",
  PENDING:   "badge bg-vesper-amber/10 text-vesper-amber border border-vesper-amber/30",
  FAILED:    "badge bg-vesper-red/10 text-vesper-red border border-vesper-red/30",
  ABORTED:   "badge bg-vesper-muted/10 text-vesper-muted border border-vesper-muted/30",
};

const PRIORITY_DOT = {
  CRITICAL: "bg-vesper-red animate-pulse",
  HIGH:     "bg-vesper-amber",
  MEDIUM:   "bg-vesper-cyan",
  LOW:      "bg-vesper-muted",
};

function CountdownBadge({ startedAt, status, estimatedMinutes }) {
  const { countdown, remaining, progress } = useLiveTimer(startedAt, status, estimatedMinutes);
  if (status !== "ACTIVE") return null;

  const urgent = remaining > 0 && remaining < 30;

  return (
    <span className={`badge font-mono text-[10px] ml-auto border ${
      urgent
        ? "bg-vesper-red/10 text-vesper-red border-vesper-red/30 animate-pulse"
        : "bg-vesper-cyan/10 text-vesper-cyan border-vesper-cyan/20"
    }`}>
      <Timer size={9} />
      {remaining === 0 ? "completing…" : countdown}
    </span>
  );
}

export default function MissionCard({ mission }) {
  const statusCls = STATUS_STYLES[mission.status] ?? STATUS_STYLES.PENDING;
  const dotCls    = PRIORITY_DOT[mission.priority] ?? "bg-vesper-muted";

  return (
    <div className="card hover:border-vesper-cyan/40 transition-colors duration-200 animate-slide-up">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 min-w-0">
          <span className={`w-2 h-2 rounded-full shrink-0 ${dotCls}`} />
          <span className="font-semibold text-white text-sm truncate max-w-[150px]">{mission.name}</span>
        </div>
        <span className={statusCls}>{mission.status}</span>
      </div>

      <div className="space-y-1.5 text-xs text-vesper-muted">
        <div className="flex items-center gap-2">
          <MapPin size={12} className="shrink-0" />
          <span>{mission.region}</span>
          <span className="ml-auto font-mono text-vesper-text/60">{mission.mission_type?.replace(/_/g, " ")}</span>
        </div>

        {mission.distance_km && (
          <div className="flex items-center gap-2">
            <Activity size={12} className="shrink-0" />
            <span>{mission.distance_km} km</span>
            {mission.status === "ACTIVE" ? (
              <CountdownBadge
                startedAt={mission.started_at}
                status={mission.status}
                estimatedMinutes={mission.estimated_duration_min}
              />
            ) : (
              mission.estimated_duration_min && (
                <span className="ml-auto flex items-center gap-1">
                  <Clock size={10} />
                  {Math.round(mission.estimated_duration_min)} min
                </span>
              )
            )}
          </div>
        )}

        {mission.battery_consumption_pct && (
          <div className="flex items-center gap-2">
            <Zap size={12} className="shrink-0" />
            <span className={mission.battery_consumption_pct > 70 ? "text-vesper-red" : "text-vesper-amber"}>
              {mission.battery_consumption_pct}% battery
            </span>
            <span className="ml-auto text-vesper-muted/60 font-mono">{mission.route_strategy}</span>
          </div>
        )}
      </div>

      {mission.assigned_drone_detail && (
        <div className="mt-3 pt-3 border-t border-vesper-border flex items-center gap-2 text-xs text-vesper-muted">
          <span className={`w-1.5 h-1.5 rounded-full ${
            mission.status === "ACTIVE" ? "bg-vesper-cyan animate-pulse" : "bg-vesper-cyan/40"
          }`} />
          <span className="font-mono">{mission.assigned_drone_detail.name}</span>
          <span className="ml-auto">{mission.assigned_drone_detail.drone_type}</span>
        </div>
      )}
    </div>
  );
}

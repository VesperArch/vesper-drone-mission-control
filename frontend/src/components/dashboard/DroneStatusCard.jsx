import { Battery, Zap } from "lucide-react";

const STATUS_COLOR = {
  IDLE:        "text-vesper-green",
  ACTIVE:      "text-vesper-cyan",
  MAINTENANCE: "text-vesper-amber",
  CHARGING:    "text-vesper-blue",
  RETURNING:   "text-vesper-muted",
};

const TYPE_LABEL = {
  SURVEILLANCE: "Surveillance",
  EMERGENCY:    "Emergency",
  DELIVERY:     "Delivery",
};

export default function DroneStatusCard({ drone }) {
  const statusColor = STATUS_COLOR[drone.status] ?? "text-vesper-muted";
  const battery = drone.battery_level ?? 0;
  const batteryColor =
    battery > 60 ? "bg-vesper-green" :
    battery > 30 ? "bg-vesper-amber" : "bg-vesper-red";

  return (
    <div className="card hover:border-vesper-border/80 transition-colors duration-200">
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="font-semibold text-white text-sm">{drone.name}</div>
          <div className="text-xs text-vesper-muted font-mono mt-0.5">{drone.model}</div>
        </div>
        <span className={`text-xs font-mono font-medium ${statusColor}`}>{drone.status}</span>
      </div>

      <div className="text-xs text-vesper-muted mb-3">
        {TYPE_LABEL[drone.drone_type] ?? drone.drone_type} · {drone.speed_kmh} km/h · {drone.range_km} km range
      </div>

      {/* Battery bar */}
      <div className="space-y-1">
        <div className="flex justify-between text-xs">
          <span className="flex items-center gap-1 text-vesper-muted">
            <Battery size={11} /> Battery
          </span>
          <span className="font-mono text-vesper-text">{battery.toFixed(0)}%</span>
        </div>
        <div className="h-1.5 bg-vesper-border rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${batteryColor}`}
            style={{ width: `${battery}%` }}
          />
        </div>
      </div>
    </div>
  );
}

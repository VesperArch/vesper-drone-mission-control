import { useEffect, useState, useCallback } from "react";
import { RefreshCw, MapPin, Clock, Zap, Route, Timer } from "lucide-react";
import { fetchMissions } from "../api/missions";
import MissionCard from "../components/dashboard/MissionCard";
import MissionTimeline from "../components/mission/MissionTimeline";
import DroneMap from "../components/map/DroneMap";
import { useLiveTimer } from "../hooks/useLiveTimer";

const FILTERS = ["ALL", "ACTIVE", "COMPLETED", "FAILED"];

function MissionDetailHeader({ mission }) {
  const { countdown, remaining, progress } = useLiveTimer(
    mission.started_at, mission.status, mission.estimated_duration_min
  );
  const urgent = mission.status === "ACTIVE" && remaining > 0 && remaining < 30;

  return (
    <div className="flex items-start justify-between">
      <div>
        <h2 className="text-white font-semibold text-lg">{mission.name}</h2>
        <p className="text-vesper-muted text-sm mt-0.5">
          {mission.mission_type?.replace(/_/g, " ")} · {mission.region}
        </p>
      </div>
      <div className="flex items-center gap-2">
        {mission.status === "ACTIVE" && (
          <span className={`badge font-mono text-sm border ${
            urgent
              ? "bg-vesper-red/10 text-vesper-red border-vesper-red/30 animate-pulse"
              : "bg-vesper-cyan/10 text-vesper-cyan border-vesper-cyan/30"
          }`}>
            <Timer size={10} className="animate-pulse" />
            {remaining === 0 ? "completing…" : countdown}
          </span>
        )}
        <span className={`badge text-sm px-3 py-1 ${
          mission.status === "COMPLETED" ? "bg-vesper-green/10 text-vesper-green border border-vesper-green/30" :
          mission.status === "ACTIVE"    ? "bg-vesper-cyan/10  text-vesper-cyan  border border-vesper-cyan/30"  :
          mission.status === "FAILED"    ? "bg-vesper-red/10   text-vesper-red   border border-vesper-red/30"   :
                                           "bg-vesper-muted/10 text-vesper-muted border border-vesper-muted/30"
        }`}>{mission.status}</span>
      </div>
    </div>
  );
}

export default function ActiveMissions() {
  const [missions, setMissions]   = useState([]);
  const [selected, setSelected]   = useState(null);
  const [filter, setFilter]       = useState("ALL");
  const [loading, setLoading]     = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    fetchMissions()
      .then((data) => {
        setMissions(data);
        // Keep selected in sync with fresh data
        setSelected((prev) => prev ? (data.find((m) => m.id === prev.id) ?? prev) : null);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    // Auto-refresh every 20s while any mission is active
    const id = setInterval(load, 20_000);
    return () => clearInterval(id);
  }, [load]);

  const filtered = filter === "ALL" ? missions : missions.filter((m) => m.status === filter);

  return (
    <div className="flex gap-5 h-full max-w-screen-xl">
      {/* Left: mission list */}
      <div className="w-72 shrink-0 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <span className="section-title">{filtered.length} Missions</span>
          <button
            onClick={load}
            className="p-1.5 rounded-lg hover:bg-vesper-border/40 text-vesper-muted hover:text-vesper-text transition-colors"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>
        </div>

        <div className="flex gap-1 bg-vesper-surface rounded-lg p-1 border border-vesper-border">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`flex-1 text-xs py-1.5 rounded-md transition-all font-medium ${
                filter === f
                  ? "bg-vesper-cyan/20 text-vesper-cyan"
                  : "text-vesper-muted hover:text-vesper-text"
              }`}
            >
              {f === "ALL" ? "All" : f.charAt(0) + f.slice(1).toLowerCase()}
            </button>
          ))}
        </div>

        <div className="space-y-2 overflow-y-auto flex-1">
          {filtered.map((m) => (
            <div
              key={m.id}
              onClick={() => setSelected(m)}
              className={`cursor-pointer transition-all duration-150 rounded-xl ${
                selected?.id === m.id ? "ring-1 ring-vesper-cyan" : ""
              }`}
            >
              <MissionCard mission={m} />
            </div>
          ))}
          {filtered.length === 0 && !loading && (
            <div className="card text-vesper-muted text-sm text-center py-10">
              No missions found
            </div>
          )}
        </div>
      </div>

      {/* Right: map + detail */}
      <div className="flex-1 flex flex-col gap-4 min-h-0 overflow-hidden">
        {selected ? (
          <>
            {/* Map */}
            <DroneMap mission={selected} height={280} />

            {/* Details */}
            <div className="flex-1 overflow-y-auto">
              <div className="card space-y-5 animate-fade-in">
                <MissionDetailHeader mission={selected} />

                <div className="glow-line" />

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                  {[
                    { icon: MapPin, label: "Distance",  val: `${selected.distance_km} km`                     },
                    { icon: Clock,  label: "Duration",  val: `${Math.round(selected.estimated_duration_min)} min` },
                    { icon: Zap,    label: "Battery",   val: `${selected.battery_consumption_pct}%`            },
                    { icon: Route,  label: "Strategy",  val: selected.route_strategy                           },
                  ].map(({ icon: Icon, label, val }) => (
                    <div key={label} className="bg-vesper-surface rounded-lg p-3 border border-vesper-border">
                      <div className="flex items-center gap-1.5 text-vesper-muted mb-1">
                        <Icon size={11} /> <span>{label}</span>
                      </div>
                      <div className="font-mono text-vesper-text font-medium">{val}</div>
                    </div>
                  ))}
                </div>

                {selected.waypoints?.length > 0 && (
                  <div>
                    <div className="label">Route Waypoints</div>
                    <div className="flex items-center gap-2 flex-wrap">
                      {selected.waypoints.map((wp, i) => (
                        <span key={i} className="badge bg-vesper-border/60 text-vesper-text">
                          {i > 0 && <span className="text-vesper-muted mr-1">→</span>}
                          {wp}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selected.route_notes && (
                  <div>
                    <div className="label">Route Notes</div>
                    <p className="text-xs text-vesper-muted bg-vesper-surface rounded-lg p-3 border border-vesper-border">
                      {selected.route_notes}
                    </p>
                  </div>
                )}

                <div>
                  <div className="section-title text-sm mb-3">Mission Timeline</div>
                  <MissionTimeline events={selected.events ?? []} />
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col gap-4">
            <DroneMap mission={null} height={280} />
            <p className="text-vesper-muted text-sm text-center">Select a mission to view its route</p>
          </div>
        )}
      </div>
    </div>
  );
}

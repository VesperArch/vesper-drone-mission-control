import { useEffect, useState } from "react";
import { Radio, Cpu, Activity, Zap } from "lucide-react";
import StatCard from "../components/dashboard/StatCard";
import MissionCard from "../components/dashboard/MissionCard";
import DroneStatusCard from "../components/dashboard/DroneStatusCard";
import EventFeed from "../components/dashboard/EventFeed";
import SystemStatus from "../components/dashboard/SystemStatus";
import { fetchStatus } from "../api/system";
import { fetchMissions } from "../api/missions";
import { fetchDrones } from "../api/drones";

export default function Dashboard() {
  const [stats, setStats]       = useState(null);
  const [missions, setMissions] = useState([]);
  const [drones, setDrones]     = useState([]);

  useEffect(() => {
    const load = () => {
      fetchStatus().then((d) => setStats(d.statistics)).catch(() => {});
      fetchMissions().then(setMissions).catch(() => {});
      fetchDrones().then(setDrones).catch(() => {});
    };
    load();
    const id = setInterval(load, 15_000);
    return () => clearInterval(id);
  }, []);

  const recentMissions = missions.slice(0, 4);

  return (
    <div className="space-y-6 max-w-screen-xl">
      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Active Drones"    value={stats?.active_drones}    icon={Radio}    accent="cyan"  sub="in operation" />
        <StatCard label="Active Missions"  value={stats?.active_missions}  icon={Activity} accent="amber" sub="in progress"  />
        <StatCard label="Total Missions"   value={stats?.total_missions}   icon={Cpu}      accent="green" sub="all time"     />
        <StatCard label="Events Fired"     value={stats?.total_events_fired} icon={Zap}   accent="red"   sub="this session" />
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left 2 cols */}
        <div className="lg:col-span-2 space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="section-title">Recent Missions</span>
              <span className="text-xs text-vesper-muted">{missions.length} total</span>
            </div>
            {recentMissions.length === 0 ? (
              <div className="card text-vesper-muted text-sm text-center py-10">
                No missions yet — create one to get started.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {recentMissions.map((m) => <MissionCard key={m.id} mission={m} />)}
              </div>
            )}
          </div>

          <div>
            <div className="section-title mb-3">Fleet Status</div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {drones.slice(0, 4).map((d) => <DroneStatusCard key={d.id} drone={d} />)}
            </div>
          </div>
        </div>

        {/* Right col */}
        <div className="space-y-4">
          <div className="h-72">
            <EventFeed />
          </div>
          <SystemStatus />
        </div>
      </div>
    </div>
  );
}

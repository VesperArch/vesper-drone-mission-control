import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { PlusCircle, Loader2, CheckCircle, AlertTriangle, ChevronDown } from "lucide-react";
import { fetchMetadata } from "../api/system";
import { fetchDrones } from "../api/drones";
import { createMission } from "../api/missions";
import MissionTimeline from "../components/mission/MissionTimeline";

const LABELS = {
  FLOOD_MONITORING:       "Flood Monitoring",
  COASTAL_PATROL:         "Coastal Patrol",
  EMERGENCY_DELIVERY:     "Emergency Delivery",
  TRAFFIC_SURVEILLANCE:   "Traffic Surveillance",
  ENVIRONMENTAL_MONITORING: "Environmental Monitoring",
  FASTEST:      "Fastest Route",
  SAFE:         "Safe Route",
  BATTERY_SAVING: "Battery Saving",
};

function Select({ label, id, value, onChange, options, placeholder }) {
  return (
    <div>
      <label className="label" htmlFor={id}>{label}</label>
      <div className="relative">
        <select id={id} value={value} onChange={(e) => onChange(e.target.value)} className="select-field pr-8">
          {placeholder && <option value="">{placeholder}</option>}
          {options.map((o) => (
            <option key={o} value={o}>{LABELS[o] ?? o}</option>
          ))}
        </select>
        <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-vesper-muted pointer-events-none" />
      </div>
    </div>
  );
}

export default function CreateMission() {
  const navigate = useNavigate();
  const [meta, setMeta]     = useState(null);
  const [drones, setDrones] = useState([]);
  const [form, setForm]     = useState({
    name: "",
    mission_type: "",
    region: "",
    priority: "MEDIUM",
    drone_id: "",
    route_strategy: "FASTEST",
  });
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState(null);

  useEffect(() => {
    fetchMetadata().then(setMeta).catch(() => {});
    fetchDrones().then(setDrones).catch(() => {});
  }, []);

  const field = (key) => (val) => setForm((f) => ({ ...f, [key]: val }));

  const idleDrones = drones.filter((d) => d.status === "IDLE" || d.status === "CHARGING");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.mission_type || !form.region || !form.drone_id) {
      setError("Please fill in all required fields.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await createMission(form);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.error ?? "Mission launch failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div className="max-w-2xl mx-auto space-y-4 animate-fade-in">
        <div className="card border-vesper-green/30 bg-vesper-green/5">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle size={20} className="text-vesper-green" />
            <span className="text-vesper-green font-semibold">Mission Completed Successfully</span>
          </div>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm mb-4">
            {[
              ["Mission",   result.name],
              ["Type",      result.mission_type?.replace(/_/g, " ")],
              ["Region",    result.region],
              ["Strategy",  result.route_strategy],
              ["Distance",  `${result.distance_km} km`],
              ["Duration",  `${Math.round(result.estimated_duration_min)} min`],
              ["Battery",   `${result.battery_consumption_pct}%`],
              ["Risk Score",`${result.weather_risk_score}`],
            ].map(([k, v]) => (
              <div key={k}>
                <span className="text-vesper-muted text-xs">{k}</span>
                <div className="text-vesper-text font-mono text-xs mt-0.5">{v}</div>
              </div>
            ))}
          </div>
          <div className="glow-line mb-4" />
          <div className="section-title text-sm mb-3">Mission Timeline</div>
          <MissionTimeline events={result.events ?? []} />
        </div>
        <div className="flex gap-3">
          <button className="btn-secondary" onClick={() => { setResult(null); setForm({ name: "", mission_type: "", region: "", priority: "MEDIUM", drone_id: "", route_strategy: "FASTEST" }); }}>
            New Mission
          </button>
          <button className="btn-primary" onClick={() => navigate("/missions")}>
            View All Missions
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-xl">
      <p className="text-vesper-muted text-sm mb-6">
        Configure and deploy a drone mission. The Facade pattern orchestrates drone selection,
        route strategy, and observer chain automatically.
      </p>

      <form onSubmit={handleSubmit} className="card space-y-5">
        <div>
          <label className="label" htmlFor="name">Mission Name *</label>
          <input
            id="name"
            type="text"
            className="input-field"
            placeholder="e.g. Flood Watch Alpha"
            value={form.name}
            onChange={(e) => field("name")(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          {meta && (
            <>
              <Select label="Mission Type *"   id="mission_type"    value={form.mission_type}    onChange={field("mission_type")}    options={meta.mission_types}    placeholder="Select type" />
              <Select label="Region *"          id="region"          value={form.region}          onChange={field("region")}          options={meta.regions}          placeholder="Select region" />
              <Select label="Priority"          id="priority"        value={form.priority}        onChange={field("priority")}        options={meta.priorities} />
              <Select label="Route Strategy"    id="route_strategy"  value={form.route_strategy}  onChange={field("route_strategy")}  options={meta.route_strategies} />
            </>
          )}
        </div>

        <div>
          <label className="label" htmlFor="drone">Assign Drone *</label>
          <div className="relative">
            <select
              id="drone"
              value={form.drone_id}
              onChange={(e) => field("drone_id")(e.target.value)}
              className="select-field pr-8"
            >
              <option value="">Select available drone</option>
              {idleDrones.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} — {d.drone_type} ({d.battery_level?.toFixed(0)}% batt)
                </option>
              ))}
            </select>
            <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-vesper-muted pointer-events-none" />
          </div>
          {idleDrones.length === 0 && (
            <p className="text-xs text-vesper-amber mt-1.5">No idle drones available. Check fleet status.</p>
          )}
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-vesper-red/10 border border-vesper-red/30">
            <AlertTriangle size={14} className="text-vesper-red shrink-0" />
            <span className="text-xs text-vesper-red">{error}</span>
          </div>
        )}

        <div className="glow-line" />

        <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
          {loading ? (
            <>
              <Loader2 size={15} className="animate-spin" />
              Deploying Mission…
            </>
          ) : (
            <>
              <PlusCircle size={15} />
              Launch Mission
            </>
          )}
        </button>
      </form>
    </div>
  );
}

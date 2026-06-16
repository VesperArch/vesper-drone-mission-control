import { useState, useEffect, useRef, useMemo } from "react";
import { MapContainer, TileLayer, Polyline, Marker, useMap } from "react-leaflet";
import L from "leaflet";

const REGION_COORDS = {
  "Centro":      [-22.9171, -42.8188],
  "Inoã":       [-22.9140, -42.9305],
  "Itaipuaçu":  [-22.9667, -43.0167],
  "Ponta Negra": [-22.9535, -42.6953],
  "São José":   [-22.9303, -42.8844],
  "Cordeirinho": [-22.9544, -42.7496],
};
const MARICA_CENTER = [-22.9171, -42.8188];
const DRONE_COLORS  = { SURVEILLANCE: "#00d4ff", EMERGENCY: "#ff3b5c", DELIVERY: "#00ff88" };
const REPLAY_SPEED  = 20; // real-time × faster for replay

function getCoords(name) {
  if (!name) return MARICA_CENTER;
  if (REGION_COORDS[name]) return REGION_COORDS[name];
  const key = Object.keys(REGION_COORDS).find(
    (k) => k.toLowerCase() === String(name).toLowerCase()
  );
  return key ? REGION_COORDS[key] : MARICA_CENTER;
}

function interpolate(coords, progress) {
  if (!coords?.length) return MARICA_CENTER;
  if (coords.length === 1) return coords[0];
  const p    = Math.max(0, Math.min(0.9999, progress));
  const segs = coords.length - 1;
  const g    = p * segs;
  const si   = Math.floor(g);
  const t    = g - si;
  const a    = coords[Math.min(si, segs - 1)];
  const b    = coords[Math.min(si + 1, segs)];
  return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
}

function makeDroneIcon(color, active) {
  const rings = active
    ? `<div style="position:absolute;top:50%;left:50%;width:28px;height:28px;border-radius:50%;
        background:${color}44;animation:drone-pulse 1.5s ease-out infinite;"></div>
       <div style="position:absolute;top:50%;left:50%;width:28px;height:28px;border-radius:50%;
        background:${color}22;animation:drone-pulse 1.5s ease-out 0.75s infinite;"></div>`
    : "";
  return L.divIcon({
    html: `<div style="position:relative;width:24px;height:24px;">
      ${rings}
      <svg viewBox="0 0 32 32" width="24" height="24"
        style="position:relative;z-index:2;filter:drop-shadow(0 0 6px ${color});">
        <ellipse cx="7"  cy="7"  rx="5" ry="2.5" fill="${color}" opacity="0.55"/>
        <ellipse cx="25" cy="7"  rx="5" ry="2.5" fill="${color}" opacity="0.55"/>
        <ellipse cx="7"  cy="25" rx="5" ry="2.5" fill="${color}" opacity="0.55"/>
        <ellipse cx="25" cy="25" rx="5" ry="2.5" fill="${color}" opacity="0.55"/>
        <line x1="7"  y1="7"  x2="16" y2="16" stroke="${color}" stroke-width="1.8" opacity="0.7"/>
        <line x1="25" y1="7"  x2="16" y2="16" stroke="${color}" stroke-width="1.8" opacity="0.7"/>
        <line x1="7"  y1="25" x2="16" y2="16" stroke="${color}" stroke-width="1.8" opacity="0.7"/>
        <line x1="25" y1="25" x2="16" y2="16" stroke="${color}" stroke-width="1.8" opacity="0.7"/>
        <circle cx="16" cy="16" r="4.5" fill="${color}"/>
        <circle cx="16" cy="16" r="2"   fill="#080c14"/>
      </svg>
    </div>`,
    className: "",
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
}

function makePinIcon(color) {
  return L.divIcon({
    html: `<div style="width:12px;height:12px;border-radius:50% 50% 50% 0;
      transform:rotate(-45deg);background:${color}33;border:2px solid ${color};"></div>`,
    className: "",
    iconSize: [12, 12],
    iconAnchor: [6, 12],
  });
}

// Forces Leaflet to recalculate container dimensions after mount
function MapResizer({ routeCoords }) {
  const map = useMap();

  useEffect(() => {
    const t = setTimeout(() => {
      map.invalidateSize();
      if (routeCoords?.length >= 2) {
        try {
          map.fitBounds(L.latLngBounds(routeCoords), { padding: [48, 48], maxZoom: 13 });
        } catch (_) {}
      }
    }, 120);
    return () => clearTimeout(t);
  // Re-fit when route changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [map, routeCoords?.map((c) => c.join()).join()]);

  return null;
}

export default function DroneMap({ mission, height = 280 }) {
  const [progress, setProgress] = useState(0);
  const timerRef = useRef(null);

  const droneType  = mission?.assigned_drone_detail?.drone_type ?? "SURVEILLANCE";
  const droneColor = DRONE_COLORS[droneType] ?? "#00d4ff";
  const isActive   = mission?.status === "ACTIVE";

  const routeCoords = useMemo(
    () => (mission?.waypoints ?? []).map(getCoords),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [mission?.waypoints?.join?.()]
  );

  // Stable icon — only recreate when color / active state changes
  const droneIcon = useMemo(() => makeDroneIcon(droneColor, isActive), [droneColor, isActive]);
  const originIcon = useMemo(() => makePinIcon("#00ff88"), []);
  const destIcon   = useMemo(() => makePinIcon("#ffaa00"), []);

  // Drive the animation
  useEffect(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (!mission || routeCoords.length < 2) return;

    const durationMs = (mission.estimated_duration_min ?? 5) * 60 * 1000;

    if (isActive && mission.started_at) {
      const start = new Date(mission.started_at).getTime();
      timerRef.current = setInterval(() => {
        setProgress(Math.min((Date.now() - start) / durationMs, 1));
      }, 300);
    } else {
      // Replay loop at REPLAY_SPEED× real time
      const replayMs = durationMs / REPLAY_SPEED;
      const began = Date.now();
      timerRef.current = setInterval(() => {
        setProgress(((Date.now() - began) % replayMs) / replayMs);
      }, 40);
    }

    return () => clearInterval(timerRef.current);
  }, [mission?.id, isActive, mission?.started_at, routeCoords.length]);

  const dronePos = routeCoords.length >= 2 ? interpolate(routeCoords, progress) : null;

  // Traveled portion of the route
  const traveledCoords = useMemo(() => {
    if (!dronePos || routeCoords.length < 2) return [];
    const segs  = routeCoords.length - 1;
    const g     = Math.max(0, Math.min(0.9999, progress)) * segs;
    const si    = Math.floor(g);
    return [...routeCoords.slice(0, si + 1), dronePos];
  }, [dronePos, routeCoords, progress]);

  return (
    <div
      className="relative rounded-xl overflow-hidden border border-vesper-border"
      style={{ width: "100%", height: `${height}px` }}
    >
      <MapContainer
        center={MARICA_CENTER}
        zoom={12}
        style={{ width: "100%", height: "100%" }}
        zoomControl
        attributionControl
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          subdomains="abcd"
          maxZoom={19}
        />

        <MapResizer routeCoords={routeCoords.length >= 2 ? routeCoords : null} />

        {routeCoords.length >= 2 && (
          <>
            {/* Full route (dim dashes) */}
            <Polyline
              positions={routeCoords}
              pathOptions={{ color: droneColor, weight: 2.5, opacity: 0.3, dashArray: "7 5" }}
            />

            {/* Traveled segment (bright) */}
            {traveledCoords.length >= 2 && (
              <Polyline
                positions={traveledCoords}
                pathOptions={{ color: droneColor, weight: 3.5, opacity: 0.9 }}
              />
            )}

            {/* Origin pin */}
            <Marker position={routeCoords[0]} icon={originIcon} />

            {/* Destination pin */}
            <Marker position={routeCoords[routeCoords.length - 1]} icon={destIcon} />

            {/* Animated drone */}
            {dronePos && <Marker position={dronePos} icon={droneIcon} />}
          </>
        )}
      </MapContainer>

      {/* HUD overlay */}
      {mission && (
        <div className="absolute bottom-3 left-3 z-[1000] flex flex-col gap-1.5 pointer-events-none">
          {routeCoords.length >= 2 && (
            <div className="flex items-center gap-2 bg-vesper-bg/85 backdrop-blur-sm border border-vesper-border rounded-lg px-2.5 py-1.5 text-xs font-mono">
              <span style={{ color: droneColor }} className="font-semibold">
                {mission.assigned_drone_detail?.name ?? "—"}
              </span>
              <span className="text-vesper-muted">
                {mission.waypoints?.[0]} → {mission.waypoints?.[mission.waypoints.length - 1]}
              </span>
            </div>
          )}
          <div className="flex items-center gap-2 bg-vesper-bg/85 backdrop-blur-sm border border-vesper-border rounded-lg px-2.5 py-1.5 text-xs font-mono">
            <span className="w-1.5 h-1.5 rounded-full" style={{ background: droneColor, animation: "drone-pulse 1.5s infinite" }} />
            <span className="text-vesper-text">{Math.round(progress * 100)}%</span>
            <span className="text-vesper-muted">·</span>
            <span className="text-vesper-text">{mission.distance_km} km</span>
            <span className="text-vesper-muted">·</span>
            <span style={{ color: isActive ? droneColor : "#4a6a8a" }}>
              {isActive ? "LIVE" : "REPLAY ×" + REPLAY_SPEED}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

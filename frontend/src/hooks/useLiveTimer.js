import { useState, useEffect } from "react";

function fmt(totalSeconds) {
  const s = Math.max(0, totalSeconds);
  return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
}

/**
 * Returns live timing data for an ACTIVE mission.
 * elapsed    — seconds since start
 * remaining  — seconds until estimated completion (counts down to 0)
 * countdown  — "MM:SS" display of remaining time
 * progress   — 0..1 fraction of estimated duration elapsed
 */
export function useLiveTimer(startedAt, status, estimatedMinutes) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!startedAt || status !== "ACTIVE") {
      setElapsed(0);
      return;
    }
    const start = new Date(startedAt).getTime();
    const tick = () => setElapsed(Math.max(0, Math.floor((Date.now() - start) / 1000)));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [startedAt, status]);

  const totalSec   = Math.round((estimatedMinutes ?? 0) * 60);
  const remaining  = Math.max(0, totalSec - elapsed);
  const progress   = totalSec > 0 ? Math.min(elapsed / totalSec, 1) : 0;

  return {
    elapsed,
    remaining,
    countdown: fmt(remaining),
    elapsedDisplay: fmt(elapsed),
    progress,
  };
}

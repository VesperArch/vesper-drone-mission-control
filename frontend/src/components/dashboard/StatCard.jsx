export default function StatCard({ label, value, sub, accent = "cyan", icon: Icon }) {
  const accentMap = {
    cyan:  "text-vesper-cyan border-vesper-cyan/20 bg-vesper-cyan/5",
    green: "text-vesper-green border-vesper-green/20 bg-vesper-green/5",
    amber: "text-vesper-amber border-vesper-amber/20 bg-vesper-amber/5",
    red:   "text-vesper-red border-vesper-red/20 bg-vesper-red/5",
  };

  return (
    <div className={`card border ${accentMap[accent]} animate-slide-up`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="label">{label}</div>
          <div className={`text-3xl font-bold font-mono ${accentMap[accent].split(" ")[0]}`}>
            {value ?? "—"}
          </div>
          {sub && <div className="text-xs text-vesper-muted mt-1">{sub}</div>}
        </div>
        {Icon && (
          <div className={`p-2.5 rounded-lg border ${accentMap[accent]}`}>
            <Icon size={18} />
          </div>
        )}
      </div>
    </div>
  );
}

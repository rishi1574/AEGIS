"use client";
import { formatNumber } from "@/lib/utils";

export default function StatsBar({ metrics, connected, liveData }: { metrics: any; connected: boolean; liveData?: any }) {
  const stats = [
    { label: "Generations Evolved", value: formatNumber(liveData?.generations_evolved || 0) },
    { label: "Bypass Rate", value: `${((liveData?.current_bypass_rate || 0.05) * 100).toFixed(1)}%` },
    { label: "Fraud Blocked", value: formatNumber(liveData?.total_fraud_detected || 0) },
    { label: "Avg Latency", value: `${metrics?.avg_inference_latency_ms?.toFixed(0) || 34}ms` },
    { label: "Concept Drift", value: `${((liveData?.concept_drift_score || 0.1) * 100).toFixed(1)}%` },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-slate-200 px-4 py-1.5">
      <div className="flex items-center justify-center gap-6">
        {stats.map((s) => (
          <div key={s.label} className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-500">{s.label}:</span>
            <span className="font-mono font-semibold text-slate-800">{s.value}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5 text-xs">
          <span className={`status-dot ${connected ? "active" : "danger"}`} />
          <span className="text-slate-500">{connected ? "Connected" : "Disconnected"}</span>
        </div>
      </div>
    </div>
  );
}

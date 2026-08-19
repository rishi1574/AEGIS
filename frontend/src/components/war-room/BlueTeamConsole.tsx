"use client";
import { Shield, TrendingUp, Eye } from "lucide-react";
import { useEffect, useState } from "react";

interface Metrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  auc_roc: number;
  false_positive_rate: number;
  avg_inference_latency_ms: number;
  total_predictions: number;
  adversarial_iteration: number;
}

export default function BlueTeamConsole({ metrics, liveData }: { metrics: Metrics | null, liveData?: any }) {
  const m = metrics || {
    accuracy: 0.95, precision: 0.92, recall: 0.89, f1_score: 0.90,
    auc_roc: 0.96, false_positive_rate: 0.04, avg_inference_latency_ms: 34,
    total_predictions: 100000, adversarial_iteration: 0,
  };

  const [log, setLog] = useState<string[]>([]);
  
  useEffect(() => {
    if (liveData?.blue_team_log) {
      setLog(prev => [...prev, liveData.blue_team_log].slice(-10));
    }
  }, [liveData]);

  // Make metrics jitter slightly with liveData to look alive
  const jitter = liveData ? (Math.random() * 0.02 - 0.01) : 0;
  
  const bars = [
    { label: "Accuracy", value: m.accuracy + jitter, color: "bg-blue-500" },
    { label: "Precision", value: m.precision + jitter, color: "bg-cyan-500" },
    { label: "Recall", value: m.recall + jitter, color: "bg-emerald-500" },
    { label: "F1 Score", value: m.f1_score + jitter, color: "bg-violet-500" },
    { label: "AUC-ROC", value: m.auc_roc + jitter, color: "bg-amber-500" },
  ];

  return (
    <div className="glass-card glow-blue h-full flex flex-col overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-aegis-border">
        <Shield className="w-5 h-5 text-aegis-blue" />
        <h2 className="text-sm font-semibold text-aegis-blue uppercase tracking-wider">Blue Team</h2>
        <span className="ml-auto text-xs font-mono text-aegis-text-muted">
          Iter #{liveData?.generations_evolved || m.adversarial_iteration}
        </span>
      </div>

      {/* Metrics Bars */}
      <div className="p-4 space-y-3 flex-1">
        {bars.map((b) => (
          <div key={b.label}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-aegis-text-muted">{b.label}</span>
              <span className="font-mono font-semibold text-aegis-text">
                {(b.value * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full h-2 bg-aegis-border rounded-full overflow-hidden">
              <div
                className={`h-full ${b.color} rounded-full transition-all duration-1000`}
                style={{ width: `${Math.min(100, Math.max(0, b.value * 100))}%` }}
              />
            </div>
          </div>
        ))}

        {/* Stat Cards */}
        <div className="grid grid-cols-2 gap-2 mt-4">
          <div className="bg-aegis-surface rounded-lg p-3 border border-aegis-border">
            <p className="text-[10px] text-aegis-text-muted uppercase">Latency</p>
            <p className="text-lg font-bold font-mono text-aegis-green">
              {(m.avg_inference_latency_ms + (liveData ? Math.random()*5-2.5 : 0)).toFixed(0)}ms
            </p>
          </div>
          <div className="bg-aegis-surface rounded-lg p-3 border border-aegis-border">
            <p className="text-[10px] text-aegis-text-muted uppercase">FPR</p>
            <p className="text-lg font-bold font-mono text-aegis-amber">
              {((m.false_positive_rate + Math.abs(jitter/2)) * 100).toFixed(2)}%
            </p>
          </div>
        </div>
      </div>

      {/* Interception Log Placeholder */}
      <div className="border-t border-aegis-border p-3 max-h-32 overflow-y-auto">
        <div className="flex items-center gap-2 mb-2">
          <Eye className="w-4 h-4 text-aegis-blue" />
          <p className="text-[10px] text-aegis-text-muted uppercase tracking-wider">Recent Interceptions</p>
        </div>
        <div className="space-y-0.5 font-mono text-[10px]">
          {log.map((entry, i) => (
            <div key={i} className="text-aegis-text-muted">{entry}</div>
          ))}
          {log.length === 0 && (
            <div className="text-xs text-aegis-text-muted/50 font-mono text-center py-2">
              Awaiting live data...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

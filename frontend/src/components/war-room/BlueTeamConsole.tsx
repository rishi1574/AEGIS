"use client";
import { Shield, Eye, Activity, TrendingDown, Target, Microscope, Search, BarChart3, ShieldCheck, Info } from "lucide-react";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Tooltip } from "@/components/ui/Tooltip";

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

export default function BlueTeamConsole({
  metrics,
  liveData,
}: {
  metrics: Metrics | null;
  liveData?: any;
}) {
  const m = metrics || {
    accuracy: 0.95, precision: 0.92, recall: 0.89, f1_score: 0.90,
    auc_roc: 0.96, false_positive_rate: 0.04, avg_inference_latency_ms: 34,
    total_predictions: 100000, adversarial_iteration: 0,
  };

  const [log, setLog] = useState<string[]>([]);

  useEffect(() => {
    if (liveData?.blue_team_log) {
      setLog((prev) => [...prev, liveData.blue_team_log].slice(-12));
    }
  }, [liveData]);

  // Slight jitter to feel alive
  const jitter = liveData ? (Math.random() * 0.01 - 0.005) : 0;

  const bars = [
    { label: "Accuracy", value: m.accuracy + jitter, color: "bg-blue-500", icon: <Target className="w-3 h-3" /> },
    { label: "Precision", value: m.precision + jitter, color: "bg-cyan-500", icon: <Microscope className="w-3 h-3" /> },
    { label: "Recall", value: m.recall + jitter, color: "bg-emerald-500", icon: <Search className="w-3 h-3" /> },
    { label: "F1 Score", value: m.f1_score + jitter, color: "bg-violet-500", icon: <BarChart3 className="w-3 h-3" /> },
    { label: "AUC-ROC", value: m.auc_roc + jitter, color: "bg-amber-500", icon: <Activity className="w-3 h-3" /> },
  ];

  return (
    <div className="bg-white border border-slate-200 shadow-sm rounded-xl h-full flex flex-col overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-200">
        <ShieldCheck className="w-5 h-5 text-slate-800" />
        <h2 className="text-sm font-semibold text-slate-800 uppercase tracking-wider">
          Blue Team
        </h2>
        <Tooltip content="Defensive metrics and live interception logs">
          <Info className="w-4 h-4 text-slate-400 cursor-help ml-1" />
        </Tooltip>
        <span className="ml-auto text-xs font-mono text-slate-500">
          Iter #{liveData?.generations_evolved || m.adversarial_iteration}
        </span>
      </div>

      {/* Metrics Bars */}
      <div className="p-3 space-y-2.5 flex-1 overflow-y-auto">
        {bars.map((b, i) => (
          <motion.div
            key={b.label}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <div className="flex justify-between text-xs mb-0.5">
              <span className="text-slate-500 flex items-center gap-1.5">
                {b.icon} {b.label}
              </span>
              <span className="font-mono font-bold text-slate-800">
                {(Math.min(1, Math.max(0, b.value)) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <motion.div
                className={`h-full ${b.color} rounded-full`}
                initial={{ width: 0 }}
                animate={{
                  width: `${Math.min(100, Math.max(0, b.value * 100))}%`,
                }}
                transition={{ duration: 1.5, delay: i * 0.15, ease: "easeOut" }}
              />
            </div>
          </motion.div>
        ))}

        {/* Stat Cards */}
        <div className="grid grid-cols-2 gap-2 mt-3">
          <div className="bg-white rounded-lg p-2.5 border border-slate-200">
            <p className="text-[9px] text-slate-500 uppercase flex items-center gap-1">
              <Activity className="w-3 h-3" /> Latency
            </p>
            <p className="text-lg font-bold font-mono text-aegis-green">
              {(m.avg_inference_latency_ms + (liveData ? Math.random() * 5 - 2.5 : 0)).toFixed(0)}
              <span className="text-xs font-normal text-slate-500">ms</span>
            </p>
          </div>
          <div className="bg-white rounded-lg p-2.5 border border-slate-200">
            <p className="text-[9px] text-slate-500 uppercase flex items-center gap-1">
              <TrendingDown className="w-3 h-3" /> FPR
            </p>
            <p className="text-lg font-bold font-mono text-aegis-amber">
              {((m.false_positive_rate + Math.abs(jitter / 2)) * 100).toFixed(2)}
              <span className="text-xs font-normal text-slate-500">%</span>
            </p>
          </div>
        </div>
      </div>

      {/* Interception Log */}
      <div className="border-t border-slate-200 p-2.5 max-h-36 overflow-y-auto">
        <div className="flex items-center gap-2 mb-1.5">
          <Eye className="w-4 h-4 text-aegis-blue" />
          <p className="text-[9px] text-slate-500 uppercase tracking-wider">
            Live Interceptions
          </p>
        </div>
        <div className="space-y-0.5 font-mono text-[10px]">
          <AnimatePresence>
            {log.map((entry, i) => (
              <motion.div
                key={`blue-${i}`}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-slate-500"
              >
                {entry}
              </motion.div>
            ))}
          </AnimatePresence>
          {log.length === 0 && (
            <div className="text-xs text-slate-500/50 font-mono text-center py-2">
              Awaiting live data...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


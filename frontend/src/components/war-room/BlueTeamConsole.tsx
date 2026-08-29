"use client";
import { Shield, Eye, Activity, TrendingDown, Target, Microscope, Search, BarChart3, ShieldCheck, Info } from"lucide-react";
import { useEffect, useState } from"react";
import { motion, AnimatePresence } from"framer-motion";
import { Tooltip } from"@/components/ui/Tooltip";

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip as RechartsTooltip } from"recharts";

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

  // Merge live battle metrics into display when available
  const live = liveData?.live_blue_metrics;
  const displayM = live ? {
    ...m,
    accuracy: live.accuracy ?? m.accuracy,
    precision: live.precision ?? m.precision,
    recall: live.recall ?? m.recall,
    f1_score: live.f1_score ?? m.f1_score,
    auc_roc: live.auc_roc ?? m.auc_roc,
    false_positive_rate: live.false_positive_rate ?? m.false_positive_rate,
    avg_inference_latency_ms: live.avg_inference_latency_ms ?? m.avg_inference_latency_ms,
  } : m;

  const [log, setLog] = useState<string[]>([]);

  useEffect(() => {
    if (liveData?.blue_team_log) {
      setLog((prev) => [...prev, liveData.blue_team_log].slice(-12));
    }
  }, [liveData]);

  // Slight jitter to feel alive
  const jitter = liveData ? (Math.random() * 0.01 - 0.005) : 0;

  const radarData = [
    { subject: 'Accuracy', value: Math.round((displayM.accuracy + jitter) * 100) },
    { subject: 'Precision', value: Math.round((displayM.precision + jitter) * 100) },
    { subject: 'Recall', value: Math.round((displayM.recall + jitter) * 100) },
    { subject: 'F1 Score', value: Math.round((displayM.f1_score + jitter) * 100) },
    { subject: 'AUC-ROC', value: Math.round((displayM.auc_roc + jitter) * 100) },
 ];

 return (
 <div className="bg-white border border-slate-200 shadow-sm h-full flex flex-col overflow-hidden">
 <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-200">
 
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

 {/* Metrics Radar Chart */}
 <div className="p-3 flex-1 flex flex-col min-h-0">
 <div className="flex-1 w-full relative min-h-[150px]">
 <ResponsiveContainer width="100%" height="100%">
 <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
 <PolarGrid stroke="#eaebf0" />
 <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 10, fontWeight: 500 }} />
 <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
 <Radar
 name="Performance"
 dataKey="value"
 stroke="#3b82f6"
 strokeWidth={2.5}
 fill="#3b82f6"
 fillOpacity={0.2}
 isAnimationActive={true}
 animationDuration={800}
 />
 <RechartsTooltip 
 contentStyle={{ borderRadius: '8px', border: '1px solid #eaebf0', fontSize: '11px', fontWeight: 'bold', boxShadow:"0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
 itemStyle={{ color: '#1a1f71' }}
 />
 </RadarChart>
 </ResponsiveContainer>
 </div>

 {/* Stat Cards */}
 <div className="grid grid-cols-2 gap-2 mt-3">
 <div className="bg-white p-2.5 border border-slate-200 shadow-sm">
 <p className="text-[9px] text-slate-500 uppercase flex items-center gap-1">
 <Activity className="w-3 h-3 text-aegis-green" /> Latency
 </p>
 <p className="text-lg font-bold font-mono text-aegis-green">
 {(displayM.avg_inference_latency_ms + (liveData ? Math.random() * 5 - 2.5 : 0)).toFixed(0)}
 <span className="text-xs font-normal text-slate-500 ml-0.5">ms</span>
 </p>
 </div>
 <div className="bg-white p-2.5 border border-slate-200 shadow-sm">
 <p className="text-[9px] text-slate-500 uppercase flex items-center gap-1">
 <TrendingDown className="w-3 h-3 text-aegis-amber" /> FPR
 </p>
 <p className="text-lg font-bold font-mono text-aegis-amber">
 {((displayM.false_positive_rate + Math.abs(jitter / 2)) * 100).toFixed(2)}
 <span className="text-xs font-normal text-slate-500 ml-0.5">%</span>
 </p>
 </div>
 </div>
 </div>

      {/* Interception Log */}
      <div className="border-t border-slate-200 p-2.5">
        <div className="flex items-center gap-2 mb-1.5">
          <p className="text-[9px] text-slate-500 uppercase tracking-wider font-bold">
            Live Interceptions
          </p>
          {log.length > 0 && (
            <span className="text-[9px] font-mono text-slate-400 ml-auto">{log.length} events</span>
          )}
        </div>
        <div className="space-y-1 max-h-[120px] overflow-y-auto">
          <AnimatePresence>
            {log.map((entry, i) => {
              const isBlocked = entry.toLowerCase().includes("block") || entry.toLowerCase().includes("intercept") || entry.toLowerCase().includes("caught");
              const isDetect = entry.toLowerCase().includes("detect") || entry.toLowerCase().includes("classif") || entry.toLowerCase().includes("monitor");
              return (
                <motion.div
                  key={`blue-${i}`}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`flex items-start gap-1.5 p-1.5 text-[10px] border-l-2 ${
                    isBlocked ? "border-red-400 bg-red-50/50" :
                    isDetect ? "border-amber-400 bg-amber-50/50" :
                    "border-blue-400 bg-blue-50/50"
                  }`}
                >
                  <span className={`text-[8px] font-mono shrink-0 mt-0.5 ${
                    isBlocked ? "text-red-500" : isDetect ? "text-amber-500" : "text-blue-500"
                  }`}>
                    {isBlocked ? "🛡️" : isDetect ? "🔍" : "📡"}
                  </span>
                  <span className="text-slate-600 leading-tight">{entry}</span>
                </motion.div>
              );
            })}
          </AnimatePresence>
          {log.length === 0 && (
            <div className="text-[10px] text-slate-400 text-center py-3 italic">
              Launch an attack to see live interceptions...
            </div>
          )}
        </div>
      </div>
 </div>
 );
}

"use client";
import { useEffect, useState } from"react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from"recharts";
import { TrendingUp, Activity } from"lucide-react";
import { useApi } from"@/hooks/useApi";

// Start with a few baseline points showing initial state
const INITIAL_DATA = Array.from({ length: 5 }, (_, i) => ({
  iteration: i + 1,
  blue_accuracy: 0.5,
  red_bypass: 0.5,
}));

export default function ConceptDriftChart({ liveData }: { liveData?: any }) {
  const [data, setData] = useState(INITIAL_DATA);

  useEffect(() => {
    if (liveData && liveData.battle_phase && liveData.battle_phase !== "IDLE") {
      setData((prev) => {
        // Use live battle metrics for accurate real-time tracking
        const blueAcc = liveData.live_blue_metrics?.accuracy ?? (1.0 - (liveData.current_bypass_rate || 0.05));
        const redBypass = liveData.red_team_success_rate ?? liveData.current_bypass_rate ?? 0.05;
        const newPoint = {
          iteration: liveData.battle_tick || (prev[prev.length - 1].iteration + 1),
          blue_accuracy: blueAcc,
          red_bypass: redBypass,
        };
        return [...prev.slice(-29), newPoint];
      });
    }
  }, [liveData]);

 return (
 <div className="bg-white border border-slate-200 shadow-sm h-full flex flex-col">
 <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-200">
 
 <h2 className="text-sm font-semibold text-slate-800 uppercase tracking-wider">
 Adversarial Co-Evolution
 </h2>
 <span className="ml-auto text-[10px] text-slate-500 font-mono bg-slate-50 px-2 py-1 border border-slate-200">
        {data.length} BATTLE TICKS
 </span>
 </div>
 <div className="flex-1 p-3">
 <ResponsiveContainer width="100%" height="100%">
 <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
 <defs>
 <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
 <stop offset="5%" stopColor="#1a1f71" stopOpacity={0.2} />
 <stop offset="95%" stopColor="#1a1f71" stopOpacity={0} />
 </linearGradient>
 <linearGradient id="redGrad" x1="0" y1="0" x2="0" y2="1">
 <stop offset="5%" stopColor="#d92d20" stopOpacity={0.2} />
 <stop offset="95%" stopColor="#d92d20" stopOpacity={0} />
 </linearGradient>
 </defs>
 <CartesianGrid strokeDasharray="3 3" stroke="#eaebf0" />
 <XAxis dataKey="iteration" tick={{ fontSize: 10, fill:"#64748b" }} axisLine={{ stroke: '#cbd5e1' }} tickLine={{ stroke: '#cbd5e1' }} />
 <YAxis tick={{ fontSize: 10, fill:"#64748b" }} domain={[0, 1]}
 tickFormatter={(v: number) => `${(v*100).toFixed(0)}%`} axisLine={{ stroke: '#cbd5e1' }} tickLine={{ stroke: '#cbd5e1' }} />
 <Tooltip
 contentStyle={{ background:"#ffffff", border:"1px solid #eaebf0", borderRadius: 8, fontSize: 12, boxShadow:"0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
 labelStyle={{ color:"#1e293b", fontWeight:"bold", marginBottom:"4px" }}
 itemStyle={{ padding:"2px 0" }}
 formatter={(value: any, name: any) => [
 `${(Number(value) * 100).toFixed(1)}%`,
 name ==="blue_accuracy" ?" Blue Team Accuracy" :" Red Team Bypass"
 ]}
 />
 <Area type="monotone" dataKey="blue_accuracy" stroke="#1a1f71" strokeWidth={2.5}
 fillOpacity={1} fill="url(#blueGrad)" dot={false} />
 <Area type="monotone" dataKey="red_bypass" stroke="#d92d20" strokeWidth={2.5}
 fillOpacity={1} fill="url(#redGrad)" dot={false} />
 </AreaChart>
 </ResponsiveContainer>
 </div>
 </div>
 );
}

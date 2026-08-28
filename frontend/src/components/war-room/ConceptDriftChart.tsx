"use client";
import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import { TrendingUp, Activity } from "lucide-react";
import { useApi } from "@/hooks/useApi";

// Demo data simulating adversarial co-evolution
const DEMO_DATA = Array.from({ length: 30 }, (_, i) => {
  const baseBlue = 0.85 + (i / 30) * 0.10;
  const redSpike = (i % 7 === 5) ? 0.15 : 0;
  return {
    iteration: i + 1,
    blue_accuracy: Math.min(0.98, baseBlue - redSpike * 0.8 + Math.random() * 0.02),
    red_bypass: Math.max(0, 0.15 - (i / 30) * 0.10 + redSpike + (Math.random() - 0.5) * 0.03),
  };
});

export default function ConceptDriftChart({ liveData }: { liveData?: any }) {
  const [data, setData] = useState(DEMO_DATA);

  useEffect(() => {
    if (liveData) {
      setData((prev) => {
        const newData = [...prev.slice(-29), {
          iteration: liveData.generations_evolved || prev[prev.length-1].iteration + 1,
          blue_accuracy: 1.0 - (liveData.concept_drift_score || 0.1),
          red_bypass: liveData.current_bypass_rate || 0.05,
        }];
        return newData;
      });
    }
  }, [liveData]);

  return (
    <div className="bg-white border border-slate-200 shadow-sm rounded-xl h-full flex flex-col">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-200">
        
        <h2 className="text-sm font-semibold text-slate-800 uppercase tracking-wider">
          Adversarial Co-Evolution
        </h2>
        <span className="ml-auto text-[10px] text-slate-500 font-mono bg-slate-50 px-2 py-1 rounded border border-slate-200">
          {data.length} ITERATIONS
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
            <XAxis dataKey="iteration" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={{ stroke: '#cbd5e1' }} tickLine={{ stroke: '#cbd5e1' }} />
            <YAxis tick={{ fontSize: 10, fill: "#64748b" }} domain={[0, 1]}
                   tickFormatter={(v: number) => `${(v*100).toFixed(0)}%`} axisLine={{ stroke: '#cbd5e1' }} tickLine={{ stroke: '#cbd5e1' }} />
            <Tooltip
              contentStyle={{ background: "#ffffff", border: "1px solid #eaebf0", borderRadius: 8, fontSize: 12, boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
              labelStyle={{ color: "#1e293b", fontWeight: "bold", marginBottom: "4px" }}
              itemStyle={{ padding: "2px 0" }}
              formatter={(value: any, name: any) => [
                `${(Number(value) * 100).toFixed(1)}%`,
                name === "blue_accuracy" ? " Blue Team Accuracy" : " Red Team Bypass"
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

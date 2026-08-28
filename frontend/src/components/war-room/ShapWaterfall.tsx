"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { Brain } from "lucide-react";

interface Props {
  shapValues: Record<string, number> | null;
  transactionId?: string;
}

export default function ShapWaterfall({ shapValues, transactionId }: Props) {
  if (!shapValues) {
    return (
      <div className="text-xs text-slate-500 text-center py-6">
        Click a transaction to see SHAP explanation
      </div>
    );
  }

  const featureMap: Record<string, string> = {
    amount: "Transaction Velocity Z-Score",
    distance: "Geospatial Anomaly (haversine)",
    time_delta: "Temporal Frequency Spike",
    mcc_risk: "Merchant Category Risk Index",
    device_id: "Device Fingerprint Entropy",
    ip_risk: "IP Subnet Risk Probability",
    velocity_24h: "24h Velocity Z-Score Spike",
    graph_centrality: "Network Mule Centrality",
    amount_log: "Log-Transformed Volume Anomaly",
    time_of_day: "Temporal Behavioral Deviation",
    // Custom shorter mappings for long feature names
    avg_monthly_transaction_count: "Avg Monthly Txns",
    avg_monthlytransactioncount: "Avg Monthly Txns",
    amount_vs_income_ratio: "Amount/Income Ratio",
    amount_vsincome_ratio: "Amount/Income Ratio",
    transactionchannel: "Transaction Channel",
    transaction_channel: "Transaction Channel",
  };

  const data = Object.entries(shapValues)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 6)
    .map(([feature, value]) => ({
      feature: featureMap[feature.toLowerCase()] || feature.replace(/_/g, " ").replace(/enc$/, "").toUpperCase(),
      value: Number(value.toFixed(4)),
    }));

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-1">
        <p className="text-[10px] text-slate-800 font-bold uppercase tracking-wider flex items-center gap-1.5">
          SHAP EXPLANATION
        </p>
        <span className="text-[9px] font-mono text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded border border-slate-200">
          {transactionId || "LIVE"}
        </span>
      </div>
      <div className="flex-1 min-h-0 relative -ml-4 mt-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 110, right: 10, top: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eaebf0" horizontal={false} />
            <XAxis type="number" tick={{ fontSize: 9, fill: "#64748b" }} axisLine={{ stroke: '#cbd5e1' }} tickLine={{ stroke: '#cbd5e1' }} />
            <YAxis type="category" dataKey="feature" tick={{ fontSize: 9, fill: "#64748b" }} width={110} axisLine={false} tickLine={false} />
            <Tooltip
              cursor={{ fill: '#f8fafc' }}
              contentStyle={{ background: "#ffffff", border: "1px solid #eaebf0", borderRadius: 8, fontSize: 11, boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
              itemStyle={{ color: '#0f172a' }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={12}>
              {data.map((entry, i) => (
                <Cell key={i} fill={entry.value > 0 ? "#d92d20" : "#027a48"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

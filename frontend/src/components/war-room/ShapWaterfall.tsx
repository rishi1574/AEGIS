"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface Props {
  shapValues: Record<string, number> | null;
  transactionId?: string;
}

export default function ShapWaterfall({ shapValues, transactionId }: Props) {
  if (!shapValues) {
    return (
      <div className="text-xs text-aegis-text-muted text-center py-6">
        Click a transaction to see SHAP explanation
      </div>
    );
  }

  const data = Object.entries(shapValues)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 6)
    .map(([feature, value]) => ({
      feature: feature.replace(/_/g, " ").replace(/enc$/, ""),
      value: Number(value.toFixed(4)),
    }));

  return (
    <div>
      <p className="text-[10px] text-aegis-text-muted mb-2 font-mono">
        SHAP — {transactionId || "Transaction"}
      </p>
      <ResponsiveContainer width="100%" height={150}>
        <BarChart data={data} layout="vertical" margin={{ left: 80, right: 10, top: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 9, fill: "#94a3b8" }} />
          <YAxis type="category" dataKey="feature" tick={{ fontSize: 9, fill: "#94a3b8" }} width={80} />
          <Tooltip contentStyle={{ background: "#1a2235", border: "1px solid #1e293b", borderRadius: 8, fontSize: 11 }} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.value > 0 ? "#ef4444" : "#3b82f6"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

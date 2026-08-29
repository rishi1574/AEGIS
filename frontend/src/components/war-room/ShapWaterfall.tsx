"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from"recharts";
import { Brain } from"lucide-react";

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
 amount:"Velocity Z-Score",
 distance:"Geo Anomaly",
 time_delta:"Time Freq Spike",
 mcc_risk:"Merchant Risk",
 device_id:"Device Entropy",
 ip_risk:"IP Risk Prob",
 velocity_24h:"24h Vol Spike",
 graph_centrality:"Mule Centrality",
 amount_log:"Volume Anomaly",
 time_of_day:"Time Deviation",
 // Custom shorter mappings for long feature names
 "avg monthly transaction count":"Avg M. Txns",
 "amount vs income ratio":"Amt/Inc Ratio",
 "avg monthly spending":"Avg M. Spend",
 "amount deviation from normal":"Amt Deviation",
 "amount spent in last 24h":"24h Spend Amt",
 "amount vs avg spend ratio":"Amt/Avg Spend",
 "devices used in 7 days":"7d Devices",
 "first-time receiver":"New Receiver",
 "international transaction":"Intl Txn",
 "merchant category risk":"Merchant Risk",
 "payment channel type":"Channel Type",
 "round amount flag":"Round Amount",
 "time since last transaction":"Time Since Txn",
 "transaction velocity anomaly":"Txn Vel Spike",
 "transactions in last 24h":"24h Txns",
 "transactions in last hour":"1h Txns",
 "unique receivers in 24h":"24h Receivers",
 // Legacy backups
 avg_monthly_transaction_count:"Avg M. Txns",
 amount_vs_income_ratio:"Amt/Inc Ratio",
 transactionchannel:"Txn Channel",
 transaction_channel:"Txn Channel",
 };

 const data = Object.entries(shapValues)
 .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
 .slice(0, 6)
 .map(([feature, value]) => {
   // Strip trailing enc or _enc before lookup
   const cleanKey = feature.toLowerCase().replace(/_?enc$/i,"");
   let label = featureMap[cleanKey];
   if (!label) {
     label = feature.replace(/_/g," ").replace(/_?enc$/i,"").toUpperCase();
     if (label.length > 13) label = label.slice(0, 11) + "..";
   }
   return { feature: label, value: Number(value.toFixed(4)) };
 });

 return (
 <div className="h-full flex flex-col">
 <div className="flex items-center justify-between mb-1">
 <p className="text-[10px] text-slate-800 font-bold uppercase tracking-wider flex items-center gap-1.5">
 SHAP EXPLANATION
 </p>
 <span className="text-[9px] font-mono text-slate-400 bg-slate-50 px-1.5 py-0.5 border border-slate-200">
 {transactionId ||"LIVE"}
 </span>
 </div>
 <div className="flex-1 min-h-0 relative -ml-8 mt-2">
 <ResponsiveContainer width="100%" height="100%">
 <BarChart data={data} layout="vertical" margin={{ left: 85, right: 10, top: 0, bottom: 0 }}>
 <CartesianGrid strokeDasharray="3 3" stroke="#eaebf0" horizontal={false} />
 <XAxis type="number" tick={{ fontSize: 9, fill:"#64748b" }} axisLine={{ stroke: '#cbd5e1' }} tickLine={{ stroke: '#cbd5e1' }} />
 <YAxis type="category" dataKey="feature" tick={{ fontSize: 9, fill:"#64748b" }} width={85} axisLine={false} tickLine={false} />
 <Tooltip
 cursor={{ fill: '#f8fafc' }}
 contentStyle={{ background:"#ffffff", border:"1px solid #eaebf0", borderRadius: 8, fontSize: 11, boxShadow:"0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
 itemStyle={{ color: '#0f172a' }}
 />
 <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={12}>
 {data.map((entry, i) => (
 <Cell key={i} fill={entry.value > 0 ?"#d92d20" :"#027a48"} />
 ))}
 </Bar>
 </BarChart>
 </ResponsiveContainer>
 </div>
 </div>
 );
}

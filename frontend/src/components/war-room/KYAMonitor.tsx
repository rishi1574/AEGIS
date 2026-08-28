"use client";
import { Bot, ShieldCheck, ShieldX } from "lucide-react";
import { motion } from "framer-motion";

const DEMO_EVENTS = [
  { id: 1, agent: "ShopBot-A42", action: "Purchase ₹29.99 BT Speaker", status: "allowed", reason: "Within spending limit" },
  { id: 2, agent: "ShopBot-A42", action: "Add ₹500 Gift Card", status: "blocked", reason: "Prompt injection detected in product page" },
  { id: 3, agent: "PayBot-M17", action: "50,000 × ₹0.01 micro-txns", status: "blocked", reason: "Velocity anomaly: machine-speed burst" },
  { id: 4, agent: "TravelBot-R8", action: "Book flight ₹12,400", status: "allowed", reason: "Matches user intent profile" },
];

export default function KYAMonitor() {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-2 mb-2">
        <Bot className="w-4 h-4 text-aegis-purple" />
        <p className="text-[10px] text-slate-500 uppercase tracking-wider">Know Your Agent (AP4M)</p>
      </div>
      {DEMO_EVENTS.map((evt, i) => (
        <motion.div
          key={evt.id}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className={`p-2 rounded-lg border text-[11px] ${
            evt.status === "blocked"
              ? "border-red-500/30 bg-red-500/5"
              : "border-green-500/30 bg-green-500/5"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-mono font-semibold text-slate-800">{evt.agent}</span>
            {evt.status === "blocked" ? (
              <ShieldX className="w-3.5 h-3.5 text-red-400" />
            ) : (
              <ShieldCheck className="w-3.5 h-3.5 text-green-400" />
            )}
          </div>
          <p className="text-slate-500 mt-0.5">{evt.action}</p>
          <p className="text-[9px] text-slate-500/70 mt-0.5 italic">{evt.reason}</p>
        </motion.div>
      ))}
    </div>
  );
}

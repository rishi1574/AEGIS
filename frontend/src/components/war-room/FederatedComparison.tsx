"use client";
import { Globe, ArrowUp } from "lucide-react";
import { motion } from "framer-motion";

interface BankData {
  name: string;
  f1: number;
  auc: number;
  txn_count: number;
}

interface FederatedData {
  banks: BankData[];
  federated: { f1: number; auc: number; improvement: string };
}

// Fallback demo data
const DEMO: FederatedData = {
  banks: [
    { name: "Bank A", f1: 0.82, auc: 0.89, txn_count: 35000 },
    { name: "Bank B", f1: 0.79, auc: 0.86, txn_count: 30000 },
    { name: "Bank C", f1: 0.84, auc: 0.91, txn_count: 35000 },
  ],
  federated: { f1: 0.93, auc: 0.97, improvement: "+12.8%" },
};

export default function FederatedComparison({ data }: { data: FederatedData | null }) {
  const d = data || DEMO;

  return (
    <div className="glass-card glow-green h-full flex flex-col">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-aegis-border">
        <Globe className="w-5 h-5 text-aegis-green" />
        <h2 className="text-sm font-semibold text-aegis-green uppercase tracking-wider">
          Federated Intelligence
        </h2>
      </div>
      <div className="flex-1 p-4 space-y-2">
        {/* Individual Banks */}
        {d.banks.map((bank, i) => (
          <div key={bank.name} className="flex items-center gap-3">
            <span className="text-xs text-aegis-text-muted w-14 shrink-0">{bank.name}</span>
            <div className="flex-1 h-5 bg-aegis-border rounded-full overflow-hidden relative">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${bank.f1 * 100}%` }}
                transition={{ duration: 1, delay: i * 0.2 }}
                className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full"
              />
            </div>
            <span className="text-xs font-mono font-semibold w-12 text-right">{(bank.f1 * 100).toFixed(1)}%</span>
          </div>
        ))}

        {/* Divider */}
        <div className="border-t border-dashed border-aegis-border my-2" />

        {/* Federated Result */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-aegis-green font-semibold w-14 shrink-0">🌐 Fed.</span>
          <div className="flex-1 h-6 bg-aegis-border rounded-full overflow-hidden relative">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${d.federated.f1 * 100}%` }}
              transition={{ duration: 1.5, delay: 0.8 }}
              className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full"
            />
          </div>
          <span className="text-sm font-mono font-bold text-aegis-green w-12 text-right">
            {(d.federated.f1 * 100).toFixed(1)}%
          </span>
        </div>

        {/* Improvement Badge */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1.5 }}
          className="flex items-center justify-center gap-2 mt-3 py-2 px-3 rounded-lg bg-aegis-green/10 border border-aegis-green/30"
        >
          <ArrowUp className="w-4 h-4 text-aegis-green" />
          <span className="text-sm font-semibold text-aegis-green">
            {d.federated.improvement} Network Intelligence Advantage
          </span>
        </motion.div>

        <p className="text-[10px] text-aegis-text-muted text-center mt-1">
          Cross-bank mule chains only detectable with federated model
        </p>
      </div>
    </div>
  );
}

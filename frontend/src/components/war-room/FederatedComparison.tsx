"use client";
import { Globe, ArrowUp, RefreshCw, CheckCircle2, Info } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Tooltip } from "@/components/ui/Tooltip";

interface BankData {
  name: string;
  f1: number;
  auc: number;
  updates?: number;
  status?: string;
  txn_count?: number;
}

interface FederatedData {
  round?: number;
  banks: BankData[];
  federated: { f1: number; auc: number; improvement: string };
}

// Fallback demo data
const DEMO: FederatedData = {
  round: 1,
  banks: [
    { name: "Global Bank (APAC)", f1: 0.82, auc: 0.89, updates: 5, status: "SYNCED" },
    { name: "Retail Bank (EMEA)", f1: 0.79, auc: 0.86, updates: 3, status: "COMPUTING" },
    { name: "Digital Bank (NAM)", f1: 0.84, auc: 0.91, updates: 8, status: "UPDATED" },
  ],
  federated: { f1: 0.93, auc: 0.97, improvement: "+12.8%" },
};

export default function FederatedComparison({ data }: { data: FederatedData | null }) {
  const d = data || DEMO;

  return (
    <div className="bg-white border border-slate-200 shadow-sm rounded-xl h-full flex flex-col">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-200">
        
        <h2 className="text-sm font-semibold text-slate-800 uppercase tracking-wider">
          Federated Intelligence
        </h2>
        <Tooltip content="Global model aggregation across institutions">
          <Info className="w-4 h-4 text-slate-400 cursor-help ml-1" />
        </Tooltip>
        {d.round && (
          <span className="ml-auto text-[10px] font-mono text-slate-500 bg-slate-50 px-2 py-1 rounded border border-slate-200">
            ROUND {d.round}
          </span>
        )}
      </div>
      <div className="flex-1 p-4 space-y-3 overflow-y-auto">
        {/* Individual Banks */}
        <div className="space-y-3">
          {d.banks.map((bank, i) => (
            <div key={bank.name} className="flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-700">{bank.name}</span>
                <div className="flex items-center gap-1.5 text-[9px] font-mono">
                  {bank.status === "SYNCED" && <CheckCircle2 className="w-3 h-3 text-slate-600" />}
                  {bank.status === "COMPUTING" && <RefreshCw className="w-3 h-3 text-slate-400 animate-spin" />}
                  {bank.status === "UPDATED" && <ArrowUp className="w-3 h-3 text-slate-600" />}
                  <span className={bank.status === 'SYNCED' ? 'text-slate-600' : bank.status === 'COMPUTING' ? 'text-slate-500' : 'text-slate-600'}>
                    {bank.status || 'SYNCED'}
                  </span>
                  <span className="text-slate-400 ml-1">({bank.updates || 0} updates)</span>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <div className="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden relative border border-slate-200">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${bank.f1 * 100}%` }}
                    transition={{ duration: 1, delay: i * 0.2 }}
                    className="h-full bg-aegis-blue rounded-full"
                  />
                </div>
                <span className="text-[11px] font-mono font-semibold w-12 text-right text-slate-600">
                  {(bank.f1 * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div className="border-t border-dashed border-slate-200 my-2" />

        {/* Federated Result */}
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-800 font-bold flex items-center gap-1.5">
              <Globe className="w-4 h-4 text-aegis-green" /> Global Model Aggregation
            </span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex-1 h-5 bg-aegis-green-light/30 rounded-full overflow-hidden relative border border-aegis-green/20 shadow-inner">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${d.federated.f1 * 100}%` }}
                transition={{ duration: 1.5, delay: 0.8 }}
                className="h-full bg-aegis-green rounded-full shadow-[0_0_10px_rgba(2,122,72,0.4)]"
              />
            </div>
            <span className="text-base font-mono font-bold text-aegis-green w-14 text-right">
              {(d.federated.f1 * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Improvement Badge */}
        <AnimatePresence>
          <motion.div
            key={d.round}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-center gap-2 mt-4 py-2 px-3 rounded-lg bg-aegis-green-light/30 border border-aegis-green/20 shadow-sm"
          >
            <ArrowUp className="w-4 h-4 text-aegis-green" />
            <span className="text-xs font-semibold text-aegis-green uppercase tracking-wide">
              {d.federated.improvement} Network Advantage
            </span>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

"use client";
import { ShieldAlert, Info, ShieldX, ShieldCheck } from "lucide-react";
import { Tooltip } from "@/components/ui/Tooltip";
import { motion } from "framer-motion";

interface PerturbedTransaction {
  txnId: string;
  attackVector: string;
  originalRisk: number;
  perturbedRisk: number;
  isEvaded: boolean;
  phase?: string;
  nodeRole?: string;
}

const phaseColors: Record<string, string> = {
  RECON: "text-yellow-700 bg-yellow-50 border-yellow-200",
  DETECTION: "text-orange-700 bg-orange-50 border-orange-200",
  CONTAINMENT: "text-blue-700 bg-blue-50 border-blue-200",
  MUTATION: "text-red-700 bg-red-50 border-red-200",
  ADAPTATION: "text-purple-700 bg-purple-50 border-purple-200",
  IDLE: "text-slate-500 bg-slate-50 border-slate-200",
};

export default function AdversarialInstanceView({ liveData }: { liveData?: any }) {
  const instances: PerturbedTransaction[] = liveData?.adversarial_instances || [];

  return (
    <div className="bg-white border border-slate-200 shadow-sm rounded-xl flex flex-col overflow-hidden h-full">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-slate-200 shrink-0 bg-slate-50/50">
        
        <h2 className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
          Battle Log — Red vs Blue
        </h2>
        <Tooltip content={
          <div className="flex flex-col gap-1 text-[10px]">
            <p><strong>Phase:</strong> Current stage of battle.</p>
            <p><strong>Transaction:</strong> Txn ID.</p>
            <p><strong>Vector/Role:</strong> Attack method & Node targeted.</p>
            <p><strong>Risk:</strong> Original risk score.</p>
            <p><strong>Boundary:</strong> The threshold visualizer (Blue vs Red).</p>
            <p><strong>Final:</strong> The perturbed risk score after mutation.</p>
            <p><strong>Result:</strong> Whether Blue Team Blocked or Red Team Evaded.</p>
          </div>
        }>
          <Info className="w-3.5 h-3.5 text-slate-400 cursor-help ml-1" />
        </Tooltip>
        {liveData?.battle_phase && liveData.battle_phase !== "IDLE" && (
          <span className={`ml-auto text-[9px] font-bold px-2 py-0.5 rounded border ${phaseColors[liveData.battle_phase] || phaseColors.IDLE}`}>
            {liveData.battle_phase}
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {instances.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs p-4">
            <ShieldCheck className="w-6 h-6 mb-2 opacity-40" />
            <p>No battle activity. Launch an attack to begin.</p>
          </div>
        ) : (
        <table className="w-full text-[10px] text-left">
          <thead className="bg-slate-50 text-slate-500 sticky top-0 z-30 border-b border-slate-200">
            <tr>
              <th className="px-2 py-1.5 font-semibold">Phase</th>
              <th className="px-2 py-1.5 font-semibold">Transaction</th>
              <th className="px-2 py-1.5 font-semibold">Vector / Role</th>
              <th className="px-2 py-1.5 font-semibold text-center">Risk</th>
              <th className="px-2 py-1.5 font-semibold text-center w-32">Boundary</th>
              <th className="px-2 py-1.5 font-semibold text-center">Final</th>
              <th className="px-2 py-1.5 font-semibold text-center">Result</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {instances.map((inst, i) => (
              <tr key={`${inst.txnId}-${i}`} className="hover:bg-slate-50/50 transition-colors">
                {/* Phase Badge */}
                <td className="px-2 py-1.5">
                  <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded border ${phaseColors[inst.phase || "IDLE"] || phaseColors.IDLE}`}>
                    {inst.phase || "—"}
                  </span>
                </td>
                
                {/* Transaction ID */}
                <td className="px-2 py-1.5 font-mono text-slate-700">{inst.txnId}</td>
                
                {/* Attack Vector + Node Role */}
                <td className="px-2 py-1.5 text-slate-600 max-w-[120px]">
                  <div className="truncate text-[9px]">{inst.attackVector}</div>
                  {inst.nodeRole && inst.nodeRole !== "—" && (
                    <div className="text-[8px] text-slate-400 truncate">{inst.nodeRole}</div>
                  )}
                </td>
                
                {/* Initial Risk */}
                <td className="px-2 py-1.5 font-mono text-red-500 text-center font-semibold">
                  {(inst.originalRisk * 100).toFixed(1)}%
                </td>
                
                {/* Decision Boundary Visualization */}
                <td className="px-2 py-1.5">
                  <div className="relative w-full h-5 flex items-center justify-center">
                    <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-[3px] rounded-full bg-gradient-to-r from-blue-200/50 to-red-200/50 z-0" />
                    <div className="absolute left-1/2 top-0 bottom-0 w-[2px] -translate-x-1/2 bg-slate-400 border-x border-white z-0" />
                    
                    <div 
                      className="absolute w-1.5 h-1.5 rounded-full bg-red-500 border border-white z-10" 
                      style={{ left: `calc(${inst.originalRisk * 100}% - 3px)` }}
                    />
                    
                    <motion.div 
                      className={`absolute w-1.5 h-1.5 rounded-full border border-white z-20 ${inst.isEvaded ? 'bg-blue-500' : 'bg-red-500'}`}
                      initial={{ left: `calc(${inst.originalRisk * 100}% - 3px)` }}
                      animate={{ left: `calc(${inst.perturbedRisk * 100}% - 3px)` }}
                      transition={{ duration: 0.6, type: "spring" }}
                    />
                  </div>
                </td>
                
                {/* Final Risk */}
                <td className={`px-2 py-1.5 font-mono text-center font-bold ${inst.isEvaded ? 'text-blue-500' : 'text-red-500'}`}>
                  {(inst.perturbedRisk * 100).toFixed(1)}%
                </td>
                
                {/* Status Badge */}
                <td className="px-2 py-1.5">
                  <div className="flex justify-center">
                    {inst.attackVector === "Normal Traffic" ? (
                      <span className="text-[8px] font-bold text-aegis-green bg-aegis-green-light/30 px-1.5 py-0.5 rounded border border-aegis-green/20">
                        CLEAN
                      </span>
                    ) : inst.isEvaded ? (
                      <span className="flex items-center gap-0.5 text-[8px] font-bold text-red-500 bg-red-500-light/30 px-1.5 py-0.5 rounded border border-aegis-red/20">
                        <ShieldX className="w-2.5 h-2.5" /> EVADED
                      </span>
                    ) : (
                      <span className="flex items-center gap-0.5 text-[8px] font-bold text-blue-500 bg-blue-500-light/30 px-1.5 py-0.5 rounded border border-aegis-blue/20">
                        <ShieldCheck className="w-2.5 h-2.5" /> BLOCKED
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        )}
      </div>
    </div>
  );
}


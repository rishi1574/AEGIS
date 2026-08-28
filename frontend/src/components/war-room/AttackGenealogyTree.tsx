"use client";
import { GitMerge, GitCommit, GitBranch } from "lucide-react";

export default function AttackGenealogyTree() {
  return (
    <div className="glass-card bg-white shadow-sm h-full flex flex-col p-4">
      <div className="flex items-center gap-2 mb-4 border-b border-slate-200 pb-2">
        <GitBranch className="w-5 h-5 text-aegis-purple" />
        <h2 className="text-sm font-semibold text-aegis-purple uppercase tracking-wider">
          Adversarial RL Mutations (Genealogy)
        </h2>
      </div>
      <div className="flex-1 relative overflow-hidden flex items-center justify-center">
        <div className="text-center text-slate-500 text-xs font-mono space-y-4">
          <div className="flex items-center justify-center gap-2">
             <span className="p-2 bg-aegis-red/20 border border-aegis-red/50 rounded">Gen 1: Fuzzing Amount (Blocked)</span>
          </div>
          <GitCommit className="w-4 h-4 mx-auto text-aegis-border" />
          <div className="flex items-center justify-center gap-2">
             <span className="p-2 bg-aegis-red/20 border border-aegis-red/50 rounded">Gen 2: Fuzzing Amount + Time (Blocked)</span>
          </div>
          <GitMerge className="w-4 h-4 mx-auto text-aegis-border" />
          <div className="flex items-center justify-center gap-4">
             <span className="p-2 bg-aegis-green/20 border border-aegis-green/50 rounded">Gen 3: Amount + 3am Burst (Bypass)</span>
          </div>
          <p className="text-[10px] mt-4 opacity-50">RL Agent Evolutionary Tree Visualization</p>
        </div>
      </div>
    </div>
  );
}

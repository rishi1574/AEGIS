"use client";
import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Crosshair, Zap, AlertTriangle, ChevronRight, IdCard, Network, Brain, Rocket, ChevronDown, Filter, Activity, Info } from "lucide-react";
import { Tooltip } from "@/components/ui/Tooltip";

interface Attack {
  id: string;
  name: string;
  layer: string;
  risk: string;
  description?: string;
  total_simulated?: number;
  bypass_rate?: number;
}

const LAYER_COLORS: Record<string, string> = {
  identity: "text-purple-700 bg-purple-50 border-purple-200",
  network: "text-amber-700 bg-amber-50 border-amber-200",
  human: "text-rose-700 bg-rose-50 border-rose-200",
  emerging: "text-cyan-700 bg-cyan-50 border-cyan-200",
};

const getLayerIcon = (layer: string, className: string = "w-3 h-3") => {
  switch (layer) {
    case "identity": return <IdCard className={className} />;
    case "network": return <Network className={className} />;
    case "human": return <Brain className={className} />;
    case "emerging": return <Rocket className={className} />;
    default: return <Zap className={className} />;
  }
};

export default function RedTeamConsole({
  attacks,
  onLaunch,
  liveData,
}: {
  attacks: Attack[];
  onLaunch: any;
  liveData?: any;
}) {
  const [launching, setLaunching] = useState<string | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (liveData?.red_team_log) {
      setLog((prev) => [...prev, liveData.red_team_log].slice(-15));
    }
  }, [liveData]);

  // Auto-scroll to bottom of log when new entries arrive
  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollTop = logEndRef.current.scrollHeight;
    }
  }, [log]);

  const handleLaunch = async (attackId: string) => {
    setLaunching(attackId);
    setLog((prev) => [...prev, `[INIT] Launching ${attackId}...`]);
    try {
      const result = await onLaunch(attackId);
      setLog((prev) => [...prev, `[SUCCESS] ${result.message}`]);
      if (result.historical_bypass_rate > 0) {
        setLog((prev) => [
          ...prev,
          `[STATS] Historical bypass: ${(result.historical_bypass_rate * 100).toFixed(1)}%`,
        ]);
      }
    } catch (e) {
      setLog((prev) => [...prev, `[ERROR] Failed to launch ${attackId}`]);
    }
    setTimeout(() => setLaunching(null), 2000);
  };

  const layers = ["identity", "network", "human", "emerging"];
  const filteredAttacks = activeFilter && activeFilter !== "all"
    ? attacks?.filter((a) => a.layer === activeFilter)
    : attacks;

  return (
    <div className="bg-white border border-slate-200 shadow-sm rounded-xl h-full flex flex-col min-h-0 overflow-hidden relative">
      {/* Header */}
      <div className="flex items-center gap-2 px-5 py-4 border-b border-slate-200 bg-slate-50 relative z-10 shrink-0">
        <Crosshair className="w-5 h-5 text-slate-800" />
        <h2 className="text-sm font-semibold text-slate-800 uppercase tracking-wider">
          Red Team Intelligence
        </h2>
        <Tooltip content="Adversarial attack simulation console">
          <Info className="w-4 h-4 text-slate-400 cursor-help ml-1" />
        </Tooltip>
        <span className="ml-auto text-xs font-medium text-slate-500 bg-white px-2 py-1 rounded-md border border-slate-200">
          {attacks?.length || 0} vectors active
        </span>
      </div>

      {/* Dropdown Filter */}
      <div className="px-5 py-3 border-b border-slate-200 bg-white flex items-center justify-between shrink-0 relative z-10">
        <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
          <Filter className="w-3.5 h-3.5" /> Filter Vectors
        </div>
        <div className="relative">
          <select
            value={activeFilter || "all"}
            onChange={(e) => setActiveFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 text-slate-700 text-xs font-medium rounded-md pl-3 pr-8 py-1.5 focus:outline-none focus:ring-2 focus:ring-slate-400 cursor-pointer"
          >
            <option value="all">All Layers</option>
            <option value="identity">Identity Layer</option>
            <option value="network">Network Layer</option>
            <option value="human">Human Layer</option>
            <option value="emerging">Emerging Tech</option>
          </select>
          <ChevronDown className="absolute right-2.5 top-2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
        </div>
      </div>

      {/* Attack List */}
      <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-1.5 bg-slate-50 relative z-0">
        <AnimatePresence mode="popLayout">
          {filteredAttacks?.map((atk) => (
            <motion.button
              key={atk.id}
              layout
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleLaunch(atk.id)}
              disabled={launching === atk.id}
              className={`w-full text-left p-3 rounded-xl border transition-all group bg-white shadow-sm relative
                ${
                  launching === atk.id
                    ? "border-red-400 bg-red-50 attacking"
                    : "border-slate-200 hover:border-slate-300"
                }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-slate-800">{atk.name}</span>
                  {atk.description && (
                    <Tooltip content={atk.description}>
                      <Info className="w-3.5 h-3.5 text-slate-400" />
                    </Tooltip>
                  )}
                </div>
                {launching === atk.id ? (
                  <Zap className="w-4 h-4 text-red-500 animate-pulse" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" />
                )}
              </div>
              <div className="flex items-center gap-2 mt-2">
                <span
                  className={`flex items-center gap-1.5 text-[10px] font-medium px-2 py-0.5 rounded-md border ${
                    LAYER_COLORS[atk.layer] || ""
                  }`}
                >
                  {getLayerIcon(atk.layer, "w-3 h-3")} {atk.layer.toUpperCase()}
                </span>
                {atk.risk === "critical" && (
                  <span className="text-[10px] font-bold text-red-600 flex items-center gap-1 bg-red-50 px-2 py-0.5 rounded-md border border-red-100">
                    <AlertTriangle className="w-3 h-3" /> CRITICAL
                  </span>
                )}
                {atk.bypass_rate !== undefined && atk.bypass_rate > 0 && (
                  <span className="text-[10px] font-mono text-amber-600 ml-auto bg-amber-50 px-2 py-0.5 rounded-md border border-amber-100">
                    Bypass: {(atk.bypass_rate * 100).toFixed(0)}%
                  </span>
                )}
              </div>
              {atk.description && (
                <p className="text-[11px] text-slate-500 mt-2 leading-relaxed line-clamp-2">
                  {atk.description}
                </p>
              )}
            </motion.button>
          ))}
        </AnimatePresence>
      </div>

      {/* Agent Thought Stream */}
      <div 
        ref={logEndRef}
        className="border-t border-slate-200 p-3 pb-5 bg-white h-36 shrink-0 overflow-y-auto relative z-10 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]"
      >
        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 sticky top-0 bg-white z-20 pb-1">
          <Activity className="w-3.5 h-3.5" /> Agent Activity Log
        </p>
        <div className="space-y-1 font-mono text-[11px]">
          <AnimatePresence>
            {log.slice(-10).map((entry, i) => (
              <motion.div
                key={`${i}-${entry.slice(0, 20)}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-slate-600 flex gap-2"
              >
                <span className="text-slate-400 shrink-0">[{new Date().toLocaleTimeString('en-US', {hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit'})}]</span>
                <span>{entry}</span>
              </motion.div>
            ))}
          </AnimatePresence>
          {log.length === 0 && (
            <span className="text-slate-400 italic block mt-1">System standing by...</span>
          )}
        </div>
      </div>
    </div>
  );
}

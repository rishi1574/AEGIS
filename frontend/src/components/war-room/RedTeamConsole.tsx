"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Crosshair, Zap, AlertTriangle, ChevronRight, Square } from "lucide-react";

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
  identity: "text-purple-400 bg-purple-400/10 border-purple-400/30",
  network: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  human: "text-rose-400 bg-rose-400/10 border-rose-400/30",
  emerging: "text-cyan-400 bg-cyan-400/10 border-cyan-400/30",
};

const LAYER_EMOJI: Record<string, string> = {
  identity: "🪪",
  network: "🌐",
  human: "🧠",
  emerging: "🚀",
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

  useEffect(() => {
    if (liveData?.red_team_log) {
      setLog((prev) => [...prev, liveData.red_team_log].slice(-15));
    }
  }, [liveData]);

  const handleLaunch = async (attackId: string) => {
    setLaunching(attackId);
    setLog((prev) => [...prev, `⚡ Launching ${attackId}...`]);
    try {
      const result = await onLaunch(attackId);
      setLog((prev) => [...prev, `✅ ${result.message}`]);
      if (result.historical_bypass_rate > 0) {
        setLog((prev) => [
          ...prev,
          `📊 Historical bypass: ${(result.historical_bypass_rate * 100).toFixed(1)}%`,
        ]);
      }
    } catch (e) {
      setLog((prev) => [...prev, `❌ Failed to launch ${attackId}`]);
    }
    setTimeout(() => setLaunching(null), 2000);
  };

  const layers = ["identity", "network", "human", "emerging"];
  const filteredAttacks = activeFilter
    ? attacks?.filter((a) => a.layer === activeFilter)
    : attacks;

  return (
    <div className="glass-card glow-red h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-aegis-border">
        <Crosshair className="w-5 h-5 text-aegis-red" />
        <h2 className="text-sm font-semibold text-aegis-red uppercase tracking-wider neon-red">
          Red Team
        </h2>
        <span className="ml-auto text-xs text-aegis-text-muted">
          {attacks?.length || 0} vectors
        </span>
      </div>

      {/* Layer Filters */}
      <div className="flex gap-1 px-3 py-2 border-b border-aegis-border">
        <button
          onClick={() => setActiveFilter(null)}
          className={`text-[9px] px-2 py-0.5 rounded-full border transition-all ${
            !activeFilter
              ? "border-aegis-blue bg-aegis-blue/20 text-aegis-blue"
              : "border-aegis-border text-aegis-text-muted hover:border-aegis-text-muted"
          }`}
        >
          All
        </button>
        {layers.map((l) => (
          <button
            key={l}
            onClick={() => setActiveFilter(l === activeFilter ? null : l)}
            className={`text-[9px] px-2 py-0.5 rounded-full border transition-all ${
              activeFilter === l
                ? LAYER_COLORS[l]
                : "border-aegis-border text-aegis-text-muted hover:border-aegis-text-muted"
            }`}
          >
            {LAYER_EMOJI[l]} {l}
          </button>
        ))}
      </div>

      {/* Attack List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
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
              className={`w-full text-left p-2.5 rounded-lg border transition-all group
                ${
                  launching === atk.id
                    ? "border-aegis-red bg-aegis-red/10 attacking"
                    : "border-aegis-border hover:border-aegis-red/50 hover:bg-aegis-red/5"
                }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-aegis-text">{atk.name}</span>
                {launching === atk.id ? (
                  <Zap className="w-3.5 h-3.5 text-aegis-red animate-pulse" />
                ) : (
                  <ChevronRight className="w-3.5 h-3.5 text-aegis-text-muted group-hover:text-aegis-red transition-colors" />
                )}
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span
                  className={`text-[9px] px-1.5 py-0.5 rounded border ${
                    LAYER_COLORS[atk.layer] || ""
                  }`}
                >
                  {LAYER_EMOJI[atk.layer] || ""} {atk.layer}
                </span>
                {atk.risk === "critical" && (
                  <span className="text-[9px] text-aegis-red flex items-center gap-0.5">
                    <AlertTriangle className="w-3 h-3" /> CRITICAL
                  </span>
                )}
                {atk.bypass_rate !== undefined && atk.bypass_rate > 0 && (
                  <span className="text-[9px] text-aegis-amber font-mono ml-auto">
                    {(atk.bypass_rate * 100).toFixed(0)}% bypass
                  </span>
                )}
              </div>
              {atk.description && (
                <p className="text-[9px] text-aegis-text-muted/60 mt-1 leading-snug line-clamp-2">
                  {atk.description}
                </p>
              )}
            </motion.button>
          ))}
        </AnimatePresence>
      </div>

      {/* Agent Thought Stream */}
      <div className="border-t border-aegis-border p-2 max-h-36 overflow-y-auto">
        <p className="text-[9px] text-aegis-text-muted uppercase tracking-wider mb-1 flex items-center gap-1">
          <Zap className="w-3 h-3" /> Agent Activity Log
        </p>
        <div className="space-y-0.5 font-mono text-[10px]">
          <AnimatePresence>
            {log.slice(-10).map((entry, i) => (
              <motion.div
                key={`${i}-${entry.slice(0, 20)}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-aegis-text-muted"
              >
                {entry}
              </motion.div>
            ))}
          </AnimatePresence>
          {log.length === 0 && (
            <span className="text-aegis-text-muted/50">Awaiting orders...</span>
          )}
        </div>
      </div>
    </div>
  );
}

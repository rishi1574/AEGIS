"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Crosshair, Zap, AlertTriangle, ChevronRight } from "lucide-react";

interface Attack {
  id: string;
  name: string;
  layer: string;
  risk: string;
}

interface Props {
  attacks: Attack[];
  onLaunch: (type: string) => Promise<any>;
  messages: any[];
}

const LAYER_COLORS: Record<string, string> = {
  identity: "text-purple-400 bg-purple-400/10 border-purple-400/30",
  network: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  human: "text-rose-400 bg-rose-400/10 border-rose-400/30",
  emerging: "text-cyan-400 bg-cyan-400/10 border-cyan-400/30",
};

export default function RedTeamConsole({ attacks, onLaunch, liveData }: { attacks: Attack[], onLaunch: any, liveData?: any }) {
  const [launching, setLaunching] = useState<string | null>(null);
  const [log, setLog] = useState<string[]>([]);

  // Listen to websocket stream
  useEffect(() => {
    if (liveData?.red_team_log) {
      setLog(prev => [...prev, liveData.red_team_log].slice(-10));
    }
  }, [liveData]);

  const handleLaunch = async (attackId: string) => {
    setLaunching(attackId);
    setLog((prev) => [...prev, `⚡ Launching ${attackId}...`]);
    try {
      const result = await onLaunch(attackId);
      setLog((prev) => [...prev, `✅ ${result.message}`]);
    } catch (e) {
      setLog((prev) => [...prev, `❌ Failed to launch ${attackId}`]);
    }
    setTimeout(() => setLaunching(null), 1000);
  };

  return (
    <div className="glass-card glow-red h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-aegis-border">
        <Crosshair className="w-5 h-5 text-aegis-red" />
        <h2 className="text-sm font-semibold text-aegis-red uppercase tracking-wider">Red Team</h2>
        <span className="ml-auto text-xs text-aegis-text-muted">{attacks?.length || 0} vectors</span>
      </div>

      {/* Attack List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {attacks?.map((atk) => (
          <motion.button
            key={atk.id}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => handleLaunch(atk.id)}
            disabled={launching === atk.id}
            className={`w-full text-left p-2.5 rounded-lg border transition-all group
              ${launching === atk.id
                ? "border-aegis-red bg-aegis-red/10 animate-pulse"
                : "border-aegis-border hover:border-aegis-red/50 hover:bg-aegis-red/5"}`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-aegis-text">{atk.name}</span>
              <ChevronRight className="w-3.5 h-3.5 text-aegis-text-muted group-hover:text-aegis-red transition-colors" />
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-[10px] px-1.5 py-0.5 rounded border ${LAYER_COLORS[atk.layer] || ""}`}>
                {atk.layer}
              </span>
              {atk.risk === "critical" && (
                <span className="text-[10px] text-aegis-red flex items-center gap-0.5">
                  <AlertTriangle className="w-3 h-3" /> CRITICAL
                </span>
              )}
            </div>
          </motion.button>
        ))}
      </div>

      {/* Agent Thought Stream (Log) */}
      <div className="border-t border-aegis-border p-2 max-h-32 overflow-y-auto">
        <p className="text-[10px] text-aegis-text-muted uppercase tracking-wider mb-1">Agent Log</p>
        <div className="space-y-0.5 font-mono text-[11px]">
          <AnimatePresence>
            {log.slice(-8).map((entry, i) => (
              <motion.div
                key={i}
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

"use client";
import { Shield, Wifi, WifiOff, Activity, ChevronDown } from "lucide-react";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function Header({ connected }: { connected: boolean }) {
  const [time, setTime] = useState("");

  useEffect(() => {
    setTime(new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }));
    const interval = setInterval(() => {
      setTime(new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-aegis-border bg-white shadow-sm z-50 relative">
      <div className="flex items-center gap-4">
        <motion.div
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        >
          {/* Logo container with Mastercard colors */}
          <div className="flex -space-x-2">
            <div className="w-8 h-8 rounded-full bg-aegis-red opacity-90 mix-blend-multiply" />
            <div className="w-8 h-8 rounded-full bg-aegis-amber opacity-90 mix-blend-multiply" />
          </div>
        </motion.div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-aegis-text">
            AEGIS <span className="font-medium text-aegis-text-muted ml-1">Command Center</span>
          </h1>
          <p className="text-[11px] font-medium text-aegis-text-muted uppercase tracking-wider">
            Mastercard Innovation Challenge 2026
          </p>
        </div>
      </div>

      <div className="flex items-center gap-6">
        {/* Environment Dropdown */}
        <div className="relative flex items-center bg-slate-50 border border-slate-200 rounded-md px-3 py-1.5 text-sm font-medium text-slate-700 cursor-pointer hover:bg-slate-100 transition-colors">
          <span className="w-2 h-2 rounded-full bg-aegis-blue mr-2"></span>
          Federated Sandbox
          <ChevronDown className="w-4 h-4 ml-2 text-slate-400" />
        </div>

        {/* Threat Level */}
        <motion.div
          className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full bg-red-50 text-red-700 border border-red-100"
          animate={connected ? { scale: [1, 1.02, 1] } : {}}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Activity className="w-4 h-4" />
          THREAT LEVEL: CRITICAL
        </motion.div>

        <div className="flex items-center gap-2 text-xs font-medium bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full">
          {connected ? (
            <>
              <Wifi className="w-3.5 h-3.5 text-aegis-green" />
              <span className="text-aegis-green">SYSTEM LIVE</span>
            </>
          ) : (
            <>
              <WifiOff className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-slate-500">OFFLINE</span>
            </>
          )}
        </div>
        <div className="text-xs text-slate-500 font-mono font-medium min-w-[150px] text-right">
          {time}
        </div>
      </div>
    </header>
  );
}

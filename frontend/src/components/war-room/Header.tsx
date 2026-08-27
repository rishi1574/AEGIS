"use client";
import { Shield, Wifi, WifiOff, Zap } from "lucide-react";
import { motion } from "framer-motion";

export default function Header({ connected }: { connected: boolean }) {
  return (
    <header className="relative flex items-center justify-between px-4 py-2 border-b border-aegis-border bg-aegis-surface/80 backdrop-blur-md scan-effect overflow-hidden">
      {/* Ambient glow */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-transparent to-red-500/5 pointer-events-none" />

      <div className="flex items-center gap-3 relative z-10">
        <motion.div
          className="relative"
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        >
          <Shield className="w-8 h-8 text-aegis-blue" />
          <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-aegis-green rounded-full animate-pulse" />
        </motion.div>
        <div>
          <h1 className="text-lg font-bold tracking-tight">
            <span className="gradient-text">AEGIS</span>
            <span className="text-aegis-text-muted font-normal ml-2">— Adversarial War Room</span>
          </h1>
          <p className="text-xs text-aegis-text-muted">
            Mastercard Innovation Challenge 2026 • AI Defense Lab
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4 relative z-10">
        {/* Active Attack Indicator */}
        <motion.div
          className="flex items-center gap-1.5 text-xs"
          animate={connected ? { opacity: [1, 0.5, 1] } : {}}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Zap className="w-3.5 h-3.5 text-aegis-amber" />
          <span className="text-aegis-amber font-mono text-[10px]">
            ADVERSARIAL LOOP ACTIVE
          </span>
        </motion.div>

        <div className="flex items-center gap-2 text-xs">
          {connected ? (
            <>
              <Wifi className="w-4 h-4 text-aegis-green" />
              <span className="text-aegis-green neon-green font-semibold">LIVE</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4 text-aegis-red" />
              <span className="text-aegis-red">OFFLINE</span>
            </>
          )}
        </div>
        <div className="text-xs text-aegis-text-muted font-mono">
          {new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })}
        </div>
      </div>
    </header>
  );
}

"use client";
import { Shield, Wifi, WifiOff } from "lucide-react";

export default function Header({ connected }: { connected: boolean }) {
  return (
    <header className="flex items-center justify-between px-4 py-2 border-b border-aegis-border bg-aegis-surface/80 backdrop-blur-md">
      <div className="flex items-center gap-3">
        <div className="relative">
          <Shield className="w-8 h-8 text-aegis-blue" />
          <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-aegis-green rounded-full animate-pulse" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight">
            <span className="text-aegis-blue">AEGIS</span>
            <span className="text-aegis-text-muted font-normal ml-2">— Adversarial War Room</span>
          </h1>
          <p className="text-xs text-aegis-text-muted">Mastercard Innovation Challenge 2026</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs">
          {connected ? (
            <><Wifi className="w-4 h-4 text-aegis-green" /><span className="text-aegis-green">LIVE</span></>
          ) : (
            <><WifiOff className="w-4 h-4 text-aegis-red" /><span className="text-aegis-red">OFFLINE</span></>
          )}
        </div>
        <div className="text-xs text-aegis-text-muted font-mono">
          {new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })}
        </div>
      </div>
    </header>
  );
}

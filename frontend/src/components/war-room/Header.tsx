"use client";
import { Shield, Wifi, WifiOff, Activity, ChevronDown } from"lucide-react";
import { motion } from"framer-motion";
import { useEffect, useState } from"react";

export default function Header({ connected }: { connected: boolean }) {
 const [time, setTime] = useState("");

 useEffect(() => {
 setTime(new Date().toLocaleString("en-IN", { timeZone:"Asia/Kolkata" }));
 const interval = setInterval(() => {
 setTime(new Date().toLocaleString("en-IN", { timeZone:"Asia/Kolkata" }));
 }, 1000);
 return () => clearInterval(interval);
 }, []);

 return (
 <header className="flex items-center justify-between px-6 py-3 border-b border-aegis-border bg-white shadow-sm z-50 relative">
 <div className="flex items-center gap-4">
        {/* Logo container with Mastercard colors */}
        <div className="flex -space-x-2 items-center">
          <div className="w-6 h-6 rounded-full bg-[#EB001B] opacity-95 mix-blend-multiply" />
          <div className="w-6 h-6 rounded-full bg-[#F79E1B] opacity-95 mix-blend-multiply" />
        </div>
 <div>
 <h1 className="text-xl font-bold tracking-tight text-slate-900">
 AEGIS <span className="font-medium text-slate-500 ml-1">Command Center</span>
 </h1>
 <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest mt-0.5">
 Mastercard Innovation Challenge 2026
 </p>
 </div>
 </div>

 <div className="flex items-center gap-5">
 {/* Environment Dropdown */}
 <div className="relative flex items-center bg-slate-100/80 border border-slate-200/60 px-3 py-1.5 text-sm font-semibold text-slate-700 cursor-pointer hover:bg-slate-200/50 transition-colors shadow-sm">
 <Shield className="w-3.5 h-3.5 text-blue-600 mr-2" />
 Federated Sandbox
 <ChevronDown className="w-3.5 h-3.5 ml-2 text-slate-400" />
 </div>

 {/* Threat Level */}
 <motion.div
 className="flex items-center gap-2 text-xs font-bold px-3 py-1.5 bg-red-100/80 text-red-700 border border-red-200 shadow-sm"
 animate={connected ? { scale: [1, 1.02, 1] } : {}}
 transition={{ duration: 2, repeat: Infinity }}
 >
 <Activity className="w-4 h-4" />
 THREAT LEVEL: CRITICAL
 </motion.div>

 {/* System Status */}
 <div className="flex items-center gap-2 text-xs font-bold bg-slate-100/80 border border-slate-200/60 px-3 py-1.5 shadow-sm">
 {connected ? (
 <>
 <Wifi className="w-4 h-4 text-emerald-600" />
 <span className="text-emerald-700 tracking-wide">SYSTEM LIVE</span>
 </>
 ) : (
 <>
 <WifiOff className="w-4 h-4 text-slate-400" />
 <span className="text-slate-500 tracking-wide">OFFLINE</span>
 </>
 )}
 </div>

 {/* Clock */}
 <div className="text-xs text-slate-500 font-mono font-semibold min-w-[150px] text-right bg-slate-50 px-3 py-1.5 border border-slate-100">
 {time}
 </div>
 </div>
 </header>
 );
}

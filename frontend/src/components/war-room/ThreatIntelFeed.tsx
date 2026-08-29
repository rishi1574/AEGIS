"use client";
import { useState, useEffect } from"react";
import { AlertTriangle, ShieldAlert, Globe } from"lucide-react";
import { motion, AnimatePresence } from"framer-motion";

const DEMO_ALERTS: any[] = [];

export default function ThreatIntelFeed({ liveData }: { liveData?: any }) {
 const [alerts, setAlerts] = useState<any[]>(DEMO_ALERTS);

 useEffect(() => {
 if (liveData?.threat_intel) {
 setAlerts((prev) => {
 // Prevent spam of the exact same message
 if (prev.length > 0 && prev[0].message === liveData.threat_intel.message) {
 return prev;
 }
 return [liveData.threat_intel, ...prev].slice(0, 20);
 });
 }
 }, [liveData]);

 const severityColor: Record<string, string> = {
 critical:"text-red-600 bg-red-50 border-red-200",
 high:"text-amber-600 bg-amber-50 border-amber-200",
 medium:"text-yellow-600 bg-yellow-50 border-yellow-200",
 };

 return (
 <div className="flex flex-col h-full min-h-0">
 <div className="flex items-center gap-2 mb-2 shrink-0">
 
 <p className="text-[10px] text-slate-800 uppercase tracking-wider font-bold">Threat Intel (Recorded Future)</p>
 </div>
 <div className="flex-1 overflow-y-auto pr-1 space-y-1.5 min-h-0">
 <AnimatePresence>
 {alerts.map((alert, i) => (
 <motion.div
 key={alert.id +"-" + i}
 initial={{ opacity: 0, x: -10 }}
 animate={{ opacity: 1, x: 0 }}
 transition={{ delay: i * 0.05 }}
 className="flex items-start gap-2 p-2.5 bg-white border border-slate-200 shadow-sm"
 >
 <ShieldAlert className="w-3.5 h-3.5 mt-0.5 text-slate-400 shrink-0" />
 <div className="flex-1 min-w-0">
 <p className="text-[11px] font-medium text-slate-700 leading-tight">{alert.message}</p>
 <div className="flex items-center justify-between mt-1.5">
 <span className={`text-[9px] font-bold px-1.5 py-0.5 border ${severityColor[alert.severity] || severityColor.medium}`}>
 {alert.severity.toUpperCase()}
 </span>
 <span className="text-[9px] font-mono text-slate-400">{alert.time}</span>
 </div>
 </div>
 </motion.div>
 ))}
 </AnimatePresence>
      {alerts.length === 0 && (
        <div className="text-[10px] text-slate-400 text-center py-4 italic">
          Threat intel feeds activate during attacks...
        </div>
      )}
 </div>
 </div>
 );
}

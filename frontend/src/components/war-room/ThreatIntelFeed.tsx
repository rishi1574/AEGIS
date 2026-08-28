"use client";
import { useState, useEffect } from "react";
import { AlertTriangle, ShieldAlert, Globe } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const DEMO_ALERTS = [
  { id: 1, type: "darkweb", message: "10K compromised cards detected on Genesis Market", time: "2m ago", severity: "critical" },
  { id: 2, type: "magecart", message: "Magecart skimmer found on travel-booking-xyz.in", time: "12m ago", severity: "high" },
  { id: 3, type: "mule", message: "New mule recruitment campaign via Telegram (Mumbai)", time: "34m ago", severity: "high" },
  { id: 4, type: "apt", message: "FIN7 TTPs observed in card-not-present attacks", time: "1h ago", severity: "medium" },
];

export default function ThreatIntelFeed({ liveData }: { liveData?: any }) {
  const [alerts, setAlerts] = useState<any[]>(DEMO_ALERTS);

  useEffect(() => {
    if (liveData?.threat_intel) {
      setAlerts((prev) => [liveData.threat_intel, ...prev].slice(0, 15));
    }
  }, [liveData]);

  const severityColor: Record<string, string> = {
    critical: "text-red-400 bg-red-400/10",
    high: "text-amber-400 bg-amber-400/10",
    medium: "text-yellow-400 bg-yellow-400/10",
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-2 mb-2">
        <Globe className="w-4 h-4 text-aegis-purple" />
        <p className="text-[10px] text-slate-500 uppercase tracking-wider">Threat Intel (Recorded Future)</p>
      </div>
      <AnimatePresence>
        {alerts.map((alert, i) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.15 }}
            className="flex items-start gap-2 p-2 rounded-lg bg-white border border-slate-200"
          >
            <ShieldAlert className="w-3.5 h-3.5 mt-0.5 text-aegis-amber shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-[11px] text-slate-800 leading-tight">{alert.message}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-[9px] px-1.5 py-0.5 rounded ${severityColor[alert.severity]}`}>
                  {alert.severity.toUpperCase()}
                </span>
                <span className="text-[9px] text-slate-500">{alert.time}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

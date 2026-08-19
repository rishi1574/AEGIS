"use client";
import { motion } from "framer-motion";

export default function SystemHardnessDial({ score = 68 }: { score?: number }) {
  const rotation = (score / 100) * 180 - 90; // -90 to 90 degrees
  const color = score > 80 ? "#22c55e" : score > 50 ? "#f59e0b" : "#ef4444";
  const label = score > 80 ? "HARDENED" : score > 50 ? "MODERATE" : "VULNERABLE";

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-16 overflow-hidden">
        {/* Background arc */}
        <svg viewBox="0 0 120 60" className="w-full h-full">
          <path d="M 10 55 A 50 50 0 0 1 110 55" fill="none" stroke="#1e293b" strokeWidth="8" strokeLinecap="round" />
          <motion.path
            d="M 10 55 A 50 50 0 0 1 110 55"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: score / 100 }}
            transition={{ duration: 2, ease: "easeOut" }}
          />
        </svg>
      </div>
      <p className="text-2xl font-bold font-mono mt-1" style={{ color }}>{score}</p>
      <p className="text-[10px] uppercase tracking-wider" style={{ color }}>{label}</p>
    </div>
  );
}

"use client";
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export function Tooltip({ children, content }: { children: React.ReactNode; content: React.ReactNode }) {
  const [show, setShow] = useState(false);

  return (
    <div 
      className="relative flex items-center" 
      onMouseEnter={() => setShow(true)} 
      onMouseLeave={() => setShow(false)}
      onClick={() => setShow(!show)}
    >
      {children}
      <AnimatePresence>
        {show && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 5 }}
            transition={{ duration: 0.15 }}
            className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-xs bg-slate-800 text-white text-[11px] px-3 py-1.5 rounded-md shadow-lg z-[9999] pointer-events-none"
          >
            {content}
            <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-slate-800" />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

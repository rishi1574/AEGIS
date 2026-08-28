"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Play, ChevronRight, Check } from "lucide-react";

const TOUR_STEPS = [
  {
    target: ".tour-red-team",
    content: "The Red Team Console lets you simulate advanced, multi-vector attacks.",
  },
  {
    target: ".tour-transaction-network",
    content: "The Battlefield Graph visualizes live transactions and anomalous paths.",
  },
  {
    target: ".tour-blue-team",
    content: "The Blue Team Console monitors defensive metrics and intercepted threats.",
  },
  {
    target: ".tour-federated",
    content: "Federated Intelligence aggregates insights from multiple financial institutions.",
  }
];

export default function SimulationTour() {
  const [showPrompt, setShowPrompt] = useState(false);
  const [runTour, setRunTour] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [mounted, setMounted] = useState(false);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    setMounted(true);
    const timer = setTimeout(() => setShowPrompt(true), 500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!runTour) return;

    const updateRect = () => {
      const step = TOUR_STEPS[stepIndex];
      if (!step) return;
      const el = document.querySelector(step.target);
      if (el) {
        setTargetRect(el.getBoundingClientRect());
      } else {
        setTargetRect(null);
      }
    };

    updateRect();
    window.addEventListener("resize", updateRect);
    window.addEventListener("scroll", updateRect);
    return () => {
      window.removeEventListener("resize", updateRect);
      window.removeEventListener("scroll", updateRect);
    };
  }, [runTour, stepIndex]);

  if (!mounted) return null;

  const nextStep = () => {
    if (stepIndex < TOUR_STEPS.length - 1) {
      setStepIndex((s) => s + 1);
    } else {
      setRunTour(false);
      setStepIndex(0);
    }
  };

  const skipTour = () => {
    setRunTour(false);
    setStepIndex(0);
  };

  return (
    <>
      <AnimatePresence>
        {showPrompt && !runTour && (
          <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/20 backdrop-blur-sm">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white rounded-xl shadow-xl border border-slate-200 p-6 max-w-sm w-full mx-4"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-bold text-slate-800">Welcome to Aegis</h3>
                <button 
                  onClick={() => setShowPrompt(false)}
                  className="p-1 hover:bg-slate-100 rounded-md text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                Would you like a quick tour of the simulation dashboard?
              </p>
              <div className="flex gap-3 justify-end">
                <button 
                  onClick={() => setShowPrompt(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Skip
                </button>
                <button 
                  onClick={() => {
                    setShowPrompt(false);
                    setRunTour(true);
                  }}
                  className="px-4 py-2 text-sm font-medium text-white bg-slate-900 rounded-lg hover:bg-slate-800 transition-colors flex items-center gap-2"
                >
                  <Play className="w-4 h-4" /> Start Tour
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {runTour && targetRect && (
          <div className="fixed inset-0 z-[10000] pointer-events-none">
            {/* Dark Overlay with cutout (simulated via box-shadow) */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute pointer-events-auto"
              style={{
                top: targetRect.top - 8,
                left: targetRect.left - 8,
                width: targetRect.width + 16,
                height: targetRect.height + 16,
                boxShadow: "0 0 0 9999px rgba(0, 0, 0, 0.5)",
                borderRadius: "12px",
                transition: "all 0.3s ease-in-out",
              }}
            />

            {/* Tooltip Card */}
            <motion.div
              key={stepIndex}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ delay: 0.1 }}
              className="absolute pointer-events-auto bg-white rounded-xl shadow-xl border border-slate-200 p-5 w-72"
              style={{
                // Position below if space permits, else above, else center
                top: Math.min(targetRect.bottom + 16, window.innerHeight - 200),
                left: Math.max(16, Math.min(targetRect.left + targetRect.width / 2 - 144, window.innerWidth - 300)),
              }}
            >
              <div className="flex justify-between items-center mb-3">
                <span className="text-xs font-bold text-slate-400 tracking-wider">
                  STEP {stepIndex + 1} OF {TOUR_STEPS.length}
                </span>
                <button onClick={skipTour} className="text-slate-400 hover:text-slate-600">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-sm text-slate-700 leading-relaxed mb-5">
                {TOUR_STEPS[stepIndex].content}
              </p>
              <div className="flex justify-end">
                <button
                  onClick={nextStep}
                  className="px-4 py-2 text-sm font-medium text-white bg-slate-900 rounded-lg hover:bg-slate-800 transition-colors flex items-center gap-1"
                >
                  {stepIndex === TOUR_STEPS.length - 1 ? (
                    <>Finish <Check className="w-4 h-4" /></>
                  ) : (
                    <>Next <ChevronRight className="w-4 h-4" /></>
                  )}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}

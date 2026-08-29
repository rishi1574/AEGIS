"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Play, ChevronRight, Check } from "lucide-react";

const TOUR_STEPS = [
  {
    target: ".tour-red-team",
    title: "Red Team — Attack Console",
    content:
      "This is where you launch adversarial attacks. Select an attack type (e.g., Synthetic ID Bust-Out) and click 'Launch'. The Red Team uses Reinforcement Learning to evolve its strategy in real-time — mutating transaction amounts, timing, and routes to try to bypass Blue Team defenses.",
  },
  {
    target: ".tour-transaction-network",
    title: "Transaction Network — Live Battlefield",
    content:
      "This is the live visualization of the battle. Gray nodes are normal accounts, blue are merchants, red are mule/fraud nodes. When Blue Team blocks a node, you'll see a pulsing red 'BLOCKED' badge appear. The narrator at the top explains each phase as it happens. Edges show money flow — orange dashed lines mean the RL policy intervened.",
  },
  {
    target: ".tour-blue-team",
    title: "Blue Team — Defensive AI",
    content:
      "The radar chart shows Blue Team's live detection metrics — accuracy, precision, recall, F1, and AUC-ROC. These drop when Red Team mutations succeed and recover as Blue adapts. The interception log below shows real-time block events.",
  },
  {
    target: ".tour-federated",
    title: "Federated Intelligence",
    content:
      "Simulates privacy-preserving federated learning across 3 bank nodes (APAC, EMEA, NAM). Each bank's local model accuracy varies based on the current attack pressure. The global federated model always outperforms individual banks — showing the 'Network Advantage'.",
  },
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
        // Scroll the element into view first
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        setTimeout(() => {
          setTargetRect(el.getBoundingClientRect());
        }, 350);
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
              className="bg-white shadow-xl border border-slate-200 p-6 max-w-md w-full mx-4"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-bold text-slate-800">Welcome to AEGIS Simulator</h3>
                <button
                  onClick={() => setShowPrompt(false)}
                  className="p-1 hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <p className="text-sm text-slate-600 mb-4 leading-relaxed">
                This is a <strong>live adversarial simulation</strong> where Red Team AI attacks and Blue Team AI defends — in real-time.
              </p>
              <div className="text-xs text-slate-500 space-y-2 mb-6 bg-slate-50 p-3 border border-slate-200">
                <p><strong>How it works:</strong></p>
                <p>1. Launch an attack from the Red Team panel (left)</p>
                <p>2. Watch the Transaction Network show nodes getting blocked</p>
                <p>3. See Blue Team radar chart respond as it detects and adapts</p>
                <p>4. Red Team mutates its strategy using RL — creating oscillation in the Co-Evolution chart</p>
              </div>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowPrompt(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 transition-colors"
                >
                  Skip
                </button>
                <button
                  onClick={() => {
                    setShowPrompt(false);
                    setRunTour(true);
                  }}
                  className="px-4 py-2 text-sm font-medium text-white bg-slate-900 hover:bg-slate-800 transition-colors flex items-center gap-2"
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
            {/* Dark Overlay with cutout */}
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
                borderRadius: "4px",
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
              className="absolute pointer-events-auto bg-white shadow-xl border border-slate-200 p-5 w-80"
              style={{
                top: targetRect.bottom + 260 > window.innerHeight 
                  ? Math.max(16, targetRect.top - 240) 
                  : targetRect.bottom + 16,
                left: Math.max(16, Math.min(targetRect.left + targetRect.width / 2 - 160, window.innerWidth - 340)),
              }}
            >
              <div className="flex justify-between items-center mb-2">
                <span className="text-[10px] font-bold text-slate-400 tracking-wider">
                  STEP {stepIndex + 1} OF {TOUR_STEPS.length}
                </span>
                <button onClick={skipTour} className="text-slate-400 hover:text-slate-600">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <h4 className="text-sm font-bold text-slate-900 mb-2">{TOUR_STEPS[stepIndex].title}</h4>
              <p className="text-xs text-slate-600 leading-relaxed mb-5">
                {TOUR_STEPS[stepIndex].content}
              </p>
              <div className="flex justify-between items-center">
                <div className="flex gap-1">
                  {TOUR_STEPS.map((_, i) => (
                    <div key={i} className={`w-2 h-2 rounded-full ${i === stepIndex ? "bg-slate-900" : i < stepIndex ? "bg-slate-400" : "bg-slate-200"}`} />
                  ))}
                </div>
                <button
                  onClick={nextStep}
                  className="px-4 py-2 text-sm font-medium text-white bg-slate-900 hover:bg-slate-800 transition-colors flex items-center gap-1"
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

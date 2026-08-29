# 🎨 Member B — Full-Stack Lead: Complete Coding Guide

> **Role:** Build the AEGIS War Room dashboard (frontend) + Docker infrastructure  
> **Your directories:** `frontend/`, `docker-compose.yml`  
> **Do NOT touch:** `red_team/`, `blue_team/`, `docs/walkthrough*`, `data/`  
> **Stack:** Next.js 14 (App Router) + TypeScript + Tailwind CSS + Recharts + react-force-graph  

---

## SETUP (Day 1 Morning)

```bash
cd /Users/swarup/Mastercard_Innovation_Challenge_2026/aegis

# Scaffold Next.js 14 app
npx -y create-next-app@latest frontend \
  --typescript --tailwind --eslint --app \
  --src-dir --import-alias "@/*" --no-turbopack

cd frontend

# Install all dependencies at once
npm install \
  recharts \
  react-force-graph-2d \
  @radix-ui/react-tabs @radix-ui/react-tooltip @radix-ui/react-scroll-area \
  lucide-react \
  framer-motion \
  socket.io-client \
  class-variance-authority clsx tailwind-merge

# Dev dependencies
npm install -D @types/node
```

---

## DAY 1 — Theme + Layout Shell

### File 1: `frontend/tailwind.config.ts`

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Cybersecurity dark theme palette
        aegis: {
          bg: "#0a0e17",
          surface: "#111827",
          card: "#1a2235",
          border: "#1e293b",
          "border-active": "#3b82f6",
          text: "#e2e8f0",
          "text-muted": "#94a3b8",
          // Red Team colors
          red: "#ef4444",
          "red-glow": "#dc262640",
          "red-bg": "#7f1d1d20",
          // Blue Team colors
          blue: "#3b82f6",
          "blue-glow": "#3b82f640",
          "blue-bg": "#1e3a5f20",
          // Accent
          green: "#22c55e",
          amber: "#f59e0b",
          purple: "#a855f7",
          cyan: "#06b6d4",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "pulse-slow": "pulse 3s ease-in-out infinite",
        "glow-red": "glow-red 2s ease-in-out infinite",
        "glow-blue": "glow-blue 2s ease-in-out infinite",
        "scan-line": "scan-line 4s linear infinite",
        "fade-in": "fade-in 0.5s ease-out",
        "slide-up": "slide-up 0.5s ease-out",
      },
      keyframes: {
        "glow-red": {
          "0%, 100%": { boxShadow: "0 0 5px #ef4444, 0 0 10px #ef444440" },
          "50%": { boxShadow: "0 0 15px #ef4444, 0 0 30px #ef444460" },
        },
        "glow-blue": {
          "0%, 100%": { boxShadow: "0 0 5px #3b82f6, 0 0 10px #3b82f640" },
          "50%": { boxShadow: "0 0 15px #3b82f6, 0 0 30px #3b82f660" },
        },
        "scan-line": {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100vh)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      backgroundImage: {
        "grid-pattern": "linear-gradient(#1e293b 1px, transparent 1px), linear-gradient(90deg, #1e293b 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};
export default config;
```

### File 2: `frontend/src/app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg-primary: #0a0e17;
  --bg-card: #1a2235;
  --border: #1e293b;
  --text: #e2e8f0;
  --red: #ef4444;
  --blue: #3b82f6;
  --green: #22c55e;
}

body {
  background: var(--bg-primary);
  color: var(--text);
  font-family: 'Inter', system-ui, sans-serif;
}

/* Glassmorphism card */
.glass-card {
  background: rgba(26, 34, 53, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(30, 41, 59, 0.8);
  border-radius: 12px;
}

/* Glowing borders */
.glow-red { box-shadow: 0 0 8px #ef444440, inset 0 0 8px #ef444410; }
.glow-blue { box-shadow: 0 0 8px #3b82f640, inset 0 0 8px #3b82f610; }
.glow-green { box-shadow: 0 0 8px #22c55e40, inset 0 0 8px #22c55e10; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #475569; }

/* Grid background */
.grid-bg {
  background-size: 30px 30px;
  background-image:
    linear-gradient(to right, rgba(30,41,59,0.3) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(30,41,59,0.3) 1px, transparent 1px);
}

/* Status indicators */
.status-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.status-dot.active { background: #22c55e; box-shadow: 0 0 6px #22c55e; }
.status-dot.warning { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.status-dot.danger { background: #ef4444; box-shadow: 0 0 6px #ef4444; }

/* Stat card number animation */
@keyframes count-up {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
.stat-value { animation: count-up 0.6s ease-out; }
```

### File 3: `frontend/src/app/layout.tsx`

```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AEGIS — AI Defense Lab | Mastercard Innovation Challenge 2026",
  description: "Adversarial Evolution & Generative Intelligence Shield — Red Team/Blue Team AI system for payment fraud defense",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-aegis-bg text-aegis-text antialiased">
        {children}
      </body>
    </html>
  );
}
```

### File 4: `frontend/src/lib/utils.ts`

```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return n.toFixed(0);
}

export function formatINR(amount: number): string {
  return "₹" + amount.toLocaleString("en-IN");
}

export function formatPercent(n: number): string {
  return (n * 100).toFixed(1) + "%";
}
```

### File 5: `frontend/src/hooks/useWebSocket.ts`

```typescript
"use client";
import { useEffect, useRef, useState, useCallback } from "react";

interface WSMessage {
  type: string;
  data?: any;
  message?: string;
}

export function useWebSocket(url: string = "ws://localhost:8000/ws/live-feed") {
  const ws = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const [messages, setMessages] = useState<WSMessage[]>([]);

  useEffect(() => {
    const socket = new WebSocket(url);
    socket.onopen = () => setConnected(true);
    socket.onclose = () => { setConnected(false); setTimeout(() => {}, 3000); };
    socket.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        setLastMessage(msg);
        setMessages((prev) => [...prev.slice(-200), msg]); // Keep last 200
      } catch {}
    };
    ws.current = socket;
    return () => { socket.close(); };
  }, [url]);

  const send = useCallback((msg: WSMessage) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(msg));
    }
  }, []);

  return { connected, lastMessage, messages, send };
}
```

### File 6: `frontend/src/hooks/useApi.ts`

```typescript
"use client";
import { useState, useCallback } from "react";

const API_BASE = "http://localhost:8000";

export function useApi() {
  const [loading, setLoading] = useState(false);

  const get = useCallback(async (path: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}${path}`);
      return await res.json();
    } finally {
      setLoading(false);
    }
  }, []);

  const post = useCallback(async (path: string, body: any) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      return await res.json();
    } finally {
      setLoading(false);
    }
  }, []);

  return { get, post, loading };
}
```

---

## DAY 2 — War Room Layout

### File 7: `frontend/src/app/page.tsx` (Main War Room)

```tsx
"use client";
import { useState, useEffect } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useApi } from "@/hooks/useApi";
import Header from "@/components/war-room/Header";
import RedTeamConsole from "@/components/war-room/RedTeamConsole";
import BattlefieldGraph from "@/components/war-room/BattlefieldGraph";
import BlueTeamConsole from "@/components/war-room/BlueTeamConsole";
import ConceptDriftChart from "@/components/war-room/ConceptDriftChart";
import FederatedComparison from "@/components/war-room/FederatedComparison";
import StatsBar from "@/components/war-room/StatsBar";

export default function WarRoom() {
  const { connected, lastMessage, messages, send } = useWebSocket();
  const { get, post } = useApi();
  const [metrics, setMetrics] = useState<any>(null);
  const [attacks, setAttacks] = useState<any[]>([]);
  const [federated, setFederated] = useState<any>(null);

  useEffect(() => {
    // Load initial data
    get("/api/blue-team/metrics").then(setMetrics);
    get("/api/red-team/attacks").then((d) => setAttacks(d?.attacks || []));
    get("/api/blue-team/federated-comparison").then(setFederated);
  }, [get]);

  const launchAttack = async (attackType: string) => {
    const result = await post("/api/red-team/launch", { attack_type: attackType });
    send({ type: "launch_attack", attack_type: attackType });
    return result;
  };

  return (
    <div className="min-h-screen bg-aegis-bg grid-bg">
      <Header connected={connected} />

      {/* Main 3-Column Layout */}
      <div className="grid grid-cols-12 gap-3 p-3 h-[calc(100vh-120px)]">
        {/* Left: Red Team */}
        <div className="col-span-3">
          <RedTeamConsole attacks={attacks} onLaunch={launchAttack} messages={messages} />
        </div>

        {/* Center: Battlefield */}
        <div className="col-span-5">
          <BattlefieldGraph messages={messages} />
        </div>

        {/* Right: Blue Team */}
        <div className="col-span-4">
          <BlueTeamConsole metrics={metrics} />
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-12 gap-3 px-3 pb-3" style={{ height: "280px" }}>
        <div className="col-span-7">
          <ConceptDriftChart />
        </div>
        <div className="col-span-5">
          <FederatedComparison data={federated} />
        </div>
      </div>

      {/* Stats Footer */}
      <StatsBar metrics={metrics} connected={connected} />
    </div>
  );
}
```

---

## DAY 2-3 — All Components

### File 8: `frontend/src/components/war-room/Header.tsx`

```tsx
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
```

### File 9: `frontend/src/components/war-room/RedTeamConsole.tsx`

```tsx
"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Crosshair, Zap, AlertTriangle, ChevronRight } from "lucide-react";

interface Attack {
  id: string;
  name: string;
  layer: string;
  risk: string;
}

interface Props {
  attacks: Attack[];
  onLaunch: (type: string) => Promise<any>;
  messages: any[];
}

const LAYER_COLORS: Record<string, string> = {
  identity: "text-purple-400 bg-purple-400/10 border-purple-400/30",
  network: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  human: "text-rose-400 bg-rose-400/10 border-rose-400/30",
  emerging: "text-cyan-400 bg-cyan-400/10 border-cyan-400/30",
};

export default function RedTeamConsole({ attacks, onLaunch, messages }: Props) {
  const [launching, setLaunching] = useState<string | null>(null);
  const [log, setLog] = useState<string[]>([]);

  const handleLaunch = async (attackId: string) => {
    setLaunching(attackId);
    setLog((prev) => [...prev, `⚡ Launching ${attackId}...`]);
    try {
      const result = await onLaunch(attackId);
      setLog((prev) => [...prev, `✅ ${result.message}`]);
    } catch (e) {
      setLog((prev) => [...prev, `❌ Failed to launch ${attackId}`]);
    }
    setTimeout(() => setLaunching(null), 1000);
  };

  return (
    <div className="glass-card glow-red h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-aegis-border">
        <Crosshair className="w-5 h-5 text-aegis-red" />
        <h2 className="text-sm font-semibold text-aegis-red uppercase tracking-wider">Red Team</h2>
        <span className="ml-auto text-xs text-aegis-text-muted">{attacks.length} vectors</span>
      </div>

      {/* Attack List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {attacks.map((atk) => (
          <motion.button
            key={atk.id}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => handleLaunch(atk.id)}
            disabled={launching === atk.id}
            className={`w-full text-left p-2.5 rounded-lg border transition-all group
              ${launching === atk.id
                ? "border-aegis-red bg-aegis-red/10 animate-pulse"
                : "border-aegis-border hover:border-aegis-red/50 hover:bg-aegis-red/5"}`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-aegis-text">{atk.name}</span>
              <ChevronRight className="w-3.5 h-3.5 text-aegis-text-muted group-hover:text-aegis-red transition-colors" />
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-[10px] px-1.5 py-0.5 rounded border ${LAYER_COLORS[atk.layer] || ""}`}>
                {atk.layer}
              </span>
              {atk.risk === "critical" && (
                <span className="text-[10px] text-aegis-red flex items-center gap-0.5">
                  <AlertTriangle className="w-3 h-3" /> CRITICAL
                </span>
              )}
            </div>
          </motion.button>
        ))}
      </div>

      {/* Agent Thought Stream (Log) */}
      <div className="border-t border-aegis-border p-2 max-h-32 overflow-y-auto">
        <p className="text-[10px] text-aegis-text-muted uppercase tracking-wider mb-1">Agent Log</p>
        <div className="space-y-0.5 font-mono text-[11px]">
          <AnimatePresence>
            {log.slice(-8).map((entry, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-aegis-text-muted"
              >
                {entry}
              </motion.div>
            ))}
          </AnimatePresence>
          {log.length === 0 && (
            <span className="text-aegis-text-muted/50">Awaiting orders...</span>
          )}
        </div>
      </div>
    </div>
  );
}
```

### File 10: `frontend/src/components/war-room/BlueTeamConsole.tsx`

```tsx
"use client";
import { Shield, TrendingUp, Eye } from "lucide-react";

interface Metrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  auc_roc: number;
  false_positive_rate: number;
  avg_inference_latency_ms: number;
  total_predictions: number;
  adversarial_iteration: number;
}

export default function BlueTeamConsole({ metrics }: { metrics: Metrics | null }) {
  const m = metrics || {
    accuracy: 0, precision: 0, recall: 0, f1_score: 0,
    auc_roc: 0, false_positive_rate: 0, avg_inference_latency_ms: 0,
    total_predictions: 0, adversarial_iteration: 0,
  };

  const bars = [
    { label: "Accuracy", value: m.accuracy, color: "bg-blue-500" },
    { label: "Precision", value: m.precision, color: "bg-cyan-500" },
    { label: "Recall", value: m.recall, color: "bg-emerald-500" },
    { label: "F1 Score", value: m.f1_score, color: "bg-violet-500" },
    { label: "AUC-ROC", value: m.auc_roc, color: "bg-amber-500" },
  ];

  return (
    <div className="glass-card glow-blue h-full flex flex-col overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-aegis-border">
        <Shield className="w-5 h-5 text-aegis-blue" />
        <h2 className="text-sm font-semibold text-aegis-blue uppercase tracking-wider">Blue Team</h2>
        <span className="ml-auto text-xs font-mono text-aegis-text-muted">
          Iter #{m.adversarial_iteration}
        </span>
      </div>

      {/* Metrics Bars */}
      <div className="p-4 space-y-3 flex-1">
        {bars.map((b) => (
          <div key={b.label}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-aegis-text-muted">{b.label}</span>
              <span className="font-mono font-semibold text-aegis-text">
                {(b.value * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full h-2 bg-aegis-border rounded-full overflow-hidden">
              <div
                className={`h-full ${b.color} rounded-full transition-all duration-1000`}
                style={{ width: `${b.value * 100}%` }}
              />
            </div>
          </div>
        ))}

        {/* Stat Cards */}
        <div className="grid grid-cols-2 gap-2 mt-4">
          <div className="bg-aegis-surface rounded-lg p-3 border border-aegis-border">
            <p className="text-[10px] text-aegis-text-muted uppercase">Latency</p>
            <p className="text-lg font-bold font-mono text-aegis-green">
              {m.avg_inference_latency_ms.toFixed(0)}ms
            </p>
          </div>
          <div className="bg-aegis-surface rounded-lg p-3 border border-aegis-border">
            <p className="text-[10px] text-aegis-text-muted uppercase">FPR</p>
            <p className="text-lg font-bold font-mono text-aegis-amber">
              {(m.false_positive_rate * 100).toFixed(2)}%
            </p>
          </div>
        </div>
      </div>

      {/* Interception Log Placeholder */}
      <div className="border-t border-aegis-border p-3">
        <div className="flex items-center gap-2 mb-2">
          <Eye className="w-4 h-4 text-aegis-blue" />
          <p className="text-[10px] text-aegis-text-muted uppercase tracking-wider">Recent Interceptions</p>
        </div>
        <div className="text-xs text-aegis-text-muted/50 font-mono text-center py-2">
          Awaiting live data...
        </div>
      </div>
    </div>
  );
}
```

### File 11: `frontend/src/components/war-room/BattlefieldGraph.tsx`

```tsx
"use client";
import { useRef, useEffect, useState, useMemo } from "react";
import { Network, Zap } from "lucide-react";

// Simple canvas-based force graph (no heavy 3D dependency needed initially)
// Replace with react-force-graph-2d when backend is connected

interface GraphNode {
  id: string;
  type: "account" | "merchant" | "mule";
  x: number;
  y: number;
}

interface GraphEdge {
  source: string;
  target: string;
  isFraud: boolean;
}

export default function BattlefieldGraph({ messages }: { messages: any[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [nodeCount, setNodeCount] = useState(0);

  // Generate demo graph data
  const graphData = useMemo(() => {
    const nodes: GraphNode[] = [];
    const edges: GraphEdge[] = [];

    // Create a small demo network
    for (let i = 0; i < 40; i++) {
      nodes.push({
        id: `N${i}`,
        type: i < 30 ? "account" : i < 38 ? "merchant" : "mule",
        x: 200 + Math.cos((i / 40) * Math.PI * 2) * (120 + Math.random() * 80),
        y: 180 + Math.sin((i / 40) * Math.PI * 2) * (100 + Math.random() * 60),
      });
    }

    for (let i = 0; i < 60; i++) {
      const src = Math.floor(Math.random() * 30);
      const tgt = 30 + Math.floor(Math.random() * 10);
      edges.push({
        source: `N${src}`,
        target: `N${tgt}`,
        isFraud: Math.random() < 0.15,
      });
    }
    return { nodes, edges };
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const w = canvas.width = canvas.offsetWidth;
    const h = canvas.height = canvas.offsetHeight;

    let frame: number;
    let t = 0;

    const draw = () => {
      ctx.clearRect(0, 0, w, h);

      // Draw edges
      graphData.edges.forEach((e) => {
        const src = graphData.nodes.find((n) => n.id === e.source);
        const tgt = graphData.nodes.find((n) => n.id === e.target);
        if (!src || !tgt) return;

        ctx.beginPath();
        ctx.strokeStyle = e.isFraud ? "#ef444480" : "#3b82f620";
        ctx.lineWidth = e.isFraud ? 2 : 0.5;
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);
        ctx.stroke();

        // Animated particle on fraud edges
        if (e.isFraud) {
          const progress = (t * 0.02) % 1;
          const px = src.x + (tgt.x - src.x) * progress;
          const py = src.y + (tgt.y - src.y) * progress;
          ctx.beginPath();
          ctx.fillStyle = "#ef4444";
          ctx.arc(px, py, 3, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      // Draw nodes
      graphData.nodes.forEach((n) => {
        const jitter = Math.sin(t * 0.03 + parseInt(n.id.slice(1)) * 0.5) * 1.5;
        const x = n.x + jitter;
        const y = n.y + jitter;

        ctx.beginPath();
        const color = n.type === "mule" ? "#ef4444" :
                      n.type === "merchant" ? "#f59e0b" : "#3b82f6";
        ctx.fillStyle = color;
        ctx.arc(x, y, n.type === "mule" ? 6 : 4, 0, Math.PI * 2);
        ctx.fill();

        // Glow for mule nodes
        if (n.type === "mule") {
          ctx.beginPath();
          ctx.fillStyle = "#ef444430";
          ctx.arc(x, y, 12 + Math.sin(t * 0.05) * 3, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      t++;
      frame = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(frame);
  }, [graphData]);

  return (
    <div className="glass-card h-full flex flex-col overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-aegis-border">
        <Network className="w-5 h-5 text-aegis-amber" />
        <h2 className="text-sm font-semibold text-aegis-amber uppercase tracking-wider">
          Transaction Network
        </h2>
        <div className="ml-auto flex items-center gap-3 text-[10px]">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500" /> Normal</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" /> Fraud</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500" /> Merchant</span>
        </div>
      </div>
      <div className="flex-1 relative">
        <canvas ref={canvasRef} className="w-full h-full" />
      </div>
    </div>
  );
}
```

### File 12: `frontend/src/components/war-room/ConceptDriftChart.tsx`

```tsx
"use client";
import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import { TrendingUp, Activity } from "lucide-react";
import { useApi } from "@/hooks/useApi";

// Demo data simulating adversarial co-evolution
const DEMO_DATA = Array.from({ length: 30 }, (_, i) => {
  const baseBlue = 0.85 + (i / 30) * 0.10;
  const redSpike = (i % 7 === 5) ? 0.15 : 0;
  return {
    iteration: i + 1,
    blue_accuracy: Math.min(0.98, baseBlue - redSpike * 0.8 + Math.random() * 0.02),
    red_bypass: Math.max(0, 0.15 - (i / 30) * 0.10 + redSpike + (Math.random() - 0.5) * 0.03),
  };
});

export default function ConceptDriftChart() {
  const [data, setData] = useState(DEMO_DATA);

  return (
    <div className="glass-card h-full flex flex-col">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-aegis-border">
        <Activity className="w-5 h-5 text-aegis-amber" />
        <h2 className="text-sm font-semibold text-aegis-amber uppercase tracking-wider">
          Adversarial Co-Evolution
        </h2>
        <span className="ml-auto text-[10px] text-aegis-text-muted font-mono">
          {data.length} iterations
        </span>
      </div>
      <div className="flex-1 p-3">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="redGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="iteration" tick={{ fontSize: 10, fill: "#94a3b8" }} />
            <YAxis tick={{ fontSize: 10, fill: "#94a3b8" }} domain={[0, 1]}
                   tickFormatter={(v: number) => `${(v*100).toFixed(0)}%`} />
            <Tooltip
              contentStyle={{ background: "#1a2235", border: "1px solid #1e293b", borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: "#94a3b8" }}
              formatter={(value: number, name: string) => [
                `${(value * 100).toFixed(1)}%`,
                name === "blue_accuracy" ? "🛡️ Blue Team Accuracy" : "🔴 Red Team Bypass"
              ]}
            />
            <Area type="monotone" dataKey="blue_accuracy" stroke="#3b82f6" strokeWidth={2}
                  fillOpacity={1} fill="url(#blueGrad)" dot={false} />
            <Area type="monotone" dataKey="red_bypass" stroke="#ef4444" strokeWidth={2}
                  fillOpacity={1} fill="url(#redGrad)" dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
```

### File 13: `frontend/src/components/war-room/FederatedComparison.tsx`

```tsx
"use client";
import { Globe, ArrowUp } from "lucide-react";
import { motion } from "framer-motion";

interface BankData {
  name: string;
  f1: number;
  auc: number;
  txn_count: number;
}

interface FederatedData {
  banks: BankData[];
  federated: { f1: number; auc: number; improvement: string };
}

// Fallback demo data
const DEMO: FederatedData = {
  banks: [
    { name: "Bank A", f1: 0.82, auc: 0.89, txn_count: 35000 },
    { name: "Bank B", f1: 0.79, auc: 0.86, txn_count: 30000 },
    { name: "Bank C", f1: 0.84, auc: 0.91, txn_count: 35000 },
  ],
  federated: { f1: 0.93, auc: 0.97, improvement: "+12.8%" },
};

export default function FederatedComparison({ data }: { data: FederatedData | null }) {
  const d = data || DEMO;

  return (
    <div className="glass-card glow-green h-full flex flex-col">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-aegis-border">
        <Globe className="w-5 h-5 text-aegis-green" />
        <h2 className="text-sm font-semibold text-aegis-green uppercase tracking-wider">
          Federated Intelligence
        </h2>
      </div>
      <div className="flex-1 p-4 space-y-2">
        {/* Individual Banks */}
        {d.banks.map((bank, i) => (
          <div key={bank.name} className="flex items-center gap-3">
            <span className="text-xs text-aegis-text-muted w-14 shrink-0">{bank.name}</span>
            <div className="flex-1 h-5 bg-aegis-border rounded-full overflow-hidden relative">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${bank.f1 * 100}%` }}
                transition={{ duration: 1, delay: i * 0.2 }}
                className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full"
              />
            </div>
            <span className="text-xs font-mono font-semibold w-12 text-right">{(bank.f1 * 100).toFixed(1)}%</span>
          </div>
        ))}

        {/* Divider */}
        <div className="border-t border-dashed border-aegis-border my-2" />

        {/* Federated Result */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-aegis-green font-semibold w-14 shrink-0">🌐 Fed.</span>
          <div className="flex-1 h-6 bg-aegis-border rounded-full overflow-hidden relative">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${d.federated.f1 * 100}%` }}
              transition={{ duration: 1.5, delay: 0.8 }}
              className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full"
            />
          </div>
          <span className="text-sm font-mono font-bold text-aegis-green w-12 text-right">
            {(d.federated.f1 * 100).toFixed(1)}%
          </span>
        </div>

        {/* Improvement Badge */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1.5 }}
          className="flex items-center justify-center gap-2 mt-3 py-2 px-3 rounded-lg bg-aegis-green/10 border border-aegis-green/30"
        >
          <ArrowUp className="w-4 h-4 text-aegis-green" />
          <span className="text-sm font-semibold text-aegis-green">
            {d.federated.improvement} Network Intelligence Advantage
          </span>
        </motion.div>

        <p className="text-[10px] text-aegis-text-muted text-center mt-1">
          Cross-bank mule chains only detectable with federated model
        </p>
      </div>
    </div>
  );
}
```

### File 14: `frontend/src/components/war-room/StatsBar.tsx`

```tsx
"use client";
import { formatNumber } from "@/lib/utils";

export default function StatsBar({ metrics, connected }: { metrics: any; connected: boolean }) {
  const stats = [
    { label: "Txns Processed", value: formatNumber(metrics?.total_predictions || 127432) },
    { label: "Attacks Generated", value: formatNumber(2548) },
    { label: "Blocked", value: "2,391 (93.8%)" },
    { label: "Avg Latency", value: `${metrics?.avg_inference_latency_ms?.toFixed(0) || 34}ms` },
    { label: "Adversarial Iter", value: `${metrics?.adversarial_iteration || 47}` },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-aegis-surface/90 backdrop-blur-md border-t border-aegis-border px-4 py-1.5">
      <div className="flex items-center justify-center gap-6">
        {stats.map((s) => (
          <div key={s.label} className="flex items-center gap-1.5 text-xs">
            <span className="text-aegis-text-muted">{s.label}:</span>
            <span className="font-mono font-semibold text-aegis-text">{s.value}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5 text-xs">
          <span className={`status-dot ${connected ? "active" : "danger"}`} />
          <span className="text-aegis-text-muted">{connected ? "Connected" : "Disconnected"}</span>
        </div>
      </div>
    </div>
  );
}
```

---

## DAY 4-5 — Additional Panels

### File 15: `frontend/src/components/war-room/ShapWaterfall.tsx`

```tsx
"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface Props {
  shapValues: Record<string, number> | null;
  transactionId?: string;
}

export default function ShapWaterfall({ shapValues, transactionId }: Props) {
  if (!shapValues) {
    return (
      <div className="text-xs text-aegis-text-muted text-center py-6">
        Click a transaction to see SHAP explanation
      </div>
    );
  }

  const data = Object.entries(shapValues)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 6)
    .map(([feature, value]) => ({
      feature: feature.replace(/_/g, " ").replace(/enc$/, ""),
      value: Number(value.toFixed(4)),
    }));

  return (
    <div>
      <p className="text-[10px] text-aegis-text-muted mb-2 font-mono">
        SHAP — {transactionId || "Transaction"}
      </p>
      <ResponsiveContainer width="100%" height={150}>
        <BarChart data={data} layout="vertical" margin={{ left: 80, right: 10, top: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 9, fill: "#94a3b8" }} />
          <YAxis type="category" dataKey="feature" tick={{ fontSize: 9, fill: "#94a3b8" }} width={80} />
          <Tooltip contentStyle={{ background: "#1a2235", border: "1px solid #1e293b", borderRadius: 8, fontSize: 11 }} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.value > 0 ? "#ef4444" : "#3b82f6"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
```

### File 16: `frontend/src/components/war-room/SystemHardnessDial.tsx`

```tsx
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
```

---

## DAY 6-7 — Polish + Remaining Components

### File 17: `frontend/src/components/war-room/ThreatIntelFeed.tsx`

```tsx
"use client";
import { AlertTriangle, ShieldAlert, Globe } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const DEMO_ALERTS = [
  { id: 1, type: "darkweb", message: "10K compromised cards detected on Genesis Market", time: "2m ago", severity: "critical" },
  { id: 2, type: "magecart", message: "Magecart skimmer found on travel-booking-xyz.in", time: "12m ago", severity: "high" },
  { id: 3, type: "mule", message: "New mule recruitment campaign via Telegram (Mumbai)", time: "34m ago", severity: "high" },
  { id: 4, type: "apt", message: "FIN7 TTPs observed in card-not-present attacks", time: "1h ago", severity: "medium" },
];

export default function ThreatIntelFeed() {
  const severityColor: Record<string, string> = {
    critical: "text-red-400 bg-red-400/10",
    high: "text-amber-400 bg-amber-400/10",
    medium: "text-yellow-400 bg-yellow-400/10",
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-2 mb-2">
        <Globe className="w-4 h-4 text-aegis-purple" />
        <p className="text-[10px] text-aegis-text-muted uppercase tracking-wider">Threat Intel (Recorded Future)</p>
      </div>
      <AnimatePresence>
        {DEMO_ALERTS.map((alert, i) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.15 }}
            className="flex items-start gap-2 p-2 rounded-lg bg-aegis-surface border border-aegis-border"
          >
            <ShieldAlert className="w-3.5 h-3.5 mt-0.5 text-aegis-amber shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-[11px] text-aegis-text leading-tight">{alert.message}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-[9px] px-1.5 py-0.5 rounded ${severityColor[alert.severity]}`}>
                  {alert.severity.toUpperCase()}
                </span>
                <span className="text-[9px] text-aegis-text-muted">{alert.time}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
```

### File 18: `frontend/src/components/war-room/KYAMonitor.tsx`

```tsx
"use client";
import { Bot, ShieldCheck, ShieldX } from "lucide-react";
import { motion } from "framer-motion";

const DEMO_EVENTS = [
  { id: 1, agent: "ShopBot-A42", action: "Purchase ₹29.99 BT Speaker", status: "allowed", reason: "Within spending limit" },
  { id: 2, agent: "ShopBot-A42", action: "Add ₹500 Gift Card", status: "blocked", reason: "Prompt injection detected in product page" },
  { id: 3, agent: "PayBot-M17", action: "50,000 × ₹0.01 micro-txns", status: "blocked", reason: "Velocity anomaly: machine-speed burst" },
  { id: 4, agent: "TravelBot-R8", action: "Book flight ₹12,400", status: "allowed", reason: "Matches user intent profile" },
];

export default function KYAMonitor() {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-2 mb-2">
        <Bot className="w-4 h-4 text-aegis-purple" />
        <p className="text-[10px] text-aegis-text-muted uppercase tracking-wider">Know Your Agent (AP4M)</p>
      </div>
      {DEMO_EVENTS.map((evt, i) => (
        <motion.div
          key={evt.id}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className={`p-2 rounded-lg border text-[11px] ${
            evt.status === "blocked"
              ? "border-red-500/30 bg-red-500/5"
              : "border-green-500/30 bg-green-500/5"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-mono font-semibold text-aegis-text">{evt.agent}</span>
            {evt.status === "blocked" ? (
              <ShieldX className="w-3.5 h-3.5 text-red-400" />
            ) : (
              <ShieldCheck className="w-3.5 h-3.5 text-green-400" />
            )}
          </div>
          <p className="text-aegis-text-muted mt-0.5">{evt.action}</p>
          <p className="text-[9px] text-aegis-text-muted/70 mt-0.5 italic">{evt.reason}</p>
        </motion.div>
      ))}
    </div>
  );
}
```

---

## DAY 8 — Docker Compose

### File 19: `docker-compose.yml` (in `aegis/` root)

```yaml
version: "3.9"

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_WS_URL=ws://backend:8000
    depends_on:
      - backend

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./data:/app/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/aegis2026
    volumes:
      - neo4j_data:/data

volumes:
  neo4j_data:
```

### File 20: `frontend/Dockerfile`

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

### File 21: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## DAY 9-10 — Integration + Polish

### Integration Checklist:
- `[ ]` Replace all demo/mock data with real API calls
- `[ ]` Connect BattlefieldGraph to real transaction stream via WebSocket
- `[ ]` Connect ConceptDriftChart to `GET /api/blue-team/concept-drift`
- `[ ]` Connect FederatedComparison to `GET /api/blue-team/federated-comparison`
- `[ ]` Connect metrics bars to `GET /api/blue-team/metrics`
- `[ ]` Connect RedTeamConsole launcher to `POST /api/red-team/launch`
- `[ ]` Add SHAP waterfall popup when clicking interceptions
- `[ ]` Test full flow: Launch attack → See graph animate → See block → See SHAP
- `[ ]` Mobile responsive check
- `[ ]` Screenshot capture for deck (Member C needs these)
- `[ ]` Docker Compose build + test on clean environment

### Polish Checklist:
- `[ ]` Glassmorphism effects working in all cards
- `[ ]` All animations smooth (no jank)
- `[ ]` Color consistency (Red=attack, Blue=defense, Green=federated, Amber=warnings)
- `[ ]` Font sizes readable on projector (demo scenario)
- `[ ]` Loading states for all API calls
- `[ ]` Error states graceful (not blank screens)

---

## API ENDPOINTS MEMBER B CONSUMES

```
GET  /api/health
GET  /api/red-team/attacks
POST /api/red-team/launch           body: {attack_type, params?}
GET  /api/red-team/status/:campaignId
GET  /api/blue-team/metrics
POST /api/blue-team/predict          body: {transaction: {...}}
GET  /api/blue-team/federated-comparison
GET  /api/blue-team/concept-drift
GET  /api/blue-team/interception-log
GET  /api/simulation/status
GET  /api/simulation/system-hardness
WS   /ws/live-feed
```

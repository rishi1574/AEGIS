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

export default function BattlefieldGraph({ liveData }: { liveData?: any }) {
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
      const isFraudEdge = Math.random() < 0.15 + (liveData?.current_bypass_rate || 0);
      edges.push({
        source: `N${src}`,
        target: `N${tgt}`,
        isFraud: isFraudEdge,
      });
    }
    return { nodes, edges };
  }, [liveData]);

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

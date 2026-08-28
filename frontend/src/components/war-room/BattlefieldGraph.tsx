"use client";
import { useState, useMemo } from "react";
import { Network, Info, ArrowDown, ArrowUp, AlertTriangle } from "lucide-react";
import { Tooltip } from "@/components/ui/Tooltip";
import { motion, AnimatePresence } from "framer-motion";

interface NodeStats {
  type: string;
  totalTxns: number;
  blockedTxns: number;
  riskScore: number;
}

interface GraphNode {
  id: string;
  type: "victim" | "mule" | "merchant" | "synthetic";
  x: number;
  y: number;
  stats: NodeStats;
}

interface GraphEdge {
  source: string;
  target: string;
  isFraud: boolean;
}

export default function BattlefieldGraph({ liveData }: { liveData?: any }) {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  const activeAttack = liveData?.active_attack || "default";

  // Generate dynamic network topology based on the current attack
  const { nodes, edges } = useMemo(() => {
    let generatedNodes: GraphNode[] = [];
    let generatedEdges: GraphEdge[] = [];

    const createNode = (id: string, type: GraphNode["type"], x: number, y: number, txns: number, blocked: number, risk: number) => {
      return { id, type, x, y, stats: { type: type.charAt(0).toUpperCase() + type.slice(1), totalTxns: txns, blockedTxns: blocked, riskScore: risk } };
    };

    if (activeAttack === "merchant_collusion") {
      // Multiple mules targeting specific merchants
      generatedNodes.push(createNode("MCH_801", "merchant", 650, 150, 450, 80, 8.5));
      generatedNodes.push(createNode("MCH_802", "merchant", 650, 250, 320, 40, 9.2));
      for (let i = 0; i < 8; i++) {
        const mId = `MUL_${300 + i}`;
        generatedNodes.push(createNode(mId, "mule", 200 + Math.random() * 200, 50 + Math.random() * 300, 15, 5, 7.8));
        generatedEdges.push({ source: mId, target: Math.random() > 0.5 ? "MCH_801" : "MCH_802", isFraud: true });
      }
    } else if (activeAttack === "synthetic_id_bustout") {
      // Cluster of fake accounts orchestrating a bust-out on a single merchant
      generatedNodes.push(createNode("MCH_999", "merchant", 600, 200, 1200, 450, 9.9));
      for (let i = 0; i < 15; i++) {
        const sId = `SYN_${900 + i}`;
        generatedNodes.push(createNode(sId, "synthetic", 150 + Math.random() * 150, 50 + Math.random() * 300, 50, 50, 9.5));
        generatedEdges.push({ source: sId, target: "MCH_999", isFraud: true });
      }
    } else {
      // Default standard fraud funnel topology
      generatedNodes = [
        createNode("152", "mule", 400, 200, 85, 42, 8.9),
        createNode("101", "victim", 100, 150, 12, 0, 1.2),
        createNode("102", "victim", 150, 80, 24, 1, 1.5),
        createNode("103", "victim", 220, 280, 8, 0, 0.8),
        createNode("104", "victim", 300, 350, 35, 2, 2.1),
        createNode("105", "victim", 280, 120, 15, 0, 1.1),
        createNode("201", "merchant", 650, 120, 890, 12, 3.4),
        createNode("202", "merchant", 700, 260, 450, 5, 2.8),
        createNode("203", "mule", 550, 300, 45, 12, 7.5),
      ];
      generatedEdges = [
        { source: "101", target: "152", isFraud: false },
        { source: "102", target: "152", isFraud: false },
        { source: "103", target: "152", isFraud: true },
        { source: "105", target: "152", isFraud: false },
        { source: "152", target: "201", isFraud: true },
        { source: "152", target: "203", isFraud: true },
        { source: "203", target: "202", isFraud: false },
      ];
    }

    return { nodes: generatedNodes, edges: generatedEdges };
  }, [activeAttack]);

  const connectedNodes = useMemo(() => {
    if (!hoveredNode) return new Set<string>();
    const connected = new Set<string>();
    connected.add(hoveredNode);
    edges.forEach((edge) => {
      if (edge.source === hoveredNode) connected.add(edge.target);
      if (edge.target === hoveredNode) connected.add(edge.source);
    });
    return connected;
  }, [hoveredNode, edges]);

  const hoveredNodeData = hoveredNode ? nodes.find((n) => n.id === hoveredNode) : null;

  return (
    <div className="bg-white border border-slate-200 shadow-sm h-full flex flex-col overflow-hidden rounded-xl">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-200 shrink-0">
        <Network className="w-5 h-5 text-slate-800" />
        <h2 className="text-sm font-semibold text-slate-800 uppercase tracking-wider">
          Transaction Network
        </h2>
        <Tooltip content="Live topology mapping of accounts, mules, and merchants">
          <Info className="w-4 h-4 text-slate-400 cursor-help ml-1" />
        </Tooltip>
        <div className="ml-auto flex items-center gap-4 text-[10px] text-slate-600">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-slate-200 border border-slate-300" /> Victim</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500 border border-blue-600" /> High-Risk (Mule/Merchant)</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full border-2 border-orange-500 flex items-center justify-center"><div className="w-1 h-1 bg-slate-300 rounded-full" /></span> Selected</span>
        </div>
      </div>

      <div className="flex-1 relative bg-[#fafafa]">
        {/* Active Attack Indicator overlay */}
        {activeAttack !== "default" && (
          <div className="absolute top-4 left-4 z-10 flex items-center gap-2 px-3 py-1.5 bg-red-500/10 border border-red-200 rounded-md text-red-700 text-xs font-semibold animate-pulse">
            <AlertTriangle className="w-3.5 h-3.5" />
            DETECTED TOPOLOGY: {activeAttack.replace(/_/g, ' ').toUpperCase()}
          </div>
        )}

        <svg viewBox="0 0 800 400" preserveAspectRatio="xMidYMid meet" className="w-full h-full">
          {edges.map((edge, i) => {
            const src = nodes.find((n) => n.id === edge.source)!;
            const tgt = nodes.find((n) => n.id === edge.target)!;
            if (!src || !tgt) return null;
            
            const isHoveredEdge = hoveredNode && (edge.source === hoveredNode || edge.target === hoveredNode);
            const isFaded = hoveredNode && !isHoveredEdge;

            return (
              <line
                key={i}
                x1={src.x}
                y1={src.y}
                x2={tgt.x}
                y2={tgt.y}
                stroke={isHoveredEdge ? "#3b82f6" : (edge.isFraud && activeAttack !== 'default' ? "#fca5a5" : "#e2e8f0")}
                strokeWidth={isHoveredEdge ? 2.5 : 1.5}
                strokeOpacity={isFaded ? 0.2 : 1}
                className="transition-all duration-300"
              />
            );
          })}

          {nodes.map((node) => {
            const isHovered = hoveredNode === node.id;
            const isFaded = hoveredNode && !connectedNodes.has(node.id);
            
            const fill = node.type === "victim" ? "#e2e8f0" : node.type === "synthetic" ? "#f87171" : "#60a5fa";
            const border = node.type === "victim" ? "#94a3b8" : node.type === "synthetic" ? "#dc2626" : "#3b82f6";
            const radius = node.type === "mule" || node.type === "merchant" ? 14 : 10;

            return (
              <g 
                key={node.id} 
                className="transition-all duration-300 cursor-pointer"
                style={{ opacity: isFaded ? 0.15 : 1 }}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
              >
                {isHovered && (
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={radius + 6}
                    fill="transparent"
                    stroke="#f97316"
                    strokeWidth={3}
                  />
                )}
                
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={radius}
                  fill={fill}
                  stroke={border}
                  strokeWidth={1.5}
                />
                
                {(isHovered || node.type === "merchant" || node.type === "mule") && (
                  <text
                    x={node.x + radius + (isHovered ? 12 : 8)}
                    y={node.y + 3}
                    fontSize={11}
                    fill="#475569"
                    fontFamily="monospace"
                  >
                    {node.id}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        <AnimatePresence>
          {hoveredNodeData && (
            <motion.div
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              className="absolute bg-white border border-slate-200 shadow-xl rounded-lg p-3 w-56 pointer-events-none z-50"
              style={{
                left: `calc(${(hoveredNodeData.x / 800) * 100}% + 20px)`,
                top: `calc(${(hoveredNodeData.y / 400) * 100}% - 70px)`,
              }}
            >
              <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-2">
                <span className="text-xs font-semibold text-slate-800">Node: {hoveredNodeData.id}</span>
              </div>
              <div className="text-[11px] text-slate-600 mb-3">
                Classification: <span className="font-semibold text-slate-800">{hoveredNodeData.stats.type}</span>
              </div>
              
              <div className="grid grid-cols-3 gap-2 text-center text-[10px]">
                <div className="flex flex-col gap-0.5">
                  <span className="text-slate-500 font-semibold">Total Txns</span>
                  <span className="font-mono">{hoveredNodeData.stats.totalTxns}</span>
                  <div className="flex justify-center text-blue-500">
                    <ArrowUp className="w-3 h-3" />
                  </div>
                </div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-slate-500 font-semibold">Blocked</span>
                  <span className="font-mono">{hoveredNodeData.stats.blockedTxns}</span>
                  <div className="flex justify-center text-red-500">
                    <ArrowDown className="w-3 h-3" />
                  </div>
                </div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-slate-500 font-semibold">Risk Score</span>
                  <span className="font-mono">{hoveredNodeData.stats.riskScore}/10</span>
                  <div className="flex justify-center text-orange-500">
                    <AlertTriangle className="w-3 h-3" />
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

"use client";
import { useRef, useEffect, useState } from"react";
import { Network, Info, AlertTriangle, ArrowUp, ArrowDown } from"lucide-react";
import { Tooltip } from"@/components/ui/Tooltip";
import { motion, AnimatePresence } from"framer-motion";

interface NodeStats {
 type: string;
 totalTxns: number;
 blockedTxns: number;
 riskScore: number;
}

interface GraphNode {
 id: string;
 type:"victim" |"mule" |"merchant" |"synthetic" |"agent" |"account";
 x: number;
 y: number;
 stats: NodeStats;
}

interface GraphEdge {
 source: string;
 target: string;
 isFraud: boolean;
 isFeedback?: boolean;
}

export default function BattlefieldGraph({ liveData }: { liveData?: any }) {
 const canvasRef = useRef<HTMLCanvasElement>(null);
 const [hoveredNode, setHoveredNode] = useState<string | null>(null);
 const [clickedNode, setClickedNode] = useState<string | null>(null);



 // Track physics state across renders
 const physicsNodes = useRef<Map<string, GraphNode & { vx: number; vy: number }>>(new Map());

 // Ingest real transactions from backend
 useEffect(() => {
 if (!liveData?.transaction_graph) return;
 
 const { nodes: incomingNodes } = liveData.transaction_graph;
 const incomingSet = new Set(incomingNodes.map((n: any) => n.id));
 
 // Add new nodes
 incomingNodes.forEach((n: any) => {
 if (!physicsNodes.current.has(n.id)) {
 // Zone-based initial placement: accounts LEFT, merchants CENTER, mules RIGHT
 let startX = 400;
 if (n.type ==="account" || n.type ==="victim") startX = 150 + Math.random() * 100;
 else if (n.type ==="merchant") startX = 350 + Math.random() * 100;
 else startX = 550 + Math.random() * 100; // mule, synthetic, agent

 physicsNodes.current.set(n.id, {
 id: n.id,
 type: n.type,
 x: startX,
 y: 100 + Math.random() * 200,
 vx: 0,
 vy: 0,
 stats: {
 type: n.type.charAt(0).toUpperCase() + n.type.slice(1),
 totalTxns: n.txn_count || 1,
 blockedTxns: n.blocked_count || 0,
 riskScore: Math.round((n.risk || 0) * 100),
 }
 });
 } else {
 // Update existing node stats with latest real data from backend
 const existing = physicsNodes.current.get(n.id)!;
 existing.stats.totalTxns = n.txn_count || existing.stats.totalTxns;
 existing.stats.blockedTxns = n.blocked_count || existing.stats.blockedTxns;
 existing.stats.riskScore = Math.round((n.risk || 0) * 100);
 }
 });

 // Remove old nodes to prevent clutter
 for (const key of physicsNodes.current.keys()) {
 if (!incomingSet.has(key)) {
 physicsNodes.current.delete(key);
 }
 }
 }, [liveData?.transaction_graph]);

 // Canvas Animation & Physics Render Loop
 useEffect(() => {
 const canvas = canvasRef.current;
 if (!canvas) return;
 const ctx = canvas.getContext("2d");
 if (!ctx) return;

 const w = canvas.width = canvas.offsetWidth;
 const h = canvas.height = canvas.offsetHeight;
 const scaleX = w / 800;
 const scaleY = h / 400;

 let frame: number;
 let t = 0;

 const draw = () => {
 ctx.clearRect(0, 0, w, h);

 const nodes = Array.from(physicsNodes.current.values());
 const edges = liveData?.transaction_graph?.edges || [];

 // PHYSICS ENGINE — higher repulsion + longer edges = more spacing
 const repel = 3000;
 const attract = 0.03;
 const friction = 0.82;
 const centerForce = 0.025;

 // 1. Repulsion between all nodes
 for (let i = 0; i < nodes.length; i++) {
 for (let j = i + 1; j < nodes.length; j++) {
 const n1 = nodes[i];
 const n2 = nodes[j];
 const dx = n2.x - n1.x;
 const dy = n2.y - n1.y;
 let dist = Math.sqrt(dx * dx + dy * dy) || 1;
 const f = repel / (dist * dist);
 n1.vx -= (dx / dist) * f;
 n1.vy -= (dy / dist) * f;
 n2.vx += (dx / dist) * f;
 n2.vy += (dy / dist) * f;
 }
 }

 // 2. Attraction along edges
 edges.forEach((e: any) => {
 const n1 = physicsNodes.current.get(e.source);
 const n2 = physicsNodes.current.get(e.target);
 if (!n1 || !n2) return;
 const dx = n2.x - n1.x;
 const dy = n2.y - n1.y;
 let dist = Math.sqrt(dx * dx + dy * dy) || 1;
 const diff = dist - 120; // Longer target edge length for spacing
 const f = diff * attract;
 n1.vx += (dx / dist) * f;
 n1.vy += (dy / dist) * f;
 n2.vx -= (dx / dist) * f;
 n2.vy -= (dy / dist) * f;
 });

 // 3. Update Positions & Apply ZONE-BASED Center Gravity
 // Accounts gravitate LEFT, merchants CENTER, mules/fraud RIGHT
 // This creates a natural left-to-right"money flow" narrative
 nodes.forEach((n) => {
 let targetX = 400; // default center
 if (n.type ==="account" || n.type ==="victim") targetX = 180;
 else if (n.type ==="merchant") targetX = 400;
 else targetX = 620; // mule, synthetic, agent

 n.vx += (targetX - n.x) * centerForce;
 n.vy += (200 - n.y) * centerForce;
 n.vx *= friction;
 n.vy *= friction;
 n.x += n.vx;
 n.y += n.vy;
 
 // Keep within bounds with generous margins
 n.x = Math.max(60, Math.min(740, n.x));
 n.y = Math.max(60, Math.min(340, n.y));
 });

 // Draw Edges
 edges.forEach((e: any) => {
 const src = physicsNodes.current.get(e.source);
 const tgt = physicsNodes.current.get(e.target);
 if (!src || !tgt) return;

 const sx = src.x * scaleX;
 const sy = src.y * scaleY;
 const tx = tgt.x * scaleX;
 const ty = tgt.y * scaleY;

 ctx.beginPath();
 if (e.isFeedback) {
 ctx.setLineDash([5, 5]);
 ctx.strokeStyle ="#f97316"; // Orange dashed for RL feedback loop
 ctx.lineWidth = 2;
 ctx.moveTo(sx, sy);
 ctx.quadraticCurveTo(sx + (tx - sx) / 2, sy - 80, tx, ty);
 ctx.stroke();
 ctx.setLineDash([]);
 
 ctx.fillStyle ="#f97316";
 ctx.font ="bold 10px sans-serif";
 ctx.fillText("RL Policy Blocked", sx + (tx - sx) / 2 - 40, sy - 45);
 } else {
 ctx.strokeStyle = e.isFraud ?"#fca5a5" :"#e2e8f0";
 ctx.lineWidth = 1.5;
 ctx.moveTo(sx, sy);
 ctx.lineTo(tx, ty);
 ctx.stroke();
 }

 // Animated particles traveling along the edge
 const progress = (t * (e.isFeedback ? 0.015 : 0.025)) % 1;
 let px, py;
 if (e.isFeedback) {
 const cx = sx + (tx - sx) / 2;
 const cy = sy - 80;
 px = (1 - progress) * (1 - progress) * sx + 2 * (1 - progress) * progress * cx + progress * progress * tx;
 py = (1 - progress) * (1 - progress) * sy + 2 * (1 - progress) * progress * cy + progress * progress * ty;
 } else {
 px = sx + (tx - sx) * progress;
 py = sy + (ty - sy) * progress;
 }

 ctx.beginPath();
 ctx.fillStyle = e.isFeedback ?"#f97316" : e.isFraud ?"#ef4444" :"#94a3b8";
 ctx.arc(px, py, 3, 0, Math.PI * 2);
 ctx.fill();
 });

 // Draw Nodes
 nodes.forEach((n) => {
 const nx = n.x * scaleX;
 const ny = n.y * scaleY;

 ctx.beginPath();
 // Clear color mapping per node type
 const color = n.type ==="account" ?"#e2e8f0" : n.type ==="victim" ?"#e2e8f0" : n.type ==="mule" ?"#fca5a5" : n.type ==="synthetic" ?"#f87171" : n.type ==="merchant" ?"#93c5fd" : n.type ==="agent" ?"#a78bfa" :"#60a5fa";
 const border = n.type ==="account" ?"#94a3b8" : n.type ==="victim" ?"#94a3b8" : n.type ==="mule" ?"#ef4444" : n.type ==="synthetic" ?"#dc2626" : n.type ==="merchant" ?"#3b82f6" : n.type ==="agent" ?"#7c3aed" :"#3b82f6";
 const radius = n.type ==="mule" || n.type ==="merchant" || n.type ==="agent" ? 14 : 10;

 if (hoveredNode === n.id) {
 ctx.beginPath();
 ctx.strokeStyle ="#f97316";
 ctx.lineWidth = 3;
 ctx.arc(nx, ny, radius + 6, 0, Math.PI * 2);
 ctx.stroke();
 }

 ctx.beginPath();
 ctx.fillStyle = color;
 ctx.strokeStyle = border;
 ctx.lineWidth = 1.5;
 ctx.arc(nx, ny, radius, 0, Math.PI * 2);
 ctx.fill();
 ctx.stroke();

 // Draw blocked indicator for nodes Blue Team has flagged
 if (n.stats.blockedTxns > 0) {
   // Pulsing red ring
   const pulse = 0.5 + Math.sin(t * 0.08) * 0.3;
   ctx.globalAlpha = pulse;
   ctx.beginPath();
   ctx.strokeStyle = "#dc2626";
   ctx.lineWidth = 3;
   ctx.setLineDash([4, 4]);
   ctx.arc(nx, ny, radius + 8, 0, Math.PI * 2);
   ctx.stroke();
   ctx.setLineDash([]);
   ctx.globalAlpha = 1;

   // Red X through the node
   const xSize = radius * 0.5;
   ctx.beginPath();
   ctx.strokeStyle = "#dc2626";
   ctx.lineWidth = 2.5;
   ctx.moveTo(nx - xSize, ny - xSize);
   ctx.lineTo(nx + xSize, ny + xSize);
   ctx.moveTo(nx + xSize, ny - xSize);
   ctx.lineTo(nx - xSize, ny + xSize);
   ctx.stroke();

   // Red "BLOCKED" badge above node
   const badgeText = `BLOCKED`;
   ctx.font = "bold 8px sans-serif";
   const textW = ctx.measureText(badgeText).width;
   const bx = nx - textW / 2 - 4;
   const by = ny - radius - 18;
   ctx.fillStyle = "#dc2626";
   ctx.beginPath();
   ctx.roundRect(bx, by, textW + 8, 14, 2);
   ctx.fill();
   ctx.fillStyle = "#ffffff";
   ctx.fillText(badgeText, bx + 4, by + 10);

   // Dim the node itself
   ctx.globalAlpha = 0.4;
 }

 if (hoveredNode === n.id || n.type ==="merchant" || n.type ==="mule" || n.type ==="agent") {
 ctx.fillStyle ="#475569";
 ctx.font ="10px monospace";
 ctx.fillText(n.id, nx + radius + (hoveredNode === n.id ? 10 : 6), ny + 4);
 }
 ctx.globalAlpha = 1;
 });

 t++;
 frame = requestAnimationFrame(draw);
 };

 draw();
 return () => cancelAnimationFrame(frame);
 }, [liveData?.transaction_graph, hoveredNode]);

 const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
 const canvas = canvasRef.current;
 if (!canvas) return;
 const rect = canvas.getBoundingClientRect();
 const x = e.clientX - rect.left;
 const y = e.clientY - rect.top;

 const scaleX = canvas.width / 800;
 const scaleY = canvas.height / 400;

 const nodes = Array.from(physicsNodes.current.values());
 let found: string | null = null;
 
 for (let i = nodes.length - 1; i >= 0; i--) {
 const n = nodes[i];
 const nx = n.x * scaleX;
 const ny = n.y * scaleY;
 const radius = n.type ==="mule" || n.type ==="merchant" || n.type ==="agent" ? 14 : 10;
 
 const dx = x - nx;
 const dy = y - ny;
 if (dx * dx + dy * dy <= (radius + 6) * (radius + 6)) {
 found = n.id;
 break;
 }
 }
 
 if (found !== hoveredNode) {
 setHoveredNode(found);
 }
 };

 const hoveredNodeData = hoveredNode ? physicsNodes.current.get(hoveredNode) : null;
 const clickedNodeData = clickedNode ? physicsNodes.current.get(clickedNode) : null;
 const displayNodeData = clickedNodeData || hoveredNodeData;

 return (
 <div className="bg-white border border-slate-200 shadow-sm h-full flex flex-col overflow-visible">
 <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-200 shrink-0 bg-white">
 
 <h2 className="text-sm font-semibold text-slate-800 uppercase tracking-wider">
 Transaction Network
 </h2>
 <Tooltip content="Live topology mapping tracking multi-agent adversarial feedback loops. Nodes represent actors (accounts, merchants, mules), and edges represent financial transactions. Anomalies and RL policy interventions are highlighted in real-time.">
 <Info className="w-4 h-4 text-slate-400 ml-1 hover:text-slate-600 transition-colors cursor-pointer" />
 </Tooltip>
 <div className="ml-auto flex items-center gap-4 text-[10px] text-slate-600">
 <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-slate-200 border border-slate-300" /> Account</span>
 <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-300 border border-blue-500" /> Merchant</span>
 <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-red-300 border border-red-500" /> Mule</span>
 </div>
 </div>

 <div className="flex-1 relative bg-[#fafafa]">
        {/* Phase Narrator — explains what's happening in plain English */}
        {liveData?.battle_phase && liveData.battle_phase !== "IDLE" && (
          <div className={`absolute top-3 left-3 right-3 z-10 flex flex-col gap-1.5 px-3 py-2.5 shadow-sm border ${
            liveData.battle_phase === "RECON" ? "bg-yellow-50 border-yellow-200" :
            liveData.battle_phase === "DETECTION" ? "bg-orange-50 border-orange-200" :
            liveData.battle_phase === "CONTAINMENT" ? "bg-blue-50 border-blue-200" :
            liveData.battle_phase === "MUTATION" ? "bg-red-50 border-red-200" :
            "bg-purple-50 border-purple-200"
          }`}>
            <div className="flex items-center justify-between">
              <div className={`flex items-center gap-2 text-xs font-bold ${
                liveData.battle_phase === "RECON" ? "text-yellow-700" :
                liveData.battle_phase === "DETECTION" ? "text-orange-700" :
                liveData.battle_phase === "CONTAINMENT" ? "text-blue-700" :
                liveData.battle_phase === "MUTATION" ? "text-red-700" :
                "text-purple-700"
              }`}>
                <AlertTriangle className="w-3.5 h-3.5" />
                {liveData.battle_phase} — Tick {liveData.battle_tick || 0}
              </div>
              {/* Red vs Blue mini bar */}
              <div className="flex items-center gap-2 text-[9px] font-mono">
                <span className="text-red-600">Red {Math.round((liveData.red_team_success_rate || 0) * 100)}%</span>
                <div className="w-16 h-1.5 bg-blue-200 rounded-full overflow-hidden">
                  <div className="h-full bg-red-500 rounded-full transition-all" style={{ width: `${(liveData.red_team_success_rate || 0) * 100}%` }} />
                </div>
                <span className="text-blue-600">Blue {Math.round((1 - (liveData.red_team_success_rate || 0)) * 100)}%</span>
              </div>
            </div>
            <div className="text-[10px] text-slate-600 leading-relaxed">
              {liveData.battle_phase === "RECON" && "Red Team is quietly injecting fraud probes into normal traffic. Blue Team hasn't detected anything yet — these early transactions build the baseline."}
              {liveData.battle_phase === "DETECTION" && (
                liveData.detected_attack_type
                  ? `Blue Team identified suspicious patterns → classified as ${liveData.detected_attack_type.replace(/_/g, " ").toUpperCase()} with ${Math.round((liveData.detection_confidence || 0) * 100)}% confidence. Flagging anomalous nodes...`
                  : `Blue Team analyzing anomalies across ${Math.round((liveData.blue_team_sensitivity || 0) * 100)}% of signal space. Narrowing down attack type...`
              )}
              {liveData.battle_phase === "CONTAINMENT" && `Blue Team is actively blocking fraud transactions. Red Team success dropping to ${Math.round((liveData.red_team_success_rate || 0) * 100)}%. Watch mule nodes get flagged with red "BLOCKED" badges.`}
              {liveData.battle_phase === "MUTATION" && `Red Team deploying Gen-${liveData.mutation_generation || 0} mutations via RL policy — altering amounts, timing, and routes to bypass Blue's defenses.`}
              {liveData.battle_phase === "ADAPTATION" && `Blue Team learning Red's mutation tactics and tightening detection thresholds. This arms race continues...`}
            </div>
          </div>
        )}

 <canvas 
 ref={canvasRef} 
 className="w-full h-full cursor-pointer" 
 onMouseMove={handleMouseMove}
 onMouseLeave={() => setHoveredNode(null)}
 onClick={() => setClickedNode(hoveredNode === clickedNode ? null : hoveredNode)}
 />

 <AnimatePresence>
 {displayNodeData && (
 <motion.div
 initial={{ opacity: 0, y: 10, scale: 0.95 }}
 animate={{ opacity: 1, y: 0, scale: 1 }}
 exit={{ opacity: 0, scale: 0.95 }}
 transition={{ duration: 0.15 }}
 className="absolute bg-white border border-slate-200 shadow-xl p-3 w-64 z-[9999]"
 style={{
 left: `calc(${(displayNodeData.x / 800) * 100}% + 20px)`,
 top: `calc(${(displayNodeData.y / 400) * 100}% - 70px)`,
 pointerEvents: clickedNodeData ?"auto" :"none"
 }}
 >
 <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-2">
 <span className="text-xs font-semibold text-slate-800">Node ID: {displayNodeData.id}</span>
 {clickedNodeData && (
 <button onClick={() => setClickedNode(null)} className="text-slate-400 hover:text-slate-600">
 &times;
 </button>
 )}
 </div>
 <div className="text-[11px] text-slate-600 mb-3">
 Classification: <span className="font-semibold text-slate-800 uppercase tracking-wider">{displayNodeData.stats.type}</span>
 </div>
 
 <div className="grid grid-cols-3 gap-2 text-center text-[10px] p-2 bg-slate-50">
 <div className="flex flex-col gap-0.5">
 <span className="text-slate-500 font-semibold">Total Txns</span>
 <span className="font-mono text-slate-900">{displayNodeData.stats.totalTxns}</span>
 <div className="flex justify-center text-blue-500">
 <ArrowUp className="w-3 h-3" />
 </div>
 </div>
 <div className="flex flex-col gap-0.5">
 <span className="text-slate-500 font-semibold">Blocked</span>
 <span className="font-mono text-slate-900">{displayNodeData.stats.blockedTxns}</span>
 <div className="flex justify-center text-red-500">
 <ArrowDown className="w-3 h-3" />
 </div>
 </div>
 <div className="flex flex-col gap-0.5">
 <span className="text-slate-500 font-semibold">Risk Score</span>
 <span className="font-mono text-orange-600 font-bold">{displayNodeData.stats.riskScore}%</span>
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

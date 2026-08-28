"use client";
import { useState, useEffect } from"react";
import { Bot, ShieldCheck, ShieldX } from"lucide-react";
import { motion, AnimatePresence } from"framer-motion";

const DEMO_EVENTS: any[] = [];

export default function KYAMonitor({ liveData }: { liveData?: any }) {
 const [events, setEvents] = useState<any[]>(DEMO_EVENTS);

 useEffect(() => {
 if (liveData?.kya_event) {
 setEvents((prev) => {
 if (prev.length > 0 && prev[0].id === liveData.kya_event.id) {
 return prev;
 }
 return [liveData.kya_event, ...prev].slice(0, 20);
 });
 }
 }, [liveData]);

 return (
 <div className="flex flex-col h-full min-h-0">
 <div className="flex items-center gap-2 mb-2 shrink-0">
 
 <p className="text-[10px] text-slate-800 uppercase tracking-wider font-bold">Know Your Agent (AP4M)</p>
 </div>
 <div className="flex-1 overflow-y-auto pr-1 min-h-0">
 <div className="grid grid-cols-2 gap-2">
 <AnimatePresence>
 {events.map((evt, i) => (
 <motion.div
 key={evt.id +"-" + i}
 initial={{ opacity: 0, y: 5 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ delay: i * 0.05 }}
 className={`p-2 border text-[11px] shadow-sm ${
 evt.status ==="blocked"
 ?"border-red-200 bg-red-50"
 :"border-green-200 bg-green-50"
 }`}
 >
 <div className="flex items-center justify-between">
 <span className="font-mono font-bold text-slate-700 truncate">{evt.agent}</span>
 {evt.status ==="blocked" ? (
 <ShieldX className="w-3.5 h-3.5 text-red-600 shrink-0 ml-1" />
 ) : (
 <ShieldCheck className="w-3.5 h-3.5 text-green-600 shrink-0 ml-1" />
 )}
 </div>
 <p className="text-slate-700 mt-1 leading-tight line-clamp-2">{evt.action}</p>
 <p className="text-[9px] text-slate-500 mt-1 italic line-clamp-1">{evt.reason}</p>
 </motion.div>
 ))}
 </AnimatePresence>
 </div>
 </div>
 </div>
 );
}

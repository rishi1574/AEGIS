"use client";
import { useState, useEffect } from"react";
import { Smartphone, Tablet, Monitor, X, Check, Copy, CheckCircle2 } from "lucide-react";
import { useWebSocket } from"@/hooks/useWebSocket";
import { useApi } from"@/hooks/useApi";
import Header from"@/components/war-room/Header";
import RedTeamConsole from"@/components/war-room/RedTeamConsole";
import BattlefieldGraph from"@/components/war-room/BattlefieldGraph";
import BlueTeamConsole from"@/components/war-room/BlueTeamConsole";
import ConceptDriftChart from"@/components/war-room/ConceptDriftChart";
import FederatedComparison from"@/components/war-room/FederatedComparison";
import StatsBar from"@/components/war-room/StatsBar";
import SystemHardnessDial from"@/components/war-room/SystemHardnessDial";
import ShapWaterfall from"@/components/war-room/ShapWaterfall";
import ThreatIntelFeed from"@/components/war-room/ThreatIntelFeed";
import KYAMonitor from"@/components/war-room/KYAMonitor";
import AttackGenealogyTree from"@/components/war-room/AttackGenealogyTree";
import SimulationTour from"@/components/war-room/SimulationTour";
import AdversarialInstanceView from"@/components/war-room/AdversarialInstanceView";

export default function WarRoom() {
 const { connected, lastMessage, messages, send } = useWebSocket();
 const { get, post } = useApi();
 const [metrics, setMetrics] = useState<any>(null);
 const [attacks, setAttacks] = useState<any[]>([]);
 const [federated, setFederated] = useState<any>(null);
 const [hardness, setHardness] = useState<any>(null);
 const [interceptions, setInterceptions] = useState<any[]>([]);
 const [shapData, setShapData] = useState<any>(null);
 const [activeAttack, setActiveAttack] = useState<string | null>(null);
 const [copied, setCopied] = useState(false);

 const handleCopy = () => {
   navigator.clipboard.writeText("https://aegis-swarup.vercel.app/simulator");
   setCopied(true);
   setTimeout(() => setCopied(false), 2000);
 };

 useEffect(() => {
 // Load initial data
 get("/api/blue-team/metrics").then(setMetrics);
 get("/api/red-team/attacks").then((d) => setAttacks(d?.attacks || []));
 get("/api/blue-team/federated-comparison").then(setFederated);
 get("/api/simulation/system-hardness").then(setHardness);
 get("/api/blue-team/interception-log").then((d) => setInterceptions(d?.interceptions || []));
 get("/api/blue-team/shap-explanations").then((d) => setShapData(d?.explanations?.[0] || null));

 // Poll federated endpoint for live animation (slower to avoid excessive round increments)
 const fedInterval = setInterval(() => {
 get("/api/blue-team/federated-comparison").then(setFederated);
 }, 10000);

 return () => clearInterval(fedInterval);
 }, [get]);

 // Update hardness and SHAP from live telemetry
 useEffect(() => {
 if (lastMessage?.data?.system_hardness) {
 setHardness((prev: any) => ({
 ...prev,
 score: lastMessage.data.system_hardness,
 }));
 }
 if (lastMessage?.data?.shap_explanation) {
 setShapData(lastMessage.data.shap_explanation);
 }
 }, [lastMessage]);

 const launchAttack = async (attackType: string) => {
 setActiveAttack(attackType);
 const result = await post("/api/red-team/launch", { attack_type: attackType });
 send({ type:"launch_attack", attack_type: attackType });
 return result;
 };

 return (
 <>
   {/* Mobile Not Supported Overlay */}
   <div className="md:hidden fixed inset-0 z-[9999] flex items-center justify-center bg-black/20 backdrop-blur-md p-4">
     <div className="bg-white shadow-2xl border border-slate-200 p-8 max-w-md w-full mx-auto text-center flex flex-col items-center rounded-xl">
       <h3 className="text-2xl font-bold text-slate-800 mb-3">Larger Screen Needed</h3>
       <p className="text-sm text-slate-600 mb-8 leading-relaxed">
         Welcome to the AEGIS Simulator! Our live adversarial war room features complex, real-time data visualizations that need a bit more space to shine.
       </p>
       
       <div className="flex items-center justify-center gap-8 mb-8 w-full px-2">
         {/* Phone - Not Supported */}
         <div className="flex flex-col items-center gap-3 opacity-40 grayscale">
           <div className="relative">
             <Smartphone className="w-12 h-12 text-slate-500" strokeWidth={1.5} />
             <div className="absolute -bottom-1 -right-1 bg-white rounded-full">
               <X className="w-5 h-5 text-red-500" strokeWidth={3} />
             </div>
           </div>
           <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Phone</span>
         </div>
         
         <div className="w-px h-16 bg-slate-200"></div>

         {/* Tablet/Desktop - Supported */}
         <div className="flex flex-col items-center gap-3">
           <div className="relative flex items-center gap-3 bg-blue-50/50 p-2 rounded-lg border border-blue-100/50">
             <Tablet className="w-10 h-10 text-blue-600" strokeWidth={1.5} />
             <Monitor className="w-12 h-12 text-blue-600" strokeWidth={1.5} />
             <div className="absolute -bottom-2 -right-2 bg-white rounded-full shadow-sm">
               <Check className="w-6 h-6 text-green-500" strokeWidth={3} />
             </div>
           </div>
           <span className="text-xs font-bold text-blue-900 uppercase tracking-wide">Tablet & Desktop</span>
         </div>
       </div>

       <div className="w-full p-4 bg-blue-50/80 border border-blue-100 rounded-lg text-sm text-blue-900 font-medium flex flex-col items-center gap-3">
         <p>Please open this link on a tablet, laptop, or desktop computer to explore the war room.</p>
         
         <div className="flex items-center gap-2 w-full mt-1">
           <div className="flex-1 bg-white border border-blue-200 rounded-md px-3 py-2 text-xs text-slate-600 font-mono truncate text-left overflow-hidden">
             https://aegis-swarup.vercel.app/simulator
           </div>
           <button 
             onClick={handleCopy}
             className="flex items-center justify-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md font-semibold text-xs transition-colors shrink-0 min-w-[90px]"
           >
             {copied ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
             {copied ? "Copied!" : "Copy"}
           </button>
         </div>
       </div>
     </div>
   </div>

   <div className="hidden md:flex h-screen bg-aegis-bg grid-bg flex-col overflow-hidden">
     <Header connected={connected} />

     {/* Main Content Area */}
     <div className="flex-1 min-h-0 flex flex-col gap-3 p-3 overflow-y-auto">
       {/* Main 3-Column Layout */}
       <div className="grid grid-cols-12 gap-3 min-h-[750px] flex-1">
         {/* Left: Red Team */}
         <div className="col-span-3 flex flex-col gap-3 min-h-0 tour-red-team">
           <div className="flex-1 min-h-0">
             <RedTeamConsole attacks={attacks} onLaunch={launchAttack} liveData={lastMessage?.data} />
           </div>
         </div>

         {/* Center: Battlefield + Instance View + System Hardness */}
         <div className="col-span-6 flex flex-col gap-3 min-h-0 tour-transaction-network">
           <div className="flex-1 min-h-0">
             <BattlefieldGraph liveData={lastMessage?.data} />
           </div>
           
           {/* Adversarial Instance View (Decision Boundary) */}
           <div className="shrink-0 h-[180px]">
             <AdversarialInstanceView liveData={lastMessage?.data} />
           </div>

           {/* System Hardness + SHAP inline */}
           <div className="grid grid-cols-2 gap-3 shrink-0 h-[140px]">
             <div className="bg-white border border-slate-200 shadow-sm flex flex-col items-center justify-center p-3">
               <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1 font-semibold">System Hardness</p>
               <SystemHardnessDial score={hardness?.score || Math.round((lastMessage?.data?.system_hardness) || 68)} />
             </div>
             <div className="bg-white border border-slate-200 shadow-sm p-3 overflow-hidden">
               <ShapWaterfall
                 shapValues={shapData?.features?.reduce((acc: any, f: any) => {
                   acc[f.description || f.feature] = f.shap_value;
                   return acc;
                 }, {}) || null}
                 transactionId={shapData?.transaction_id}
               />
             </div>
           </div>
         </div>

         {/* Right: Blue Team */}
         <div className="col-span-3 flex flex-col gap-3 min-h-0 tour-blue-team">
           <div className="flex-1 min-h-0">
             <BlueTeamConsole metrics={metrics} liveData={lastMessage?.data} />
           </div>
         </div>
       </div>

       {/* Bottom Row: Charts + Intel */}
       <div className="grid grid-cols-12 gap-3 shrink-0 min-h-[260px] pb-6 mt-6">
         <div className="col-span-4 h-full max-h-[340px]">
           <ConceptDriftChart liveData={lastMessage?.data} />
         </div>
         <div className="col-span-3 tour-federated h-full max-h-[340px]">
           <FederatedComparison data={federated} />
         </div>
         <div className="col-span-2 h-full max-h-[340px]">
           <div className="bg-white border border-slate-200 shadow-sm h-full p-3 overflow-y-auto">
             <ThreatIntelFeed liveData={lastMessage?.data} />
           </div>
         </div>
         <div className="col-span-3 h-full max-h-[340px]">
           <div className="bg-white border border-slate-200 shadow-sm h-full p-3 overflow-y-auto">
             <KYAMonitor liveData={lastMessage?.data} />
           </div>
         </div>
       </div>
     </div>

     {/* Stats Footer */}
     <StatsBar metrics={metrics} connected={connected} liveData={lastMessage?.data} />
     
     {/* Simulation Tour */}
     <SimulationTour />
   </div>
 </>
 );
}

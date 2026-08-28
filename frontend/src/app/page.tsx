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
import SystemHardnessDial from "@/components/war-room/SystemHardnessDial";
import ShapWaterfall from "@/components/war-room/ShapWaterfall";
import ThreatIntelFeed from "@/components/war-room/ThreatIntelFeed";
import KYAMonitor from "@/components/war-room/KYAMonitor";
import AttackGenealogyTree from "@/components/war-room/AttackGenealogyTree";
import SimulationTour from "@/components/war-room/SimulationTour";
import AdversarialInstanceView from "@/components/war-room/AdversarialInstanceView";

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

  useEffect(() => {
    // Load initial data
    get("/api/blue-team/metrics").then(setMetrics);
    get("/api/red-team/attacks").then((d) => setAttacks(d?.attacks || []));
    get("/api/blue-team/federated-comparison").then(setFederated);
    get("/api/simulation/system-hardness").then(setHardness);
    get("/api/blue-team/interception-log").then((d) => setInterceptions(d?.interceptions || []));
    get("/api/blue-team/shap-explanations").then((d) => setShapData(d?.explanations?.[0] || null));

    // Poll federated endpoint for live animation
    const fedInterval = setInterval(() => {
      get("/api/blue-team/federated-comparison").then(setFederated);
    }, 3000);

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
    send({ type: "launch_attack", attack_type: attackType });
    return result;
  };

  return (
    <div className="h-screen bg-aegis-bg grid-bg flex flex-col overflow-hidden">
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
              <div className="bg-white border border-slate-200 shadow-sm rounded-xl flex flex-col items-center justify-center p-3">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1 font-semibold">System Hardness</p>
                <SystemHardnessDial score={hardness?.score || Math.round((lastMessage?.data?.system_hardness) || 68)} />
              </div>
              <div className="bg-white border border-slate-200 shadow-sm rounded-xl p-3 overflow-hidden">
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
            <div className="bg-white border border-slate-200 shadow-sm rounded-xl h-full p-3 overflow-y-auto">
              <ThreatIntelFeed liveData={lastMessage?.data} />
            </div>
          </div>
          <div className="col-span-3 h-full max-h-[340px]">
            <div className="bg-white border border-slate-200 shadow-sm rounded-xl h-full p-3 overflow-y-auto">
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
  );
}

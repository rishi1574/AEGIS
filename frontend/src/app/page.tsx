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

  // Update hardness from live telemetry
  useEffect(() => {
    if (lastMessage?.data?.system_hardness) {
      setHardness((prev: any) => ({
        ...prev,
        score: lastMessage.data.system_hardness,
      }));
    }
  }, [lastMessage]);

  const launchAttack = async (attackType: string) => {
    setActiveAttack(attackType);
    const result = await post("/api/red-team/launch", { attack_type: attackType });
    send({ type: "launch_attack", attack_type: attackType });
    return result;
  };

  return (
    <div className="min-h-screen bg-aegis-bg grid-bg">
      <Header connected={connected} />

      {/* Main 3-Column Layout */}
      <div className="grid grid-cols-12 gap-3 p-3" style={{ height: "max(650px, calc(100vh - 120px))" }}>
        {/* Left: Red Team */}
        <div className="col-span-3 flex flex-col gap-3 min-h-0 tour-red-team">
          <div className="flex-1 min-h-0">
            <RedTeamConsole attacks={attacks} onLaunch={launchAttack} liveData={lastMessage?.data} />
          </div>
        </div>

        {/* Center: Battlefield + System Hardness */}
        <div className="col-span-5 flex flex-col gap-3 min-h-0 tour-transaction-network">
          <div className="flex-1 min-h-0">
            <BattlefieldGraph liveData={lastMessage?.data} />
          </div>
          {/* System Hardness + SHAP inline */}
          <div className="grid grid-cols-2 gap-3 shrink-0" style={{ height: "140px" }}>
            <div className="glass-card flex flex-col items-center justify-center p-3">
              <p className="text-[10px] text-aegis-text-muted uppercase tracking-wider mb-1">System Hardness</p>
              <SystemHardnessDial score={hardness?.score || Math.round((lastMessage?.data?.system_hardness) || 68)} />
            </div>
            <div className="glass-card p-3 overflow-hidden">
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
        <div className="col-span-4 flex flex-col gap-3 min-h-0 tour-blue-team">
          <div className="flex-1 min-h-0">
            <BlueTeamConsole metrics={metrics} liveData={lastMessage?.data} />
          </div>
        </div>
      </div>

      {/* Bottom Row: Charts + Intel */}
      <div className="grid grid-cols-12 gap-3 px-3 pb-16" style={{ height: "240px" }}>
        <div className="col-span-4">
          <ConceptDriftChart liveData={lastMessage?.data} />
        </div>
        <div className="col-span-3 tour-federated">
          <FederatedComparison data={federated} />
        </div>
        <div className="col-span-2">
          <div className="glass-card h-full p-3 overflow-y-auto">
            <ThreatIntelFeed />
          </div>
        </div>
        <div className="col-span-3">
          <div className="glass-card h-full p-3 overflow-y-auto">
            <KYAMonitor />
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

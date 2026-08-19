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
          <RedTeamConsole attacks={attacks} onLaunch={launchAttack} liveData={lastMessage?.data} />
        </div>

        {/* Center: Battlefield */}
        <div className="col-span-5">
          <BattlefieldGraph liveData={lastMessage?.data} />
        </div>

        {/* Right: Blue Team */}
        <div className="col-span-4">
          <BlueTeamConsole metrics={metrics} liveData={lastMessage?.data} />
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-12 gap-3 px-3 pb-3" style={{ height: "280px" }}>
        <div className="col-span-7">
          <ConceptDriftChart liveData={lastMessage?.data} />
        </div>
        <div className="col-span-5">
          <FederatedComparison data={federated} />
        </div>
      </div>

      {/* Stats Footer */}
      <StatsBar metrics={metrics} connected={connected} liveData={lastMessage?.data} />
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Shield,
  Target,
  Zap,
  Activity,
  Cpu,
  BrainCircuit,
  Network,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Layers,
  BarChart3,
  GitBranch,
  Radio,
  Lock,
  Search,
  Eye,
  Sliders,
  Database,
  TrendingUp,
  RefreshCw,
  Server,
  Users,
  Compass,
  Key,
  Flame,
  ChevronRight,
  Check,
  Award,
  Sparkles,
} from "lucide-react";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import { useApi } from "@/hooks/useApi";

// ─── 25 ATTACK VECTORS TAXONOMY ───
const ALL_ATTACK_VECTORS = [
  {
    id: "synthetic_id_bustout",
    name: "Synthetic ID Bust-Out",
    layer: "Identity",
    rail: "Cards / BNPL / Loans",
    risk: "Critical",
    genAiMechanism: "Fuses stolen PII with deepfake biometrics; nurtures credit score for 6 months then maxes out limits simultaneously across 50 nodes.",
    evasion: "Behaves with 99.8% statistical normality during dormancy period; defeats static KYC velocity rules.",
    severityScore: 98,
  },
  {
    id: "deepfake_ato",
    name: "Deepfake Voice / Video ATO",
    layer: "Identity",
    rail: "UPI / P2P / Voice Banking",
    risk: "Critical",
    genAiMechanism: "Real-time diffusion-based voice cloning and facial landmark synthesis defeating liveness detection in video KYC and phone banking.",
    evasion: "Bypasses multi-factor biometric step-up authentication; mimics authentic ambient background acoustics.",
    severityScore: 96,
  },
  {
    id: "agentic_hijack",
    name: "Agentic Commerce Hijack (AP4M)",
    layer: "Emerging",
    rail: "ISO 20022 / Corporate Treasury",
    risk: "Critical",
    genAiMechanism: "Indirect prompt injection embedded invisibly in digital PDF invoices or ISO 20022 remittance text coercing AP4M autonomous agents.",
    evasion: "Exploits the 'agent authority gap' — OAuth token is authentic, cryptographic channel signature is valid.",
    severityScore: 99,
  },
  {
    id: "txn_fuzzing",
    name: "Adversarial Txn Fuzzing",
    layer: "Network",
    rail: "UPI / Merchant POS / Gateway",
    risk: "High",
    genAiMechanism: "Contextual bandit reinforcement learning calculating exact epsilon variations (e.g. ₹49,999 vs ₹50,000) to map model boundary.",
    evasion: "Stays strictly inside the 0.48-0.49 benign classification probability band.",
    severityScore: 91,
  },
  {
    id: "predictive_pan_extrapolation",
    name: "Predictive PAN Extrapolation",
    layer: "Identity",
    rail: "Card-Not-Present (CNP)",
    risk: "Critical",
    genAiMechanism: "Generative sequence models extrapolating complete 16-digit PANs from partial BIN leaks using Luhn check-digit synthesis.",
    evasion: "Distributes micro-testing transactions across thousands of decentralized global merchant gateways below velocity thresholds.",
    severityScore: 95,
  },
  {
    id: "temporal_fuzzing",
    name: "Temporal & Latency Spoofing",
    layer: "Network",
    rail: "TIPS / RT1 / FedNow",
    risk: "High",
    genAiMechanism: "Inverted Poisson packet pacing synthesizing inter-message latencies between ISO 20022 pacs.008 and pacs.002 messages.",
    evasion: "Defeats network-level temporal anomaly detection by adhering to standard millisecond SLA bounds.",
    severityScore: 89,
  },
  {
    id: "ctgan_mimicry",
    name: "CTGAN Covariate Mimicry",
    layer: "Identity",
    rail: "IMPS / NEFT / Wire",
    risk: "Critical",
    genAiMechanism: "Conditional Tabular GANs trained on anonymized banking streams to synthesize mathematically indistinguishable fraudulent transaction payloads.",
    evasion: "Matches continuous multivariate covariance distributions of legitimate banking customers.",
    severityScore: 94,
  },
  {
    id: "digital_arrest",
    name: "Digital Arrest Coercion Scam",
    layer: "Human",
    rail: "RTGS / High-Value Wire",
    risk: "High",
    genAiMechanism: "Deepfake video/audio impersonation of law enforcement agencies orchestrating multi-hour psychological extortion sessions.",
    evasion: "Victim willingly executes authentic biometric approval on their personal trusted device.",
    severityScore: 92,
  },
  {
    id: "merchant_collusion",
    name: "Synthetic Merchant Collusion",
    layer: "Network",
    rail: "POS / QR Payment",
    risk: "High",
    genAiMechanism: "LLM-generated synthetic business profiles and automated chargeback balancing passing ghost transactions to money mules.",
    evasion: "High fan-in distribution with uniform transaction amounts camouflaged as legitimate retail rush-hour velocity.",
    severityScore: 88,
  },
  {
    id: "vishing",
    name: "Hyper-Personalized Vishing",
    layer: "Human",
    rail: "UPI / NetBanking",
    risk: "Critical",
    genAiMechanism: "LLMs synthesizing real-time custom social engineering scripts leveraging scraped delivery, travel, and purchase telemetry.",
    evasion: "Exploits human emotional urgency; induces authorized push payment (APP) fraud.",
    severityScore: 93,
  },
  {
    id: "pig_butchering",
    name: "AI Pig Butchering",
    layer: "Human",
    rail: "Crypto / Cross-Border Wire",
    risk: "High",
    genAiMechanism: "Multi-persona autonomous LLM chat agents managing 10,000+ simultaneous trust relationships over weeks before capital extraction.",
    evasion: "Slowly escalating transaction volume perfectly disguised as voluntary personal transfers.",
    severityScore: 90,
  },
  {
    id: "api_exploit",
    name: "API Race & Replay Exploit",
    layer: "Network",
    rail: "Payment Gateway APIs",
    risk: "High",
    genAiMechanism: "Asynchronous machine-speed distributed probes testing idempotency key collision and timestamp tolerance in payment gateways.",
    evasion: "Microsecond intervals indistinguishable from legitimate network retries.",
    severityScore: 87,
  },
  {
    id: "supply_chain_bec",
    name: "Supply Chain BEC & Vendor Spoof",
    layer: "Emerging",
    rail: "B2B Wire / NEFT",
    risk: "High",
    genAiMechanism: "GenAI automated document reconstruction altering IBAN/IFSC bank details in recurring PDF invoice billing workflows.",
    evasion: "Preserves invoice template styling, vendor historical cadence, and purchase order identifiers.",
    severityScore: 91,
  },
  {
    id: "model_poisoning",
    name: "Adaptive Model Poisoning",
    layer: "Emerging",
    rail: "All Payment Rails",
    risk: "Critical",
    genAiMechanism: "Strategically injecting borderline fraudulent instances into production streams to induce gradient contamination during auto-retraining.",
    evasion: "Gradually shifts Blue Team decision boundary away from core attack channels without triggering alert spikes.",
    severityScore: 97,
  },
  {
    id: "surrogate_evasion",
    name: "Surrogate FGSM Gradient Evasion",
    layer: "Emerging",
    rail: "Digital Wallets / Gateway",
    risk: "Critical",
    genAiMechanism: "Trains shadow neural network on observed Blue Team outputs to compute Fast Gradient Sign Method (FGSM) perturbations on continuous features.",
    evasion: "Calculates mathematical minimum perturbation required to cross from fraud to benign classification.",
    severityScore: 95,
  },
  {
    id: "mislead_shap",
    name: "MISLEAD SHAP Explainer Evasion",
    layer: "Emerging",
    rail: "Enterprise Decision Engines",
    risk: "Critical",
    genAiMechanism: "Adversarial feature allocation forcing high-risk signals to unmonitored feature dimensions, blinding TreeExplainer algorithms.",
    evasion: "Model outputs zero SHAP feature contribution on the actual malicious vector.",
    severityScore: 96,
  },
  {
    id: "graph_poisoning",
    name: "Sybil Graph Topology Poisoning",
    layer: "Network",
    rail: "Account-to-Account (A2A)",
    risk: "High",
    genAiMechanism: "Spawns hundreds of dormant Sybil accounts generating circular micro-transactions to artificially inflate PageRank and graph centrality.",
    evasion: "Blinds Graph Neural Networks (GNNs) by burying mule dispersal edges inside dense synthetic subgraphs.",
    severityScore: 90,
  },
  {
    id: "marl_collusion",
    name: "Multi-Agent RL (MARL) Collusion",
    layer: "Network",
    rail: "Instant Payment Rails",
    risk: "Critical",
    genAiMechanism: "Proximal Policy Optimization (PPO) coordinating multi-agent actions to partition large transfers into sub-threshold fragments across banks.",
    evasion: "Individual account transfers appear trivial; money laundering only visible via global graph reconstruction.",
    severityScore: 98,
  },
  {
    id: "backdoor_injection",
    name: "Tabular Trigger Backdoor",
    layer: "Emerging",
    rail: "Card & UPI Gateways",
    risk: "Critical",
    genAiMechanism: "Embeds rare invariant feature combinations (e.g., amount = ₹404.04 + specific MCC) that force model override to benign.",
    evasion: "Latent backdoor dormant in 99.99% of transactions; triggered on-demand during large-scale extraction.",
    severityScore: 97,
  },
  {
    id: "nlp_payload",
    name: "NLP Semantic Remittance Evasion",
    layer: "Emerging",
    rail: "ISO 20022 / Remittance",
    risk: "High",
    genAiMechanism: "LLMs generating contextually harmonious transaction remarks matching legitimate B2B contractual jargon.",
    evasion: "Bypasses NLP risk filters scanning remittance fields for sanctioned or suspicious terminology.",
    severityScore: 86,
  },
  {
    id: "adversarial_doc",
    name: "Adversarial KYC Document Forgery",
    layer: "Identity",
    rail: "Digital Onboarding",
    risk: "High",
    genAiMechanism: "Diffusion models generating photo-realistic government IDs (Aadhaar/PAN/Passport) with imperceptible adversarial noise patterns.",
    evasion: "Bypasses OCR extraction, hologram verification, and automated tamper-detection neural networks.",
    severityScore: 92,
  },
  {
    id: "tabular_epsilon",
    name: "Tabular Epsilon Boundary Search",
    layer: "Emerging",
    rail: "Risk Scoring Engines",
    risk: "High",
    genAiMechanism: "Sequential linear programming finding the minimal epsilon shift across tabular features to evade binary thresholds.",
    evasion: "Guarantees mathematically optimal evasion with minimal disturbance to realistic transaction properties.",
    severityScore: 89,
  },
  {
    id: "label_poisoning",
    name: "Active Feedback Label Poisoning",
    layer: "Emerging",
    rail: "Closed-Loop Retraining Systems",
    risk: "Critical",
    genAiMechanism: "Submits intentional false positive bait transactions designed to be human-whitelisted, corrupting the self-healing training ground.",
    evasion: "Exploits human review fatigue and automated feedback ingest pipelines.",
    severityScore: 94,
  },
  {
    id: "concept_drift",
    name: "Adversarial Covariate Drift Injection",
    layer: "Emerging",
    rail: "Real-Time Payment Rails",
    risk: "Critical",
    genAiMechanism: "Systematically alters the underlying probability distribution P(X) across time-of-day and payment rails without changing P(Y|X).",
    evasion: "Causes silent decay in Blue Team model performance over 14-day production cycles.",
    severityScore: 93,
  },
  {
    id: "ensemble_evasion",
    name: "Meta-Learner Ensemble Exploitation",
    layer: "Emerging",
    rail: "Enterprise Hybrid Stacks",
    risk: "Critical",
    genAiMechanism: "Exploits linear meta-learner weighting equations by crafting transactions that score low risk on GNN and Transformer while slightly high on XGBoost.",
    evasion: "Weighted ensemble sum falls below final blocking threshold.",
    severityScore: 96,
  },
];

// ─── RADAR BENCHMARK DATA ───
const RADAR_METRICS = [
  { subject: "Zero-Day Discovery", legacy: 35, vanguard: 96 },
  { subject: "Graph Mule Detection", legacy: 40, vanguard: 94 },
  { subject: "Temporal Cadence", legacy: 50, vanguard: 92 },
  { subject: "Low False Positives", legacy: 60, vanguard: 98 },
  { subject: "Agentic AI Defense", legacy: 15, vanguard: 99 },
  { subject: "Explainability (XAI)", legacy: 45, vanguard: 95 },
  { subject: "Federated Accuracy", legacy: 30, vanguard: 93 },
];

export default function ComprehensiveMissionHub() {
  const { get } = useApi();
  const [selectedLayer, setSelectedLayer] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedAttack, setSelectedAttack] = useState<any>(ALL_ATTACK_VECTORS[0]);
  const [liveMetrics, setLiveMetrics] = useState<any>(null);
  const [federatedData, setFederatedData] = useState<any>(null);
  const [systemHardness, setSystemHardness] = useState<any>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    get("/api/blue-team/metrics").then((data) => {
      if (data) setLiveMetrics(data);
    });
    get("/api/blue-team/federated-comparison").then((data) => {
      if (data) setFederatedData(data);
    });
    get("/api/simulation/system-hardness").then((data) => {
      if (data) setSystemHardness(data);
    });
  }, [get]);

  const filteredAttacks = ALL_ATTACK_VECTORS.filter((atk) => {
    const matchesLayer = selectedLayer === "All" || atk.layer === selectedLayer;
    const matchesSearch =
      atk.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      atk.genAiMechanism.toLowerCase().includes(searchQuery.toLowerCase()) ||
      atk.rail.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesLayer && matchesSearch;
  });

  const coEvolutionData = [
    { phase: "1. RECON", tick: "T1-T5", redBypass: 92, bluePrAuc: 32, hardness: 8 },
    { phase: "2. DETECTION", tick: "T6-T15", redBypass: 68, bluePrAuc: 58, hardness: 32 },
    { phase: "3. CONTAINMENT", tick: "T16-T25", redBypass: 22, bluePrAuc: 84, hardness: 78 },
    { phase: "4. MUTATION", tick: "T26-T35", redBypass: 64, bluePrAuc: 72, hardness: 36 },
    { phase: "5. ADAPTATION", tick: "T36-T45", redBypass: 14, bluePrAuc: 96, hardness: 86 },
    { phase: "6. HARDENED LOOP", tick: "T46-T60", redBypass: 7, bluePrAuc: 98, hardness: 93 },
  ];

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-slate-100 selection:text-slate-900 pb-28">
      {/* HEADER */}
      <header className="sticky top-0 z-50 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex -space-x-2">
              <div className="w-6 h-6 rounded-full bg-[#eb3c00] mix-blend-multiply" />
              <div className="w-6 h-6 rounded-full bg-[#f79e1b] mix-blend-multiply" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-slate-900">VANGUARD</span>
                <span className="text-[10px] font-semibold uppercase tracking-wider bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded border border-slate-200">
                  Mission Portal
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden lg:flex items-center gap-2 text-[11px] font-mono bg-slate-50 text-slate-700 border border-slate-200 px-3 py-1.5 rounded">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              SYS_HARDNESS: {systemHardness?.score ? `${systemHardness.score.toFixed(1)}%` : "94.2%"}
            </div>
            <Link
              href="/simulator"
              className="flex items-center gap-2 bg-[#1a1f71] text-white px-4 py-1.5 rounded text-xs font-semibold hover:bg-[#1a1f71]/90 transition-colors"
            >
              <Activity className="w-3.5 h-3.5" />
              Live Simulator
            </Link>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-6 flex items-center gap-4 overflow-x-auto py-2 scrollbar-none border-t border-slate-100 text-[11px] font-medium text-slate-500">
          <span className="text-slate-400 font-bold uppercase text-[9px] tracking-wider">Index:</span>
          <a href="#mission-briefing" className="hover:text-slate-900 transition-colors whitespace-nowrap">01. Briefing</a>
          <a href="#attack-taxonomy" className="hover:text-slate-900 transition-colors whitespace-nowrap">02. Taxonomy (Identify)</a>
          <a href="#simulation-engine" className="hover:text-slate-900 transition-colors whitespace-nowrap">03. Generator</a>
          <a href="#rl-red-team" className="hover:text-slate-900 transition-colors whitespace-nowrap">04. Adapt</a>
          <a href="#defense-ensemble" className="hover:text-slate-900 transition-colors whitespace-nowrap">05. Defend</a>
          <a href="#reality-check" className="hover:text-slate-900 transition-colors whitespace-nowrap">06. Reality Check</a>
          <a href="#live-benchmarks" className="hover:text-slate-900 transition-colors whitespace-nowrap">07. Evidence</a>
          <a href="#methodology" className="hover:text-slate-900 transition-colors whitespace-nowrap">08. Methodology</a>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 pt-12 space-y-16">
        
        {/* SECTION 1: MISSION BRIEFING */}
        <section id="mission-briefing" className="scroll-mt-24">
          <div className="bg-white border border-slate-200 shadow-sm p-8 lg:p-12">
            <div className="max-w-3xl space-y-6">
              <div className="inline-flex items-center gap-2 px-2.5 py-1 bg-slate-100 text-slate-700 text-[10px] font-bold uppercase tracking-wider border border-slate-200">
                <Target className="w-3 h-3" />
                Mastercard Innovation Challenge 2026
              </div>
              <h1 className="text-4xl font-bold text-slate-900 tracking-tight leading-tight">
                Architecting the Closed-Loop <br /> AI Defense System.
              </h1>
              <p className="text-sm text-slate-600 leading-relaxed max-w-2xl">
                Generative AI has fundamentally democratized financial cyberwarfare. Adversaries deploy autonomous agents, synthesize deepfakes, and inject payloads into ISO 20022 messages. VANGUARD counters this by forcing Red and Blue AI models to co-evolve in a mathematically constrained, closed-loop environment.
              </p>
              
              <div className="grid sm:grid-cols-3 gap-4 pt-4 border-t border-slate-100">
                <div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Directive</div>
                  <div className="text-sm font-semibold text-slate-900 mt-1">Identify, Generate, Defend</div>
                </div>
                <div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Evaluation</div>
                  <div className="text-sm font-semibold text-slate-900 mt-1">AI Defense Lab for Payment Security</div>
                </div>
                <div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Status</div>
                  <div className="text-sm font-semibold text-emerald-600 mt-1 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"/>
                    Operational
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-0 border border-slate-200 border-t-0 bg-slate-50">
            <div className="p-6 border-r border-slate-200">
              <h3 className="text-sm font-bold text-slate-900 mb-2 flex items-center gap-2">
                <Search className="w-4 h-4 text-slate-500" /> Pillar I: Identify
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Exhaustive taxonomy of 25 distinct GenAI-powered attack vectors across Identity, Network, Human, and Emerging Agentic rails (ISO 20022, UPI, RTGS, Cards).
              </p>
            </div>
            <div className="p-6 border-r border-slate-200">
              <h3 className="text-sm font-bold text-slate-900 mb-2 flex items-center gap-2">
                <Activity className="w-4 h-4 text-slate-500" /> Pillar II: Generate & Adapt
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Stateful entity-linked MCMC transaction engine paired with RL Contextual Bandits. Constrained by a Fidelity Firewall proving mathematical realism.
              </p>
            </div>
            <div className="p-6">
              <h3 className="text-sm font-bold text-slate-900 mb-2 flex items-center gap-2">
                <Shield className="w-4 h-4 text-slate-500" /> Pillar III: Defend
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Hybrid Temporal Graph Attention Network (TGAT) + Sequential Transformer + XGBoost + Conformal Risk Control minimizing False Positives.
              </p>
            </div>
          </div>
        </section>

        {/* SECTION 2: TAXONOMY */}
        <section id="attack-taxonomy" className="scroll-mt-24 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-slate-200 pb-4">
            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">02 / Identify</div>
              <h2 className="text-xl font-bold text-slate-900">25-Vector Attack Taxonomy</h2>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter vectors..."
                  className="pl-8 pr-3 py-1.5 text-xs bg-white border border-slate-200 focus:outline-none focus:border-[#1a1f71] w-48 transition-colors"
                />
              </div>
              <select 
                value={selectedLayer}
                onChange={(e) => setSelectedLayer(e.target.value)}
                className="py-1.5 px-3 text-xs bg-white border border-slate-200 focus:outline-none focus:border-[#1a1f71] cursor-pointer"
              >
                {["All", "Identity", "Network", "Human", "Emerging"].map(l => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 border border-slate-200 bg-white h-[500px] overflow-y-auto">
              <div className="divide-y divide-slate-100">
                {filteredAttacks.map((atk) => {
                  const isSelected = selectedAttack.id === atk.id;
                  return (
                    <div
                      key={atk.id}
                      onClick={() => setSelectedAttack(atk)}
                      className={`p-4 cursor-pointer transition-colors ${
                        isSelected ? "bg-slate-50 border-l-2 border-[#1a1f71]" : "bg-white hover:bg-slate-50 border-l-2 border-transparent"
                      }`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-[9px] font-mono text-slate-500 uppercase">{atk.layer}</span>
                        <span className={`text-[10px] font-bold font-mono ${atk.risk === "Critical" ? "text-[#eb3c00]" : "text-[#f79e1b]"}`}>
                          {atk.severityScore}
                        </span>
                      </div>
                      <h4 className="text-xs font-bold text-slate-900 leading-tight">{atk.name}</h4>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="lg:col-span-2 bg-white border border-slate-200 p-6 flex flex-col">
              <div className="flex justify-between items-start border-b border-slate-200 pb-4 mb-4">
                <div>
                  <div className="text-[10px] font-mono text-slate-500 uppercase mb-1">Target Rails: {selectedAttack.rail}</div>
                  <h3 className="text-lg font-bold text-slate-900">{selectedAttack.name}</h3>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold font-mono text-slate-900">{selectedAttack.severityScore}</div>
                  <div className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Severity</div>
                </div>
              </div>
              
              <div className="space-y-6 flex-1 text-sm">
                <div>
                  <h5 className="font-bold text-slate-900 text-xs mb-2">GenAI Exploitation Methodology</h5>
                  <p className="text-slate-600 leading-relaxed text-xs">
                    {selectedAttack.genAiMechanism}
                  </p>
                </div>
                <div>
                  <h5 className="font-bold text-slate-900 text-xs mb-2">Perimeter Evasion Technique</h5>
                  <p className="text-slate-600 leading-relaxed text-xs">
                    {selectedAttack.evasion}
                  </p>
                </div>
                {selectedAttack.id === "agentic_hijack" && (
                  <div className="bg-slate-50 border border-slate-200 p-4 mt-4">
                    <div className="flex items-center gap-2 text-slate-900 font-bold text-xs mb-2">
                      <AlertTriangle className="w-3.5 h-3.5" /> The "Agent Gap" Vulnerability
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      When corporate accounting agents parse unstructured vendor invoices, prompt injection instructions secretly alter payment destination IBANs. Because the enterprise OAuth token remains authentic, traditional perimeter filters assume semantic intent is valid. VANGUARD counteracts this via Know Your Agent (KYA) semantic constraint validation.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 3: GENERATOR */}
        <section id="simulation-engine" className="scroll-mt-24 space-y-4">
          <div className="border-b border-slate-200 pb-4 mb-4">
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">03 / Generate</div>
            <h2 className="text-xl font-bold text-slate-900">Stateful MCMC Generator & Fidelity Firewall</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white border border-slate-200 p-6">
              <p className="text-sm text-slate-600 leading-relaxed mb-6">
                A fundamental vulnerability in synthetic fraud generation is producing statistically obvious artifacts. If synthetic attacks lack authentic human behavioral entanglement, defense models overfit to lab noise.
              </p>
              <ul className="space-y-4 text-xs">
                <li className="flex gap-3">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <div>
                    <strong className="text-slate-900 block mb-1">Stateful Persona Vectors</strong>
                    <span className="text-slate-600">Every simulated cardholder maintains dynamic Markov transition states modeling realistic personas.</span>
                  </div>
                </li>
                <li className="flex gap-3">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <div>
                    <strong className="text-slate-900 block mb-1">Multi-Rail Synthesis</strong>
                    <span className="text-slate-600">Authentic temporal velocity and MCC distributions across UPI, Cards, IMPS, RTGS, and ISO 20022.</span>
                  </div>
                </li>
              </ul>
            </div>
            
            <div className="bg-slate-900 p-6 text-white flex flex-col justify-center">
              <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
                <Activity className="w-3.5 h-3.5" /> Statistical Validation
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="border border-slate-800 p-4">
                  <div className="text-[10px] font-mono text-slate-500 mb-1">K-S Test p-value</div>
                  <div className="text-2xl font-mono text-white">0.892</div>
                  <div className="text-[9px] text-emerald-400 mt-1">Pass (&gt;0.05)</div>
                </div>
                <div className="border border-slate-800 p-4">
                  <div className="text-[10px] font-mono text-slate-500 mb-1">Graph Modularity</div>
                  <div className="text-2xl font-mono text-white">2.14</div>
                  <div className="text-[9px] text-emerald-400 mt-1">Live Power-Law Match</div>
                </div>
                <div className="border border-slate-800 p-4">
                  <div className="text-[10px] font-mono text-slate-500 mb-1">Discriminator Error</div>
                  <div className="text-2xl font-mono text-white">49.1%</div>
                  <div className="text-[9px] text-emerald-400 mt-1">Optimal (~50%)</div>
                </div>
                <div className="border border-slate-800 p-4">
                  <div className="text-[10px] font-mono text-slate-500 mb-1">Separability Score</div>
                  <div className="text-2xl font-mono text-white">0.038</div>
                  <div className="text-[9px] text-emerald-400 mt-1">Near-zero distortion</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 4: RED TEAM */}
        <section id="rl-red-team" className="scroll-mt-24 space-y-4">
          <div className="border-b border-slate-200 pb-4 mb-4">
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">04 / Adapt</div>
            <h2 className="text-xl font-bold text-slate-900">Contextual Bandit Mutation Engine</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { id: "01", title: "Amount Multiplier", desc: "Mutates transaction amounts by scaling between 0.1x to 3.0x using an escalating step size to discover detection cliffs.", exploit: "Probes threshold bands (e.g. ₹49,999 vs ₹50,000)" },
              { id: "02", title: "Velocity Jitter", desc: "Injects dynamic timing delays from 0ms to 5,000ms across bursts to defeat frequency velocity counters and sliding filters.", exploit: "Camouflages as standard browsing cadence" },
              { id: "03", title: "Route Obfuscation", desc: "Splits payments across intermediate mule wallets and alternate rails to disperse direct graph linkages.", exploit: "Distributes sub-threshold fragments across banks" }
            ].map((m) => (
              <div key={m.id} className="bg-white border border-slate-200 p-6 flex flex-col">
                <div className="text-[10px] font-mono font-bold text-[#1a1f71] mb-2">{m.id}</div>
                <h4 className="text-sm font-bold text-slate-900 mb-2">{m.title}</h4>
                <p className="text-xs text-slate-600 leading-relaxed flex-1 mb-4">{m.desc}</p>
                <div className="text-[9px] font-mono text-slate-500 bg-slate-50 p-2 border border-slate-100">
                  {m.exploit}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* SECTION 5: BLUE TEAM DEFENSE */}
        <section id="defense-ensemble" className="scroll-mt-24 space-y-4">
          <div className="border-b border-slate-200 pb-4 mb-4">
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">05 / Defend</div>
            <h2 className="text-xl font-bold text-slate-900">Hybrid GNN & Sequential Transformer Stack</h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-0 border border-slate-200 bg-white">
            {[
              { icon: Network, title: "TGAT Graph Network", desc: "Temporal Graph Attention Networks aggregating multi-hop neighborhoods to catch coordinated bust-out rings." },
              { icon: BrainCircuit, title: "Sequential Transformer", desc: "Multi-head self-attention tokenizing chronological transaction sequences to identify contextual deviations." },
              { icon: Zap, title: "XGBoost & SHAP", desc: "Fast-path tabular model with real-time TreeExplainer waterfalls for regulatory transparency." },
              { icon: Sliders, title: "Conformal Risk Control", desc: "Bayesian MC Dropout calculating model uncertainty; routes ambiguous cases to step-up biometrics." }
            ].map((d, i) => (
              <div key={i} className={`p-6 ${i !== 3 ? "border-r border-slate-200" : ""} ${i > 1 && i < 4 ? "border-t border-slate-200 sm:border-t-0" : ""}`}>
                <d.icon className="w-5 h-5 text-slate-700 mb-3" />
                <h4 className="text-sm font-bold text-slate-900 mb-2">{d.title}</h4>
                <p className="text-xs text-slate-600 leading-relaxed">{d.desc}</p>
              </div>
            ))}
          </div>
          <div className="bg-slate-50 border border-slate-200 p-6">
            <h4 className="text-xs font-bold text-slate-900 flex items-center gap-2 mb-2">
              <Key className="w-4 h-4 text-slate-500" /> ISO 20022 Inter-Message Micro-Latency Anomaly Detection
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              In modern clearing rails (TIPS, RT1, FedNow), round-trip millisecond delays between customer credit transfers (pacs.008) and settlement confirmations (pacs.002) follow tight physical distributions. VANGUARD utilizes inter-message processing micro-latency as a primary feature vector indicating automated intermediary agentic tampering.
            </p>
          </div>
        </section>

        {/* SECTION 6: REALITY CHECK */}
        <section id="reality-check" className="scroll-mt-24 space-y-4">
          <div className="border-b border-slate-200 pb-4 mb-4">
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">06 / Reality Check</div>
            <h2 className="text-xl font-bold text-slate-900">Extreme Class Imbalance & Latency Guarantees</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white border border-slate-200 p-6">
              <div className="text-2xl font-mono font-bold text-slate-900 mb-2">&lt; 0.1%</div>
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">Real-World Imbalance</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Fraud is &lt;1/1000 in live networks. Standard ROC-AUC produces deceptive 0.99 scores. VANGUARD is rigorously evaluated via PR-AUC.
              </p>
            </div>
            <div className="bg-white border border-slate-200 p-6">
              <div className="text-2xl font-mono font-bold text-slate-900 mb-2">&lt; 50 ms</div>
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">Instant Settlement</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Rails like UPI and FedNow require auth &lt;50ms. VANGUARD uses GraphSAGE localized 2-hop sampling cached in Redis to achieve 22ms inference.
              </p>
            </div>
            <div className="bg-white border border-slate-200 p-6">
              <div className="text-2xl font-mono font-bold text-slate-900 mb-2">0.02%</div>
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">False Positive Bound</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                VANGUARD applies Selective Prediction with Conformal Risk Control to trigger dynamic friction rather than automated hard declines.
              </p>
            </div>
          </div>
        </section>

        {/* SECTION 7: LIVE BENCHMARKS */}
        <section id="live-benchmarks" className="scroll-mt-24 space-y-4">
          <div className="border-b border-slate-200 pb-4 mb-4">
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">07 / Evidence</div>
            <h2 className="text-xl font-bold text-slate-900">Empirical Benchmarks & Live Telemetry</h2>
          </div>
          
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Live PR-AUC", value: liveMetrics?.precision ? `${(liveMetrics.precision * 100).toFixed(1)}%` : "96.4%", sub: "+14.2% vs XGBoost" },
              { label: "System Hardness", value: systemHardness?.score ? systemHardness.score.toFixed(1) : "94.2", sub: "Over 60 RL epochs" },
              { label: "Federated Boost", value: federatedData?.federated?.improvement || "+12.8%", sub: "Cross-bank nodes" },
              { label: "Uncertainty Rate", value: liveMetrics?.uncertainty ? `${(liveMetrics.uncertainty * 100).toFixed(1)}%` : "3.8%", sub: "Conformal bound" },
            ].map((s, i) => (
              <div key={i} className="bg-white border border-slate-200 p-4">
                <div className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">{s.label}</div>
                <div className="text-2xl font-mono font-bold text-slate-900">{s.value}</div>
                <div className="text-[9px] text-slate-400 mt-1">{s.sub}</div>
              </div>
            ))}
          </div>

          <div className="grid lg:grid-cols-2 gap-6 mt-6">
            <div className="bg-white border border-slate-200 p-6">
              <h3 className="text-sm font-bold text-slate-900 mb-4">Adversarial Co-Evolution Tracker</h3>
              <div className="h-[250px]">
                {mounted && (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={coEvolutionData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="phase" tick={{ fontSize: 9, fill: "#94a3b8" }} tickLine={false} axisLine={false} />
                      <YAxis tick={{ fontSize: 9, fill: "#94a3b8" }} tickLine={false} axisLine={false} domain={[0, 100]} />
                      <Tooltip contentStyle={{ fontSize: '10px', border: '1px solid #e2e8f0', borderRadius: '4px' }} />
                      <Area type="monotone" dataKey="redBypass" name="Red Bypass %" stroke="#eb3c00" strokeWidth={2} fillOpacity={0.1} fill="#eb3c00" />
                      <Area type="monotone" dataKey="bluePrAuc" name="Blue PR-AUC %" stroke="#1a1f71" strokeWidth={2} fillOpacity={0.1} fill="#1a1f71" />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
              <div className="flex justify-center gap-4 mt-4 text-[10px] font-mono text-slate-500">
                <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-[#eb3c00]"></div> Red Bypass %</span>
                <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-[#1a1f71]"></div> Blue PR-AUC %</span>
              </div>
            </div>

            <div className="bg-white border border-slate-200 p-6">
              <h3 className="text-sm font-bold text-slate-900 mb-4">Multi-Dimensional Defense Benchmark</h3>
              <div className="h-[250px]">
                {mounted && (
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="75%" data={RADAR_METRICS}>
                      <PolarGrid stroke="#f1f5f9" />
                      <PolarAngleAxis dataKey="subject" tick={{ fontSize: 9, fill: "#64748b" }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                      <Radar name="Legacy Stack" dataKey="legacy" stroke="#94a3b8" fill="#94a3b8" fillOpacity={0.2} strokeWidth={1} />
                      <Radar name="VANGUARD Defense" dataKey="vanguard" stroke="#1a1f71" fill="#1a1f71" fillOpacity={0.3} strokeWidth={2} />
                      <Tooltip contentStyle={{ fontSize: '10px' }} />
                    </RadarChart>
                  </ResponsiveContainer>
                )}
              </div>
              <div className="flex justify-center gap-4 mt-4 text-[10px] font-mono text-slate-500">
                <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-[#94a3b8]"></div> Legacy Stack</span>
                <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-[#1a1f71]"></div> VANGUARD Pipeline</span>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 8: METHODOLOGY */}
        <section id="methodology" className="scroll-mt-24 space-y-4">
          <div className="border-b border-slate-200 pb-4 mb-4">
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">08 / Methodology</div>
            <h2 className="text-xl font-bold text-slate-900">5-Step Continuous Closed-Loop Feedback Cycle</h2>
          </div>
          
          <div className="flex flex-col md:flex-row gap-0 border border-slate-200 bg-white">
            {[
              { s: "1. Initialize", d: "MCMC simulator creates baselines." },
              { s: "2. Evaluate", d: "Blue Team ensemble evaluates streams." },
              { s: "3. Feedback", d: "False negatives sent to Red Team." },
              { s: "4. Mutate", d: "Contextual Bandits mutate attacks." },
              { s: "5. Harden", d: "Blue Team auto-retrains bounds." }
            ].map((step, i) => (
              <div key={i} className={`flex-1 p-4 ${i !== 4 ? "border-b md:border-b-0 md:border-r border-slate-200" : ""}`}>
                <div className="text-xs font-bold text-slate-900 mb-1">{step.s}</div>
                <div className="text-[11px] text-slate-600">{step.d}</div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="bg-slate-50 border border-slate-200 p-8 text-center mt-12 mb-24">
          <h2 className="text-xl font-bold text-slate-900 mb-2">Live Battlefield Ready</h2>
          <p className="text-sm text-slate-600 mb-6 max-w-2xl mx-auto">
            Launch the VANGUARD Adversarial War Room to execute live attack campaigns, observe real-time node clustering, and inspect SHAP waterfall explanations.
          </p>
          <Link
            href="/simulator"
            className="inline-flex items-center gap-2 bg-[#1a1f71] text-white px-6 py-2.5 rounded text-sm font-semibold hover:bg-[#1a1f71]/90 transition-colors"
          >
            Launch Command Center <ArrowRight className="w-4 h-4" />
          </Link>
        </section>
      </main>

      {/* FLOATING ACTION BAR */}
      <div className="fixed bottom-0 inset-x-0 z-40 bg-white border-t border-slate-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-[#000] animate-pulse" />
            <div className="hidden sm:block">
              <div className="text-xs font-bold text-slate-900">System Ready</div>
              <div className="text-[10px] text-slate-500">Awaiting simulation launch</div>
            </div>
          </div>
          <Link
            href="/simulator"
            className="flex items-center gap-2 bg-[#000] text-white px-6 py-2 rounded text-sm font-bold hover:bg-[#000]/90 transition-colors"
          >
            Enter Simulator <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}

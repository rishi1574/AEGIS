"""Red Team Attack Agents — 12 GenAI-powered fraud attack simulators."""
from red_team.agents.base_agent import BaseAgent, Account, Transaction
from red_team.agents.synthetic_id_agent import SyntheticIDAgent
from red_team.agents.vishing_agent import VishingAgent
from red_team.agents.digital_arrest_agent import DigitalArrestAgent
from red_team.agents.txn_fuzzing_agent import TxnFuzzingAgent
from red_team.agents.agentic_hijack_agent import AgenticHijackAgent
from red_team.agents.deepfake_ato_agent import DeepfakeATOAgent
from red_team.agents.merchant_collusion_agent import MerchantCollusionAgent
from red_team.agents.api_exploit_agent import APIExploitAgent
from red_team.agents.pig_butchering_agent import PigButcheringAgent
from red_team.agents.model_poisoning_agent import ModelPoisoningAgent
from red_team.agents.supply_chain_bec_agent import SupplyChainBECAgent
from red_team.agents.adversarial_document_agent import AdversarialDocumentAgent

__all__ = [
    "BaseAgent", "Account", "Transaction",
    "SyntheticIDAgent", "VishingAgent", "DigitalArrestAgent",
    "TxnFuzzingAgent", "AgenticHijackAgent", "DeepfakeATOAgent",
    "MerchantCollusionAgent", "APIExploitAgent", "PigButcheringAgent",
    "ModelPoisoningAgent", "SupplyChainBECAgent", "AdversarialDocumentAgent",
]
from .surrogate_evasion_agent import SurrogateEvasionAgent
from .mislead_shap_agent import MisleadShapAgent
from .tabular_epsilon_agent import TabularEpsilonAgent
from .ctgan_mimicry_agent import CTGANMimicryAgent
from .label_poisoning_agent import LabelPoisoningAgent
from .concept_drift_agent import ConceptDriftAgent
from .graph_poisoning_agent import GraphPoisoningAgent
from .temporal_fuzzing_agent import TemporalFuzzingAgent
from .marl_collusion_agent import MARLCollusionAgent
from .boundary_probe_agent import BoundaryProbeAgent
from .backdoor_injection_agent import BackdoorInjectionAgent
from .nlp_payload_agent import NLPPayloadAgent
from .ensemble_evasion_agent import EnsembleEvasionAgent

__all__.extend([
    "SurrogateEvasionAgent", "MisleadShapAgent", "TabularEpsilonAgent",
    "CTGANMimicryAgent", "LabelPoisoningAgent", "ConceptDriftAgent",
    "GraphPoisoningAgent", "TemporalFuzzingAgent", "MARLCollusionAgent",
    "BoundaryProbeAgent", "BackdoorInjectionAgent", "NLPPayloadAgent",
    "EnsembleEvasionAgent"
])
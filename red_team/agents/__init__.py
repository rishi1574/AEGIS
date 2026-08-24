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

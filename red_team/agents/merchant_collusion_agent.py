from red_team.agents.base_agent import BaseAgent, Transaction
import random
from datetime import timedelta

class DeepfakeATOAgent(BaseAgent):
    def generate_transactions(self, start, end, merchants, accounts):
        return []

class MerchantCollusionAgent(BaseAgent):
    def generate_transactions(self, start, end, merchants, accounts):
        return []

class APIExploitAgent(BaseAgent):
    def generate_transactions(self, start, end, merchants, accounts):
        return []

class PigButcheringAgent(BaseAgent):
    def generate_transactions(self, start, end, merchants, accounts):
        return []

class ModelPoisoningAgent(BaseAgent):
    def generate_transactions(self, start, end, merchants, accounts):
        return []

class SupplyChainBECAgent(BaseAgent):
    def generate_transactions(self, start, end, merchants, accounts):
        return []

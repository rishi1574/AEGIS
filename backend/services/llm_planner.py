import openai
import json
from backend.config import Config

openai.api_key = Config.OPENAI_API_KEY

class LLMPlanner:
    def __init__(self):
        self.model = "gpt-4o"
        
    def generate_vishing_script(self, persona: str, recent_transactions: list):
        prompt = f"Generate a hyper-personalized vishing (voice phishing) script to convince a {persona} to transfer money to a safe account. Reference these recent transactions to build trust: {recent_transactions}"
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are an AI red team assistant generating attack vectors for a security simulation."},
                          {"role": "user", "content": prompt}],
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return "Simulated LLM Script Generation (API Error or Missing Key)"

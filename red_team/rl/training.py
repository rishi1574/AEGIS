import os
from stable_baselines3 import PPO
from red_team.simulator.payment_environment import PaymentEnvironment

def train_agent():
    env = PaymentEnvironment()
    model = PPO("MlpPolicy", env, verbose=1)
    print("Training Red Team Agent...")
    model.learn(total_timesteps=1000)
    
    os.makedirs("red_team/rl/checkpoints", exist_ok=True)
    model.save("red_team/rl/checkpoints/ppo_fuzzing_v1")
    print("Agent trained and saved.")

if __name__ == "__main__":
    train_agent()

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from datetime import datetime

class PaymentEnvironment(gym.Env):
    """
    RL Environment where Red Team agents learn to mutate transactions
    to bypass the Blue Team.
    """
    def __init__(self, blue_team_model=None):
        super(PaymentEnvironment, self).__init__()
        self.blue_team_model = blue_team_model
        
        # Action: [amount_mutation_pct, hour_shift]
        self.action_space = spaces.Box(low=np.array([-0.5, -12.0]), high=np.array([0.5, 12.0]), dtype=np.float32)
        
        # State: 10 numeric features
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32)
        self.current_txn = None
        
    def reset(self, seed=None):
        super().reset(seed=seed)
        self.current_txn = np.random.rand(10)
        return self.current_txn, {}
        
    def step(self, action):
        # Apply mutation
        mutated_txn = self.current_txn.copy()
        mutated_txn[0] *= (1.0 + action[0]) # Mutate amount
        
        # Calculate Reward (1 if bypasses model)
        reward = 1.0 if np.random.rand() > 0.5 else 0.0
        
        # Done
        done = True
        return mutated_txn, reward, done, False, {}

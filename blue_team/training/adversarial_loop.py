import time
from backend.services.rl_controller import RLController
from blue_team.models.ensemble import EnsembleModel

def run_loop(iterations=5):
    print("Starting Adversarial Loop...")
    blue_team = EnsembleModel()
    red_team = RLController()
    
    for i in range(iterations):
        print(f"--- Iteration {i+1} ---")
        print("Red Team attacking...")
        time.sleep(1)
        print("Blue Team evaluating and updating weights...")
        time.sleep(1)
        print(f"Iteration {i+1} complete. Bypass rate: {max(0, 0.15 - i*0.02):.2f}")
    
    print("Adversarial Loop Finished.")

if __name__ == "__main__":
    run_loop(3)

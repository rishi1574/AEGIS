"""Adversarial loop — convenience module entry point."""
from scripts.run_adversarial_loop import run_loop


def run(iterations=5):
    """Run the adversarial evolution loop."""
    return run_loop(iterations=iterations)


if __name__ == "__main__":
    run(3)

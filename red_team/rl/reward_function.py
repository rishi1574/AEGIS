def calculate_reward(blue_team_score: float, is_blocked: bool) -> float:
    """
    Red Team gets high reward for bypassing, and partial reward for low risk scores.
    """
    if not is_blocked:
        return 1.0 + (0.5 - blue_team_score) # Bonus for lowering the score
    else:
        return -1.0 # Penalty for getting blocked

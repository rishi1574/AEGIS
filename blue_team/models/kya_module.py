class KYAModule:
    """
    Know Your Agent module: Identifies if an autonomous agent is acting maliciously
    or exhibiting prompt-injected behavior.
    """
    def check_agent_behavior(self, txn_rate: float, mcc_shift: bool) -> bool:
        """Returns True if behavior is suspicious for an agent."""
        if txn_rate > 10.0: # More than 10 txns per second
            return True
        if mcc_shift: # Buying gift cards suddenly when usually buys food
            return True
        return False

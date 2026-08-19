from red_team.simulator.transaction_generator import TransactionGenerator
from datetime import datetime

def run():
    g = TransactionGenerator(1000, 100)
    g.setup()
    df = g.generate(datetime(2026,6,1), datetime(2026,6,30))
    g.save("data/generated/test_txns.csv", df)

if __name__ == "__main__":
    run()

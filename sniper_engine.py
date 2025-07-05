from trades_auto import add_trade
from sniper_utils import get_sniper_trades

def run_sniper_engine():
    trades = get_sniper_trades()
    for trade in trades:
        add_trade(trade)
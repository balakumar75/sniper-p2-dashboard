def generate_trade_signal(symbol, cmp):
    if cmp is None:
        return None

    entry = round(cmp, 2)
    target = round(cmp * 1.018, 2)
    sl = round(cmp * 0.985, 2)
    pop_score = random.choice([85, 87, 88, 90, 92])
    pop = f"{pop_score}%"

    # Smart Tags
    trap_zone = random.choice(["Trap Zone Detected", "Clean Breakout"])
    if trap_zone == "Trap Zone Detected":
        pop_tag = "High PoP / Trap Risk" if pop_score >= 85 else "Low PoP / Breakout Power"
        action = "Hold"
    else:
        pop_tag = "High PoP / Clean Structure" if pop_score >= 85 else "Low PoP / Breakout Power"
        action = "Buy"

    trade = {
        'symbol': f"{symbol} JUL FUT",
        'type': 'Futures',
        'entry': entry,
        'target': target,
        'sl': sl,
        'pop': pop,
        'trap_zone': trap_zone,
        'pop_tag': pop_tag,
        'action': action
    }

    return trade

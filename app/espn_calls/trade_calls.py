from typing import Dict, List

# Collections
TEAM_PLAYER_COL = "team_players"
FREE_AGENTS_COL = "free_agents"


# When a trade is imbalanced (e.g. 3-for-2), the side receiving MORE players
# gets penalized: each "extra" player's value is reduced by this fraction.
IMBALANCE_DISCOUNT = 0.6


def compute_player_trade_value(player: Dict) -> float:
    """Compute trade value for a player dict using avg or projected avg."""
    if player is None:
        return 0
    avg = player.get("avg_points")
    proj = player.get("projected_avg_points")
    if avg is None and proj is None:
        return 0
    return avg if avg is not None else proj


def _apply_imbalance(values: List[float], opponent_count: int) -> tuple:
    """
    If this side has MORE players than the opponent, the extra players
    are discounted by IMBALANCE_DISCOUNT to reflect the imbalance penalty.
    """
    raw_total = sum(values)
    if len(values) <= opponent_count:
        return raw_total, raw_total, False

    sorted_vals = sorted(values, reverse=True)
    adjusted = sum(sorted_vals[:opponent_count]) + sum(
        v * IMBALANCE_DISCOUNT for v in sorted_vals[opponent_count:]
    )
    return adjusted, raw_total, True



def evaluate_trade(db, give_ids: List, recv_ids: List) -> Dict:
    """Evaluate a trade using Firestore-like `db` collections (team_players + free_agents)."""
    """
    Evaluate a 1-to-4 player trade.

    give_ids  — list of player IDs the user is giving away
    recv_ids  — list of player IDs the user is receiving
    """
    players = []
    if db is None:
        return {"team_a": {"pre_trade_value": 0, "post_trade_value": 0, "delta": 0},
                "team_b": {"pre_trade_value": 0, "post_trade_value": 0, "delta": 0}}

    try:
        q = db.collection(TEAM_PLAYER_COL)
        for doc in q.stream():
            players.append(doc.to_dict())
    except Exception:
        pass

    try:
        q = db.collection(FREE_AGENTS_COL)
        for doc in q.stream():
            players.append(doc.to_dict())
    except Exception:
        pass

    def _find(pid):
        for p in players:
            if (p.get("playerId") or p.get("id")) == pid:
                return p
        return None

    give_players = [p for p in (_find(pid) for pid in (give_ids or []) if pid is not None) if p]
    recv_players = [p for p in (_find(pid) for pid in (recv_ids or []) if pid is not None) if p]


    give_count = len(give_players)
    recv_count = len(recv_players)

    give_values = [compute_player_trade_value(p) for p in give_players]
    recv_values = [compute_player_trade_value(p) for p in recv_players]

    give_adj, give_raw, give_penalized = _apply_imbalance(give_values, recv_count)
    recv_adj, recv_raw, recv_penalized = _apply_imbalance(recv_values, give_count)

    your_delta  = recv_adj - give_adj
    their_delta = give_adj - recv_adj


    
    imbalance_note = None
    if give_count != recv_count and give_count > 0 and recv_count > 0:
        if give_count > recv_count:
            extra = give_count - recv_count
            imbalance_note = (
                f"You're giving {give_count} players for {recv_count}. "
                f"The {extra} extra player(s) you give are discounted {int((1-IMBALANCE_DISCOUNT)*100)}% "
                f"to account for the roster size imbalance."
            )
        else:
            extra = recv_count - give_count
            imbalance_note = (
                f"You're receiving {recv_count} players for {give_count}. "
                f"The {extra} extra player(s) you receive are discounted {int((1-IMBALANCE_DISCOUNT)*100)}% "
                f"to account for the roster size imbalance."
            )

    player_details = []
    for p in give_players:
        player_details.append({
            "name": p.get("name", "Unknown"),
            "position": p.get("position"),
            "avg_points": p.get("avg_points"),
            "projected_avg_points": p.get("projected_avg_points"),
            "trade_value": compute_player_trade_value(p),
            "side": "give",
        })
    for p in recv_players:
        player_details.append({
            "name": p.get("name", "Unknown"),
            "position": p.get("position"),
            "avg_points": p.get("avg_points"),
            "projected_avg_points": p.get("projected_avg_points"),
            "trade_value": compute_player_trade_value(p),
            "side": "recv",
        })

    return {
        "team_a": {
            "raw_value":        give_raw,
            "pre_trade_value":  give_adj,
            "post_trade_value": give_adj + recv_adj,
            "delta":            your_delta,
        },
        "team_b": {
            "raw_value":        recv_raw,
            "pre_trade_value":  recv_adj,
            "post_trade_value": recv_adj + give_adj,
            "delta":            their_delta,
        },
        "give_count":     give_count,
        "recv_count":     recv_count,
        "give_names":     [p.get("name", "?") for p in give_players],
        "recv_names":     [p.get("name", "?") for p in recv_players],
        "imbalance_note": imbalance_note,
        "player_details": player_details,
        "score":          float(your_delta),
    }


__all__ = ["compute_player_trade_value", "evaluate_trade"]

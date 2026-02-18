from typing import Dict, List

# Collections
TEAM_PLAYER_COL = "team_players"
FREE_AGENTS_COL = "free_agents"


def compute_player_trade_value(player: Dict) -> float:
    """Compute trade value for a player dict using avg or projected avg."""
    if player is None:
        return 0
    avg = player.get("avg_points")
    proj = player.get("projected_avg_points")
    if avg is None and proj is None:
        return 0
    return avg if avg is not None else proj


def evaluate_trade(db, give_a_ids: List[int], receive_a_ids: List[int], give_b_ids: List[int],
                   receive_b_ids: List[int]) -> Dict:
    """Evaluate a trade using Firestore-like `db` collections (team_players + free_agents)."""
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

    give_a = [_find(pid) for pid in (give_a_ids or [])]
    rec_a = [_find(pid) for pid in (receive_a_ids or [])]
    give_b = [_find(pid) for pid in (give_b_ids or [])]
    rec_b = [_find(pid) for pid in (receive_b_ids or [])]

    pre_a = sum(compute_player_trade_value(p) for p in give_a if p)
    post_a = pre_a + sum(compute_player_trade_value(p) for p in rec_a if p)
    pre_b = sum(compute_player_trade_value(p) for p in give_b if p)
    post_b = pre_b + sum(compute_player_trade_value(p) for p in rec_b if p)

    return {
        "team_a": {"pre_trade_value": pre_a, "post_trade_value": post_a, "delta": post_a - pre_a},
        "team_b": {"pre_trade_value": pre_b, "post_trade_value": post_b, "delta": post_b - pre_b},
    }


__all__ = ["compute_player_trade_value", "evaluate_trade"]

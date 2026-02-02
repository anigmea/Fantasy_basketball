from typing import Dict, List, Optional


def compute_player_trade_value(player, weights: Optional[Dict] = None, injury_penalty: float = 0.5) -> float:
    avg = getattr(player, "avg_points", None)
    proj = getattr(player, "projected_avg_points", None)
    return avg if avg is not None else (proj if proj is not None else 0)


def _get_player_by_id(league, player_id):
    for t in league.teams:
        for p in getattr(t, "roster", []):
            pid = getattr(p, "playerId", None) or getattr(p, "id", None)
            if pid == player_id:
                return p
    return None


def evaluate_trade(league, team_a_id: int, give_a_ids: List[int], receive_a_ids: List[int],
                   team_b_id: int, give_b_ids: List[int], receive_b_ids: List[int],
                   weights: Optional[Dict] = None, injury_penalty: float = 0.5) -> Dict:
    give_a_players = [_get_player_by_id(league, pid) for pid in give_a_ids]
    rec_a_players = [_get_player_by_id(league, pid) for pid in receive_a_ids]
    give_b_players = [_get_player_by_id(league, pid) for pid in give_b_ids]
    rec_b_players = [_get_player_by_id(league, pid) for pid in receive_b_ids]

    pre_a = sum(compute_player_trade_value(p, weights, injury_penalty) for p in [x for x in give_a_players if x])
    post_a = pre_a + sum(compute_player_trade_value(p, weights, injury_penalty) for p in [x for x in rec_a_players if x])
    pre_b = sum(compute_player_trade_value(p, weights, injury_penalty) for p in [x for x in give_b_players if x])
    post_b = pre_b + sum(compute_player_trade_value(p, weights, injury_penalty) for p in [x for x in rec_b_players if x])

    return {
        "team_a": {"pre_trade_value": pre_a, "post_trade_value": post_a, "delta": post_a - pre_a},
        "team_b": {"pre_trade_value": pre_b, "post_trade_value": post_b, "delta": post_b - pre_b},
    }


__all__ = ["compute_player_trade_value", "evaluate_trade"]

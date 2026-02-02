from typing import List, Dict, Optional


def get_all_players(league) -> List:
    players = []
    seen = set()
    for team in league.teams:
        for p in getattr(team, "roster", []):
            pid = getattr(p, "playerId", None) or getattr(p, "id", None)
            if pid and pid not in seen:
                seen.add(pid)
                players.append(p)
    return players


def _safe_get(p, attr, default=None):
    return getattr(p, attr, default)


def generate_player_rankings(league, by: str = "avg_points", position: Optional[str] = None,
                             top_n: Optional[int] = None, remaining_games: Optional[int] = None) -> List[Dict]:
    players = get_all_players(league)
    if position:
        players = [p for p in players if _safe_get(p, "position") == position]
    results = []
    for p in players:
        results.append({
            "playerId": getattr(p, "playerId", None) or getattr(p, "id", None),
            "name": getattr(p, "name", None),
            "position": getattr(p, "position", None),
            "proTeam": getattr(p, "proTeam", None) or getattr(p, "team", None),
            "posRank": getattr(p, "posRank", None),
            "avg_points": _safe_get(p, "avg_points"),
            "projected_avg_points": _safe_get(p, "projected_avg_points"),
            "total_points": _safe_get(p, "total_points") or _safe_get(p, "points", None),
            "projected_total_points": _safe_get(p, "projected_total_points"),
            "games_played": _safe_get(p, "games_played") or _safe_get(p, "gamesPlayed")
        })
    def _sort_key(x):
        return x["avg_points"] if x["avg_points"] is not None else (x["projected_avg_points"] or 0)
    results = sorted(results, key=_sort_key, reverse=True)
    if top_n:
        results = results[:top_n]
    return results


__all__ = ["get_all_players", "generate_player_rankings"]

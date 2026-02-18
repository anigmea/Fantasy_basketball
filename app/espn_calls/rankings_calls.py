from typing import List, Dict, Optional

# Collections
TEAM_PLAYER_COL = "team_players"
FREE_AGENTS_COL = "free_agents"


def get_all_players(db) -> List[Dict]:
    """Return all players from DB collections (team_players + free_agents)."""
    players = []
    if db is None:
        return players
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
    return players


def generate_player_rankings(db, by: str = "avg_points", position: Optional[str] = None,
                             top_n: Optional[int] = None, remaining_games: Optional[int] = None) -> List[Dict]:
    players = get_all_players(db)
    if position is not None:
        players = [p for p in players if p.get("position") == position]
    results = []
    for p in players:
        results.append({
            "playerId": p.get("playerId") or p.get("id"),
            "name": p.get("name"),
            "position": p.get("position"),
            "proTeam": p.get("proTeam") or p.get("team"),
            "posRank": p.get("posRank"),
            "avg_points": p.get("avg_points"),
            "projected_avg_points": p.get("projected_avg_points"),
            "total_points": p.get("total_points") or p.get("points"),
            "projected_total_points": p.get("projected_total_points"),
            "games_played": p.get("games_played") or p.get("gamesPlayed"),
        })

    def _sort_key(x):
        return x["avg_points"] if x["avg_points"] is not None else (x["projected_avg_points"] or 0)

    results = sorted(results, key=_sort_key, reverse=True)
    if top_n:
        results = results[:top_n]
    return results


__all__ = ["get_all_players", "generate_player_rankings"]

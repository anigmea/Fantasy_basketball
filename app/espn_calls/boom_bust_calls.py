from typing import Dict, List, Optional
from firebase_admin import firestore

# Collections
TEAM_PLAYER_COL = "team_players"
FREE_AGENTS_COL = "free_agents"

def compute_boom_score(player: Dict):
    '''Boom score = season-to-date avg minus project avg'''
    avg_points = player.get("avg_points")
    projected_avg = player.get("projected_avg_points")

    if avg_points is None or projected_avg is None:
        return None
    return avg_points - projected_avg


def get_boom_bust_players(db):
    '''Returns boom/bust data for players'''
    result = []

    # Team players
    for doc in db.collection(TEAM_PLAYER_COL).stream():
        p = doc.to_dict()
        score = compute_boom_score(p)
        if score is not None:
            result.append({
                "playerId": p.get("playerId"),
                "name": p.get("name"),
                "boom_score": score,
                "avg_points": p.get("avg_points"),
                "projected_avg_points": p.get("projected_avg_points"),
                "injured": p.get("injured"),
                "position": p.get("position")
            })

    # Free agents
    for doc in db.collection(FREE_AGENTS_COL).stream():
        p = doc.to_dict()
        score = compute_boom_score(p)
        if score is not None:
            result.append({
                "playerId": p.get("playerId"),
                "name": p.get("name"),
                "boom_score": score,
                "avg_points": p.get("avg_points"),
                "projected_avg_points": p.get("projected_avg_points"),
                "injured": p.get("injured"),
                "position": p.get("position"),
            })
    return result
    


__all__ = [
    "compute_boom_score",
    "get_boom_bust_players"
]
from typing import Optional

# Collections
TEAM_PLAYER_COL = "team_players"
FREE_AGENTS_COL = "free_agents"

def get_team_players(db):
    '''Returns all rostered players across the League'''
    q = db.collection(TEAM_PLAYER_COL)
    return [doc.to_dict() for doc in q.stream()]


def get_free_agents(db, position: Optional[str] = None, injured: Optional[bool] = None, limit: Optional[int] = None):
    '''Returns free agents, optionally filtered by position / injured flag'''
    q = db.collection(FREE_AGENTS_COL)

    if position is not None:
        q = q.where("position", "==", position)
    if injured is not None:
        q = q.where('injured', '==', injured)
    if limit is not None:
        q = q.limit(limit)
    
    return [doc.to_dict() for doc in q.stream()]


__all__ = [
    "get_team_players",
    "get_free_agents"
]
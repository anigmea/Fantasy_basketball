# Collections
TEAM_PLAYER_COL = "team_players"
FREE_AGENTS_COL = "free_agents"

def compute_boom_score(player):
    '''Boom score = season-to-date avg minus project avg'''
    avg_points = player.get("avg_points")
    projected_avg = player.get("projected_avg_points")

    if avg_points is None or projected_avg is None:
        return None
    return avg_points - projected_avg


def get_boom_bust_players(db, include_injured=True, year=2026, min_games=10):
    '''
    Returns:
        booms: list of players with boom_score > 0
        busts: list of players with boom_score < 0
    '''
    seen = set()
    booms = []
    busts = []

    def process(col_name):
        for doc in db.collection(col_name).stream():
            p = doc.to_dict()
            pid = p.get("playerId")
            if pid is None or pid in seen:
                continue
            seen.add(pid)

            if not include_injured and p.get("injured"):
                continue

            # min game filter
            season = p.get("stats", {}).get(f"{year}_total", {})
            total = season.get("total", {})
            gp = total.get("GP", 0)

            if gp < min_games:
                continue

            score = compute_boom_score(p)
            if score is None:
                continue

            player_entry = {
                "playerId": pid,
                "name": p.get("name"),
                "boom_score": score,
                "avg_points": p.get("avg_points"),
                "projected_avg_points": p.get("projected_avg_points"),
                "position": p.get("position")
            }

            if score > 0:
                booms.append(player_entry)
            elif score < 0:
                busts.append(player_entry)

    process(TEAM_PLAYER_COL)
    process(FREE_AGENTS_COL)

    booms.sort(key=lambda r: r["boom_score"], reverse=True)
    busts.sort(key=lambda r: r["boom_score"])
    return booms, busts
    


__all__ = [
    "compute_boom_score",
    "get_boom_bust_players"
]

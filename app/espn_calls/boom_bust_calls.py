def compute_boom_score(player):
    if player.avg_points is None or player.projected_avg_points is None:
        return None
    return player.avg_points - player.projected_avg_points

def get_boom_bust_players(league):
    players = []
    for team in league.teams:
        players.extend(team.roster)

    results = []
    for p in players:
        score = compute_boom_score(p)
        if score is not None:
            results.append({
                "playerId": p.playerId,
                "name": p.name,
                "boom_score": score,
                "avg_points": p.avg_points,
                "projected_avg_points": p.projected_avg_points,
            })
    return results

__all__ = [
    "compute_boom_score",
    "get_boom_bust_players"
]
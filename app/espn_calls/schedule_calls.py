from typing import List, Dict, Optional


def get_team_schedule(league, team_id: int, week: Optional[int] = None) -> List[Dict]:
    results = []
    try:
        sb = league.scoreboard(week=week)
    except Exception:
        return results
    for matchup in sb:
        try:
            home = getattr(matchup, "home_team", None) or getattr(matchup, "home", None)
            away = getattr(matchup, "away_team", None) or getattr(matchup, "away", None)
        except Exception:
            continue
        for team_obj, side, opp in ((home, "home", away), (away, "away", home)):
            if team_obj is None:
                continue
            tid = getattr(team_obj, "team_id", None) or getattr(team_obj, "teamId", None) or getattr(team_obj, "id", None)
            if tid == team_id:
                opp_id = getattr(opp, "team_id", None) or getattr(opp, "teamId", None) or getattr(opp, "id", None) if opp else None
                opp_name = getattr(opp, "team_name", None) or getattr(opp, "teamName", None) or getattr(opp, "name", None) if opp else None
                points_for = getattr(matchup, "home_score", None) if side == "home" else getattr(matchup, "away_score", None)
                points_against = getattr(matchup, "away_score", None) if side == "home" else getattr(matchup, "home_score", None)
                results.append({"team_id": tid, "team_name": getattr(team_obj, "team_name", None) or getattr(team_obj, "teamName", None) or getattr(team_obj, "name", None), "week": week, "opponent_id": opp_id, "opponent_name": opp_name, "home_away": side, "points_for": points_for, "points_against": points_against})
    return results


def get_games_left_in_week(league, week: int) -> Dict[int, int]:
    games_left = {}
    try:
        sb = league.scoreboard(week=week)
    except Exception:
        return games_left
    for matchup in sb:
        home_score = getattr(matchup, "home_score", None)
        away_score = getattr(matchup, "away_score", None)
        if home_score is None or away_score is None:
            home = getattr(matchup, "home_team", None) or getattr(matchup, "home", None)
            away = getattr(matchup, "away_team", None) or getattr(matchup, "away", None)
            home_id = getattr(home, "team_id", None) or getattr(home, "teamId", None) if home else None
            away_id = getattr(away, "team_id", None) or getattr(away, "teamId", None) if away else None
            if home_id:
                games_left[home_id] = games_left.get(home_id, 0) + 1
            if away_id:
                games_left[away_id] = games_left.get(away_id, 0) + 1
    return games_left


__all__ = ["get_team_schedule", "get_games_left_in_week"]

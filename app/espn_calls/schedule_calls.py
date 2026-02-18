from typing import List, Dict, Optional
from firebase_admin import firestore

# Collections
SCOREBOARD_COL = "scoreboard"


def get_team_schedule(db, team_id: int, week: Optional[int] = None) -> List[Dict]:
    """Return schedule for a team using a Firestore-like `db` collection named 'scoreboard'."""
    results = []
    if db is None:
        return results
    try:
        q = db.collection(SCOREBOARD_COL)
        docs = [doc.to_dict() for doc in q.stream()]
    except Exception:
        return results

    for matchup in docs:
        home = matchup.get("home_team") or matchup.get("home")
        away = matchup.get("away_team") or matchup.get("away")
        for team_obj, side, opp in ((home, "home", away), (away, "away", home)):
            if not team_obj:
                continue
            tid = team_obj.get("team_id") or team_obj.get("teamId") or team_obj.get("id")
            if tid == team_id:
                opp_id = opp.get("team_id") or opp.get("teamId") or opp.get("id") if opp else None
                opp_name = opp.get("team_name") or opp.get("teamName") or opp.get("name") if opp else None
                points_for = matchup.get("home_score") if side == "home" else matchup.get("away_score")
                points_against = matchup.get("away_score") if side == "home" else matchup.get("home_score")
                results.append({
                    "team_id": tid,
                    "team_name": team_obj.get("team_name") or team_obj.get("teamName") or team_obj.get("name"),
                    "week": week,
                    "opponent_id": opp_id,
                    "opponent_name": opp_name,
                    "home_away": side,
                    "points_for": points_for,
                    "points_against": points_against,
                })
    return results


def get_games_left_in_week(db, week: int) -> Dict[int, int]:
    games_left = {}
    if db is None:
        return games_left
    try:
        q = db.collection(SCOREBOARD_COL)
        docs = [doc.to_dict() for doc in q.stream()]
    except Exception:
        return games_left

    for matchup in docs:
        home_score = matchup.get("home_score")
        away_score = matchup.get("away_score")
        if home_score is None or away_score is None:
            home = matchup.get("home_team") or matchup.get("home")
            away = matchup.get("away_team") or matchup.get("away")
            home_id = home.get("team_id") or home.get("teamId") if home else None
            away_id = away.get("team_id") or away.get("teamId") if away else None
            if home_id:
                games_left[home_id] = games_left.get(home_id, 0) + 1
            if away_id:
                games_left[away_id] = games_left.get(away_id, 0) + 1
    return games_left


__all__ = ["get_team_schedule", "get_games_left_in_week"]

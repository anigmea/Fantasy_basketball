def get_roster(league, team_id):
    return league.teams[team_id].roster

def get_injured_players(league, team_id):
    roster = get_roster(league, team_id)
    return [p for p in roster if p.injured]

def get_free_agents(league, week=None, position=None):
    return league.free_agents(week=week, position=position)

def calculate_replacement_score() 

__all__ = [
    "get_roster",
    "get_injured_players",
    "get_free_agents"
]

# will work on this soon...

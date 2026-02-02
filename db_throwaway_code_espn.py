# Basketball API
from espn_api.basketball import League
from app import app
from app.espn_calls import *

league = League(league_id = app.config["LEAGUE_ID"], year = 2026, swid = app.config["SWID"], espn_s2 = app.config["ESPN_S2"])
print(get_boom_bust_players(league))

# Example usages of new helpers
try:
    print("Top 10 players by avg_points:")
    print(generate_player_rankings(league, by='avg_points', top_n=10))
except Exception as e:
    print("Error generating rankings:", e)

try:
    print("Games left in week 1:")
    print(get_games_left_in_week(league, week=1))
except Exception as e:
    print("Error getting schedule:", e)







































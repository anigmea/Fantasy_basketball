# Basketball API
from espn_api.basketball import League
from app import app

league = League(league_id = app.config["LEAGUE_ID"], year = 2026, swid = app.config["SWID"], espn_s2 = app.config["ESPN_S2"])
print(league)






































# Basketball API
from espn_api.basketball import League
from app import app
from app.espn_calls import *
import firebase_admin
from firebase_admin import credentials, firestore

# PLAYER CLASS 
# name: str
# playerId: int
# eligibleSlots = List[str]
# posRank: int # players positional rank
# acquisitionType: str
# proTeam: str
# position: str
# injuryStatus: str
# injured: boolean
# stats: dict # example {'2': {'team': 'NYK', 'date': datetime.datetime(2019, 4, 11, 0, 0), 'total': {'PTS': 20.0, 'BLK': 0.0, 'AST': 3.0}}}
# schedule: dict # key is scoring period, example: {'2': {'team': 'BKN', 'date': datetime.datetime(2018, 10, 17, 23, 0)}}
# lineupSlot: str # SG, C, PG, SF, IR
# total_points: int # players total points during the season
# avg_points: int # players average points during the season
# projected_total_points: int # projected player points for the season
# projected_avg_points: int # projected players average points for the season

# TEAM CLASS
# team_id: int
# team_abbrev: str
# team_name: str
# division_id: str
# division_name: str
# wins: int
# losses: int
# ties: int
# points_for: int # total points for through out the season
# points_against: int # total points against through out the season
# waiver_rank: int # waiver position
# acquisitions: int # number of acquisitions made by the team
# acquisition_budget_spent: int # budget spent on acquisitions 
# drops: int # number of drops made by the team
# trades: int # number of trades made by the team 
# move_to_ir: int # number of players move to ir
# owners: List[dict] # array of owner dict example: { id: '1234', displayName: 'team', firstName: 'Bob', lastName: 'Joe'} 
# # Note for owners name attributes will only be available for private leagues. Public leagues will not show name data.
# stats: dict # holds teams season long stats
# streak_type: str # string of either WIN or LOSS
# streak_length: int # how long the streak is for streak type
# standing: int # standing before playoffs
# final_standing: int # final standing at end of season
# draft_projected_rank: int # projected rank after draft
# playoff_pct: int # teams projected chance to make playoffs
# logo_url: str
# roster: List[Player]
# schedule: List[Team] # These 3 variables will have the same index and match on those indexes
# scores: List[int]
# outcomes: List[str]

league = League(league_id = app.config["LEAGUE_ID"], year = 2026, swid = app.config["SWID"], espn_s2 = app.config["ESPN_S2"])

teams = league.teams # length 12 [Team(NEW HORIZON 2), ..., Team(Divyansh's Daring Team)]
teams_for_db = []
players_for_db = []
free_agents_for_db = []

for team in teams: 
    for player in team.roster:
        players_for_db.append({'name': player.name, 'playerId': player.playerId, 'eligibleSlots':player.eligibleSlots, 'posRank':player.posRank,
                               'acquisitionType':player.acquisitionType, 'proTeam':player.proTeam, 'position':player.position, 'injuryStatus':player.injuryStatus,
                               'injured':player.injured, 'stats': player.stats, 'schedule':player.schedule, 'lineupSlot':player.lineupSlot,
                               'total_points':player.total_points, 'avg_points':player.avg_points, 'projected_total_points':player.projected_total_points,
                               'projected_avg_points':player.projected_avg_points})
        
    # account for free agents (players not on team)
    for player in league.free_agents():
        free_agents_for_db.append({'name': player.name, 'playerId': player.playerId, 'eligibleSlots':player.eligibleSlots, 'posRank':player.posRank,
                               'acquisitionType':player.acquisitionType, 'proTeam':player.proTeam, 'position':player.position, 'injuryStatus':player.injuryStatus,
                               'injured':player.injured, 'stats': player.stats, 'schedule':player.schedule, 'lineupSlot':player.lineupSlot,
                               'total_points':player.total_points, 'avg_points':player.avg_points, 'projected_total_points':player.projected_total_points,
                               'projected_avg_points':player.projected_avg_points})

    # roster and schedule must hold ids since firestore cannot hold python classes 
    # waiver_rank, move_to_ir, streak_type, streak_length, draft_projected_rank, playoff_pct, scores, and outcomes don't exist)
    # teams_for_db.append({'team_id': team.team_id, 'team_abbrev': team.team_abbrev, 'team_name':team.team_name, 'division_id':team.division_id, 'division_name':team.division_name,
    #                      'wins':team.wins, 'losses':team.losses, 'ties':team.ties, 'points_for':team.points_for, 'points_against':team.points_against, 
    #                      'acquisitions':team.acquisitions, 'acquisition_budget_spent':team.acquisition_budget_spent, 
    #                      'drops':team.drops, 'trades':team.trades, 'owners':team.owners, 'stats':team.stats,
    #                      'standing':team.standing, 'final_standing':team.final_standing,
    #                      'logo_url':team.logo_url, 'roster':[player.playerId for player in team.roster],
    #                      'schedule':[{'home_team':matchup.home_team, 'home_final_score':matchup.home_final_score, 'away_team':matchup.away_team,
    #                                   'away_final_score':matchup.away_final_score, 'winner':matchup.winner} for matchup in team.schedule]})
    
# [team_dummy.team_id for team_dummy in team.schedule.Team if team_dummy.team_id != team.team_id]

print(players_for_db[0], len(players_for_db), '\n')
print(free_agents_for_db[0], len(free_agents_for_db), '\n')
# print(teams_for_db[0], len(teams_for_db), '\n')

db = firestore.client()

# delete current player tables before pushing new data
def delete_collection(collection_ref, batch_size=500):
    docs = collection_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        delete_collection(collection_ref, batch_size)

delete_collection(db.collection("team_players"))
delete_collection(db.collection("free_agents"))

for player in players_for_db:
    doc_ref = db.collection('team_players').document()
    doc_ref.set(player)

for player in free_agents_for_db:
    doc_ref = db.collection('free_agents').document()
    doc_ref.set(player)

# DO NOT EXIT VSCODE OR CANCEL THE SCRIPT BEFORE YOU SEE THE MESSAGE
print('\n' + 'scraping complete')

# for team in teams_for_db:
#     doc_ref = db.collection('teams').document()
#     doc_ref.set(team)



































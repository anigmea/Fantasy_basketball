from app import app, db
from flask import jsonify, request
from app.espn_calls.boom_bust_calls import compute_boom_score
from app.espn_calls.rankings_calls import generate_player_rankings
from app.espn_calls.waiver_injury_calls import get_roster, get_free_agents, get_injured_players
from app.espn_calls.schedule_calls import get_team_schedule
from app.espn_calls.trade_calls import evaluate_trade

SWID = app.config["SWID"]
ESPN_S2 = app.config["ESPN_S2"]
LEAGUE_ID = app.config["LEAGUE_ID"]

# NOTE: Functions from espn_calls still need to be edited to accept the correct parameters based on updated pipelines/espn_calls

# ROUTE FOR PLAYER RANKINGS
@app.route('/api/players', methods=['GET'])
def get_players():
    # get all players from Firebase
    try:
        results = db.collection("Players").stream()
        players = [doc.to_dict() for doc in results]
        return jsonify({"success": True, "data": players}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/rankings', methods=['GET'])
def get_rankings():
    # generate player rankings
    try:
        rankings = generate_player_rankings(ESPN_S2, SWID, LEAGUE_ID)
        return jsonify({"success": True, "data": rankings}), 200 # 200 - success
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500 # 500 = server/code error

# ROUTE FOR PLAYER WAIVER/INJURY REPLACEMENT
@app.route('/api/replacements', methods=['POST'])
def replacements_api():
    # get replacement players for injured team members
    try:
        data = request.json
        team = data.get("team", [])
        
        if not team:
            return jsonify({"success": False, "error": "No team provided"}), 400 # 400 = bad request
        
        replacements = get_injured_players(team)
        return jsonify({"success": True, "data": replacements}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ROUTE FOR Boom/Bust
@app.route('/api/boombust', methods=['POST'])
def boombust():
    # analyze team boom/bust scores
    try:
        data = request.json
        team = data.get("team", [])
        
        if not team:
            return jsonify({"success": False, "error": "No team provided"}), 400
        
        results = compute_boom_score(ESPN_S2, LEAGUE_ID, team)
        return jsonify({"success": True, "data": results}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ROUTE FOR schedule tracker
@app.route('/api/schedule', methods=['GET'])
def schedule_api():
    """Get team schedules"""
    try:
        schedule = get_team_schedule(ESPN_S2, LEAGUE_ID)
        return jsonify({"success": True, "data": schedule}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ROUTE FOR trade analyzer
@app.route('/api/trade', methods=['POST'])
def trade_api():
    """Analyze a proposed trade"""
    try:
        data = request.json
        trade_info = data.get("trade", {})
        
        if not trade_info:
            return jsonify({"success": False, "error": "No trade info provided"}), 400
        
        analysis = evaluate_trade(trade_info)
        return jsonify({"success": True, "data": analysis}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy", "message": "Backend is running"}), 200
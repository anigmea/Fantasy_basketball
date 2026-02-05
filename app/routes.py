from app import app, db
from flask import jsonify, request
from espn_api.basketball import League
from app.espn_calls import (
    compute_boom_score,
    generate_player_rankings,
    get_injured_players,
    _get_player_by_id,
    compute_player_trade_value,
    get_team_schedule,
    evaluate_trade
)

# Load ESPN credentials from config
SWID = app.config["SWID"]
ESPN_S2 = app.config["ESPN_S2"]
LEAGUE_ID = app.config["LEAGUE_ID"]

# league python object for espn_calls
league = League(
    league_id=LEAGUE_ID,
    year=2026,
    espn_s2=ESPN_S2,
    swid=SWID
)

# NOTE: Functions from espn_calls still need to be edited to accept the correct parameters based on updated pipelines/espn_calls

# ROUTE FOR PLAYER RANKINGS
@app.route('/api/players', methods=['GET'])
def get_players():
    try:
        # get team players from Firestore
        team_players = db.collection("team_players").limit(50).stream()
        
        # get free agents from Firestore
        free_agents = db.collection("free_agents").limit(50).stream()
        
        # convert to list of dicts
        team_players = [doc.to_dict() for doc in team_players]
        free_agents = [doc.to_dict() for doc in free_agents]
        
        # return JSON for front end to call & access
        return jsonify({
            "team_players": team_players,
            "free_agents": free_agents
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in rankings endpoint: {str(e)}")
        return jsonify({"error": "Failed to fetch rankings"}), 500

@app.route("/api/rankings", methods=["GET"])
def rankings():

    position = request.args.get("position")
    top_n = request.args.get("top_n", type=int)

    results = generate_player_rankings(
        league,
        position=position,
        top_n=top_n
    )

    return jsonify(results), 200


# ROUTE FOR PLAYER WAIVER/INJURY REPLACEMENT
@app.route('/api/replacements', methods=['POST'])
def replacements_api():
 
    # get injured players and potential replacements (free agents) for a team.
    # TEMPORARY
    try:
        # TODO: replace the following with actual logic once waiver/injury functions are ready
        data = request.json
        team_id = data.get("team_id") if data else None

        # TEMPORARY: Return template response
        template_response = {
            "success": True,
            "injured_players": [],
            "free_agents": []
        }

        return jsonify(template_response), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



# ROUTE FOR Boom/Bust
@app.route('/api/boombust', methods=['POST'])
def boombust():
    # analyze team boom/bust scores
    try:
        # NOTE: STILL NEED TO EDIT BASED ON OUR BOOM BUST FUNCTION
        results = compute_boom_score(league)
        return jsonify(results), 200
        
    except Exception as e:
        app.logger.error(f"Error in boombust endpoint: {str(e)}")
        return jsonify({"error": "Failed to fetch boom/bust data", "details": str(e)}), 500


# ROUTE FOR schedule tracker
@app.route('/api/schedule', methods=['GET'])
def schedule_api():
    """Get team schedules"""
    try:
        team_id = request.args.get("team_id") # get team_id from front-end request

        schedule = get_team_schedule(league, team_id)
        return jsonify({"success": True, "data": schedule}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ROUTE FOR compute player trade value
@app.route("/api/player_trade_value", methods=["GET"])
def player_value():
    player_id = request.args.get("player_id", type=int)
    # league_id = request.args.get("league_id")  # might be used in production

    if not player_id:
        return jsonify({"success": False, "error": "Missing player_id"}), 400

    # league_obj = get_league(league_id) # in production, we would fetch the league based on league_id which is sent from front-end. (or would league id already be store in firebase ?)
    player = _get_player_by_id(league, player_id) # takes in player_id from front-end
    if not player:
        return jsonify({"success": False, "error": "Player not found"}), 404

    value = compute_player_trade_value(player)
    return jsonify({"success": True, "player_id": player_id, "trade_value": value}), 200


# ROUTE FOR trade analyzer
@app.route("/api/trade", methods=["POST"])
def trade_api():
    # analyze multi-player trade between two teams
    data = request.json # this is what front-end will send over when calling endpoint
    league_id = data.get("league_id")
    # league_obj = get_league(league_id) # use for production possibly

    try:
        # pass on the necessary data to evaluate_trade function
        analysis = evaluate_trade(
            league,
            team_a_id = data["team_a_id"],
            give_a_ids = data["give_a_ids"],
            receive_a_ids = data["receive_a_ids"],
            team_b_id = data["team_b_id"],
            give_b_ids = data["give_b_ids"],
            receive_b_ids = data["receive_b_ids"]
        )
        return jsonify({"success": True, "data": analysis}), 200
    except KeyError as e:
        return jsonify({"success": False, "error": f"Missing key {e}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    # simple health check endpoint
    return jsonify({"status": "healthy", "message": "Backend is running"}), 200
from app import app # import the app VARIABLE from the app MODULE/FILE
from app.forms import SearchForm
from app import db
from flask import flash, redirect, url_for # Important for user navigation
from flask import render_template # import the render_template() function to use the template from the index.html file in the templates folder
from flask import request # Flask provides a request variable that contains all the information that the client sent with the request (send user to the page they originally requested after they log in)
from urllib.parse import urlsplit # A function that parses a URL and has a .netloc component that reveals if the url is a relative path within the app or includes an outside domain name, which is dangerous and should be ignored
from app.espn_calls.boom_bust_calls import get_boom_bust_players
from app.models.waiver_regression import load_training_data, train_model, recommend_replacements_by_name
from app.espn_calls.rankings_calls import generate_player_rankings
from app.espn_calls.trade_calls import evaluate_trade
from app.espn_calls.schedule_calls import get_team_schedule, get_games_left_in_week
from datetime import datetime, timedelta, timezone


# Helper functions
def _parse_iso(dt_str):
    return datetime.fromisoformat(dt_str)

def _normalize_name(s):
    if not isinstance(s, str):
        return ""
    return s.strip().lower()

def _find_player_by_name_in_db(db, name):
    q = _normalize_name(name)
    if not q:
        return None
    
    for col in ("team_players", "free_agents"):
        for doc in db.collection(col).stream():
            p = doc.to_dict()
            pname = _normalize_name(p.get("name"))
            if pname and q in pname:
                return p
    return None


# ROUTE FOR PLAYER RANKINGS
@app.route('/', methods=['GET', 'POST']) # these decorators make the function below a "view function."
@app.route('/index', methods=['GET', 'POST']) # When a browser requests either of these 2 URLs Flask will return the result of this function as a response (just a print statement)
def index(): # this is a view function mapped to one or more route URLs so Flask knows what logic to execute when a client requests a given URL
    form = SearchForm()
    if form.validate_on_submit(): 
        # call database for user search here
        return redirect(url_for('index')) # refresh application to show changes (we ain't using websockets) (this will also have to take parameter)
    
    rankings = []
    err = None
    position = request.args.get("position")
    top_n = request.args.get("top_n")

    try:
        rankings = generate_player_rankings(
            db,
            by="avg_points",
            position=position if position else None,
            top_n=int(top_n) if top_n else 50
        )
    except Exception as e:
        err = str(e)

    return render_template('index.html', title='Player Rankings', form=form, rankings=rankings, err=err)

# ROUTE FOR PLAYER WAIVER/INJURY REPLACEMENT
@app.route('/replacements', methods=['GET', 'POST'])
def replacements():
    form = SearchForm()
    replacements = []
    err = None

    if form.validate_on_submit(): 
        # call database for user search here
        player_name = form.search.data

        try:
            X, y = load_training_data(db)
            model, metrics = train_model(X, y)

            recs, err = recommend_replacements_by_name(
                db,
                model,
                player_name=player_name,
                games_remaining=3,
                top_n=50,
                include_injured=False
            )
            replacements = recs

        except Exception as e:
            err = str(e)


    return render_template('replacements.html', title='Replacements', form=form, replacements=replacements, err=err) 

# ROUTE FOR Boom/bust
@app.route('/boombust', methods=['GET', 'POST'])
def boombust():
    form = SearchForm()
    if form.validate_on_submit(): 
        # call database for user search here
        return redirect(url_for('boombust'))

    include_injured = True
    year = 2026
    min_games = 10

    booms = []
    busts = []
    err = None

    try:
        booms, busts = get_boom_bust_players(
            db,
            include_injured=include_injured,
            year=year,
            min_games=min_games
        )
    except Exception as e:
        err = str(e)

    return render_template('boombust.html', title='Boom/Bust', form=form, booms=booms, busts=busts, err=err)

# ROUTE FOR schedule tracker
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    form = SearchForm()
    games = []
    err = None
    player = None

    if form.validate_on_submit(): 
        player_name = form.search.data
        try:
            player = _find_player_by_name_in_db(db, player_name)
            if not player:
                err = f"Player not found: {player_name}"
            else:
                sched = player.get("schedule") or {}
                rows = []
                for game_id, info in sched.items():
                    dt_str = info.get("date")
                    opp = info.get("team")
                    if not dt_str:
                        continue
                    try:
                        dt = _parse_iso(dt_str)
                    except Exception:
                        continue
                    rows.append({
                        "game_id": game_id,
                        "date": dt,
                        "opponent": opp
                    })
                rows.sort(key=lambda r: r["date"])

                now = datetime.now()
                end = now + timedelta(days = 7)
                games = [r for r in rows if now <= r["date"] <= end]

        except Exception as e:
            err = str(e)

    return render_template('schedule.html', title='Schedule', form=form, player=player, games=games, err=err)

# ROUTE FOR trade analyzer
@app.route('/trade', methods=['GET', 'POST'])
def trade():
    err = None
    result = None
    score = None
    winner = None

    if request.method == "POST":
        left_name = request.form.get("left_player")
        right_name = request.form.get("right_player")

        left_p = _find_player_by_name_in_db(db, left_name)
        right_p = _find_player_by_name_in_db(db, right_name)

        if left_p is None or right_p is None:
            missing = []
            if left_p is None: missing.append(left_name or "(left player)")
            if right_p is None: missing.append(right_name or "(right player)")
            err = f"Player(s) not found: {', '.join(missing)}"
        else:
            left_id = left_p.get("playerId") or left_p.get("id")
            right_id = right_p.get("playerId") or right_p.get("id")

            result = evaluate_trade(
                db,
                give_a_ids=[left_id], receive_a_ids=[right_id],
                give_b_ids=[right_id], receive_b_ids=[left_id]
            )

            score = float(result["team_a"]["delta"] - result["team_b"]["delta"])
            winner = "Team A" if score > 0 else ("Team B" if score < 0 else "Even")

    return render_template('trade.html', title='Trades', err=err, result=result, score=score, winner=winner)
























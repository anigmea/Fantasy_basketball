from app import app # import the app VARIABLE from the app MODULE/FILE
from app.forms import SearchForm
from app import db
from flask import redirect, url_for # Important for user navigation
from flask import render_template # import the render_template() function to use the template from the index.html file in the templates folder
from flask import request # Flask provides a request variable that contains all the information that the client sent with the request
from urllib.parse import urlsplit # A function that parses a URL — .netloc reveals if the url is relative (safe) or includes an outside domain (dangerous, should be ignored)
from app.espn_calls.boom_bust_calls import get_boom_bust_players
from app.models.waiver_regression import (
    load_training_data,
    train_model,
    recommend_replacements_by_name,
    get_injured_players,
    find_player_by_name,
)
from app.espn_calls.rankings_calls import generate_player_rankings
from app.espn_calls.trade_calls import evaluate_trade
from app.espn_calls.schedule_calls import get_team_schedule, get_games_left_in_week
from datetime import datetime, timedelta


# HELPER FUNCTIONS

def _parse_iso(dt_str):
    # Parse an ISO 8601 date string (e.g. "2026-02-25T19:30:00") into a datetime object
    return datetime.fromisoformat(dt_str)


def _normalize_name(s):
    # Lowercase + strip whitespace so name lookups are case-insensitive
    if not isinstance(s, str):
        return ""
    return s.strip().lower()


def _find_player_by_name_in_db(db, name):
    # Search both team_players and free_agents for a player whose name contains the query
    # Returns the first matching player dict, or None if not found
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


def _find_player_id(db, name):
    # Wrapper around _find_player_by_name_in_db that also returns the player's ID
    # Returns (player_dict, player_id) or (None, None) if not found
    p = _find_player_by_name_in_db(db, name)
    if p is None:
        return None, None
    return p, p.get("playerId") or p.get("id")


def _build_team_schedule_grid(db):
    # Build a per-NBA-team schedule summary by reading player schedule data from Firestore.
    #
    # Each player doc has a "schedule" field structured like:
    #   { "game_123": { "date": "2026-02-25T19:30:00", "team": "LAL" }, ... }
    #
    # KEY FIX: We deduplicate by game_id across ALL players on a team so each game
    # is counted exactly once — without this, a team with 10 rostered players would
    # count the same Tuesday game 10 times (once per player doc).
    #
    # We also scan BOTH team_players and free_agents since NBA pro teams appear in both.
    #
    # Returns a list sorted by week_games descending:
    #   [{ name, abbr, week_games, month_games, season_games, week_opponents }, ...]

    now   = datetime.now()
    week  = now + timedelta(days=7)
    month = now + timedelta(days=30)

    # team_name -> { game_id -> { date: datetime, opp: str } }
    # Outer dict keyed by team name; inner dict keyed by game_id for deduplication
    team_games = {}

    for col in ("team_players", "free_agents"):
        # Scan both collections — NBA teams appear in both (rostered players + available free agents)
        try:
            for doc in db.collection(col).stream():
                p = doc.to_dict()
                team_name = p.get("proTeam") or p.get("team") or ""
                if not team_name:
                    continue

                sched = p.get("schedule") or {}

                if team_name not in team_games:
                    team_games[team_name] = {}

                for game_id, info in sched.items():
                    if game_id in team_games[team_name]:
                        continue  # already recorded this game for this team — skip duplicate

                    dt_str = info.get("date")
                    if not dt_str:
                        continue
                    try:
                        dt = _parse_iso(dt_str)
                    except Exception:
                        continue  # skip any malformed date strings

                    opp = info.get("team") or info.get("opponent") or ""
                    team_games[team_name][game_id] = {"date": dt, "opp": opp}

        except Exception:
            continue  # if one collection fails don't block the other

    # Roll up per-game records into week / month / season counts for each team
    result = []
    for team_name, games_by_id in team_games.items():
        week_cnt   = 0
        month_cnt  = 0
        season_cnt = 0
        week_opps  = []

        for game_id, g in games_by_id.items():
            dt  = g["date"]
            opp = g["opp"]

            if dt < now:
                continue  # past game — don't count it

            season_cnt += 1

            if dt <= month:
                month_cnt += 1

            if dt <= week:
                week_cnt += 1
                if opp:
                    week_opps.append(opp)

        result.append({
            "name":           team_name,
            "abbr":           team_name[:3].upper(),  # rough abbreviation — swap with a lookup dict if needed
            "week_games":     week_cnt,
            "month_games":    month_cnt,
            "season_games":   season_cnt,
            "week_opponents": list(set(week_opps)),  # deduplicate in case any opp appeared twice
        })

    # Sort by games this week descending so best schedule targets appear first in the grid
    result.sort(key=lambda t: t["week_games"], reverse=True)
    return result


# PLAYER RANKINGS
@app.route('/', methods=['GET', 'POST']) # these decorators make the function below a "view function"
@app.route('/index', methods=['GET', 'POST']) # when a browser requests either of these 2 URLs Flask will return the result of this function as a response
def index(): # view function mapped to one or more route URLs so Flask knows what logic to execute when a client requests a given URL
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('index')) # refresh application to show changes (we ain't using websockets)

    rankings = []
    err      = None
    position = request.args.get("position") # optional ?position=PG filter from URL
    top_n    = request.args.get("top_n")    # optional ?top_n=25 filter from URL

    try:
        rankings = generate_player_rankings(
            db,
            by="avg_points",
            position=position if position else None,
            top_n=int(top_n) if top_n else 50,
        )
    except Exception as e:
        err = str(e)

    return render_template('index.html', title='Player Rankings', form=form, rankings=rankings, err=err)


# PLAYER WAIVER / INJURY REPLACEMENT
@app.route('/replacements', methods=['GET', 'POST'])
def replacements():
    form          = SearchForm()
    repl_list     = []
    err           = None
    target_player = None

    # Always fetch injured players on page load so the browse tab is populated
    # regardless of whether the user has searched for a specific player yet
    try:
        injured_players = get_injured_players(db)
    except Exception as e:
        injured_players = []
        err = str(e)

    if form.validate_on_submit():
        player_name = form.search.data

        try:
            # Fetch the target player's card data to display above the results table
            target_raw = find_player_by_name(db, player_name)
            if target_raw:
                target_player = {
                    "name":                 target_raw.get("name"),
                    "position":             target_raw.get("position"),
                    "proTeam":              target_raw.get("proTeam") or target_raw.get("team"),
                    "avg_points":           target_raw.get("avg_points"),
                    "projected_avg_points": target_raw.get("projected_avg_points"),
                }

            # Train the regression model on the fly using all player data in Firestore
            # (features: projected_avg_points, posRank, injured → target: avg_points)
            X, y = load_training_data(db)
            model, metrics = train_model(X, y)

            # Get top-N position-compatible replacements sorted by predicted PPG
            # Exact position matches are ranked above flex-compatible alternatives
            recs, err = recommend_replacements_by_name(
                db,
                model,
                player_name=player_name,
                games_remaining=3,
                top_n=50,
                include_injured=False, # don't recommend other injured players as replacements
            )
            repl_list = recs

        except Exception as e:
            err = str(e)

    return render_template(
        'replacements.html',
        title='Replacements',
        form=form,
        replacements=repl_list,
        injured_players=injured_players,
        target_player=target_player,
        err=err,
    )


# ROUTE FOR BOOM / BUST
@app.route('/boombust', methods=['GET', 'POST'])
def boombust():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('boombust'))

    include_injured = True  # include injured players in boom/bust analysis
    year            = 2026
    min_games       = 10    # minimum games played to qualify (filters out tiny sample sizes)

    booms = []
    busts = []
    err   = None

    try:
        booms, busts = get_boom_bust_players(
            db,
            include_injured=include_injured,
            year=year,
            min_games=min_games,
        )
    except Exception as e:
        err = str(e)

    return render_template('boombust.html', title='Boom/Bust', form=form, booms=booms, busts=busts, err=err)


# SCHEDULE TRACKER
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    form   = SearchForm()
    games  = []
    err    = None
    player = None

    # Build the team grid on every page load — aggregates unique game counts per NBA team
    # from player schedule data in Firestore (team_players + free_agents).
    # grid_err is passed separately so a grid failure doesn't suppress the player search error
    team_schedule = []
    grid_err      = None
    try:
        team_schedule = _build_team_schedule_grid(db)
    except Exception as e:
        grid_err = str(e)

    # Handle player name search submitted from the search form (POST only)
    if form.validate_on_submit():
        player_name = form.search.data
        try:
            player = _find_player_by_name_in_db(db, player_name)
            if not player:
                err = f"Player not found: {player_name}"
            else:
                # Pull the player's schedule dict and filter to games in the next 7 days
                sched = player.get("schedule") or {}
                rows  = []
                for game_id, info in sched.items():
                    dt_str = info.get("date")
                    opp    = info.get("team") or info.get("opponent")
                    if not dt_str:
                        continue
                    try:
                        dt = _parse_iso(dt_str)
                    except Exception:
                        continue
                    rows.append({"game_id": game_id, "date": dt, "opponent": opp})

                rows.sort(key=lambda r: r["date"])

                now  = datetime.now()
                end  = now + timedelta(days=7)
                games = [r for r in rows if now <= r["date"] <= end] # only games within the next 7 days

        except Exception as e:
            err = str(e)

    return render_template(
        'schedule.html',
        title='Schedule',
        form=form,
        player=player,
        games=games,
        team_schedule=team_schedule,
        grid_err=grid_err,
        err=err,
    )


# TRADE ANALYZER
@app.route('/trade', methods=['GET', 'POST'])
def trade():
    err    = None
    result = None
    score  = None
    winner = None

    if request.method == "POST":
        # Collect up to 4 player names per side from the form inputs
        # Empty slots are simply ignored — 1v1, 2v1, 3v2, 4v4 etc. all work
        give_names = []
        recv_names = []
        for i in range(4):
            g = (request.form.get(f"give_player_{i}") or "").strip()
            r = (request.form.get(f"receive_player_{i}") or "").strip()
            if g:
                give_names.append(g)
            if r:
                recv_names.append(r)

        if not give_names or not recv_names:
            err = "Please enter at least one player on each side."
        else:
            # Resolve player names -> player IDs for the trade evaluator
            give_ids  = []
            recv_ids  = []
            not_found = []

            for name in give_names:
                p, pid = _find_player_id(db, name)
                if pid is None:
                    not_found.append(name)
                else:
                    give_ids.append(pid)

            for name in recv_names:
                p, pid = _find_player_id(db, name)
                if pid is None:
                    not_found.append(name)
                else:
                    recv_ids.append(pid)

            if not_found:
                err = f"Player(s) not found: {', '.join(not_found)}"
            else:
                try:
                    # evaluate_trade handles imbalance weighting internally:
                    # if sides have different player counts, the extra players on the
                    # larger side are discounted to penalize lopsided trades
                    result = evaluate_trade(db, give_ids=give_ids, recv_ids=recv_ids)
                    score  = float(result["score"])
                    winner = "You" if score > 0 else ("Them" if score < 0 else "Even")
                except Exception as e:
                    err = str(e)

    return render_template(
        'trade.html',
        title='Trade Analyzer',
        err=err,
        result=result,
        score=score,
        winner=winner,
    )
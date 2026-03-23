import numpy as np
from sklearn.linear_model import LinearRegression

# Collection Names
TEAM_PLAYERS_COL = "team_players"
FREE_AGENTS_COL = "free_agents"

# -----------------------------
# Step 1: Load All Player Data
# -----------------------------
def load_all_players(db):
    players = []
    # We pool everyone to train the volatility model correctly
    for collection in [TEAM_PLAYERS_COL, FREE_AGENTS_COL]:
        docs = db.collection(collection).stream()
        for doc in docs:
            p = doc.to_dict()
            p["id"] = doc.id
            players.append(p)
    return players

# -----------------------------
# Step 2: Train Volatility Model
# -----------------------------
def train_volatility_model(players):
    X, y = [], []
    for p in players:
        try:
            # We use the gap between actual avg and projected avg to guess 'swing'
            mean = float(p.get("avg_points", 0))
            proj = float(p.get("projected_avg_points", mean))
            if mean <= 0: continue
            
            deviation = abs(proj - mean)
            X.append([mean])
            y.append(deviation)
        except (ValueError, TypeError):
            continue

    if len(X) < 10:
        raise ValueError("Not enough player data to train volatility model.")

    model = LinearRegression()
    model.fit(X, y)
    return model

# -----------------------------
# Step 3: Estimate Player Std Dev
# -----------------------------
def estimate_std(mean, volatility_model):
    # Predicts how much a player's score typically varies based on their average
    pred_dev = volatility_model.predict([[mean]])[0]
    std = np.sqrt(2) * abs(pred_dev)
    return max(std, 2.0) # Floor of 2.0 to avoid zero-variance errors

# -----------------------------
# Step 4: Calculate Replacement Level
# -----------------------------
def get_replacement_value(db, volatility_model):
    """
    Finds the average value of the top 10 available Free Agents.
    This represents the 'Waiver Wire' player you pick up in a 2-for-1 trade.
    """
    docs = (db.collection(FREE_AGENTS_COL)
            .order_by("projected_avg_points", direction="DESCENDING")
            .limit(10)
            .stream())
    
    top_fa_means = []
    for doc in docs:
        p = doc.to_dict()
        top_fa_means.append(float(p.get("projected_avg_points", 0)))
    
    if not top_fa_means:
        return 0.0, 5.0 # Fallback if DB is empty
        
    rep_mean = np.mean(top_fa_means)
    rep_std = estimate_std(rep_mean, volatility_model)
    return rep_mean, rep_std

# -----------------------------
# Step 5: Get Individual Player Projection
# -----------------------------
def get_player_projection(db, player_id):
    # Search both collections for the player
    doc = db.collection(TEAM_PLAYERS_COL).document(player_id).get()
    if not doc.exists:
        doc = db.collection(FREE_AGENTS_COL).document(player_id).get()
        if not doc.exists:
            raise ValueError(f"Player {player_id} not found in DB.")

    p = doc.to_dict()
    mean = float(p.get("projected_avg_points", p.get("avg_points", 0)))
    
    # 15% 'Availability' tax for injured players
    if p.get("injured", False):
        mean *= 0.85 

    return mean

# -----------------------------
# Step 6: Simulate Trade
# -----------------------------
def simulate_trade(db, players_out_ids, players_in_ids, simulations=10000):
    # 1. Setup Models
    all_players = load_all_players(db)
    vol_model = train_volatility_model(all_players)
    rep_mean, rep_std = get_replacement_value(db, vol_model)

    out_means, out_stds = [], []
    in_means, in_stds = [], []

    # 2. Extract Data for Real Players
    for pid in players_out_ids:
        m = get_player_projection(db, pid)
        out_means.append(m)
        out_stds.append(estimate_std(m, vol_model))

    for pid in players_in_ids:
        m = get_player_projection(db, pid)
        in_means.append(m)
        in_stds.append(estimate_std(m, vol_model))

    # 3. BALANCE ROSTERS (The 2-for-1 Logic)
    # If I give 2 and get 1, I gain a roster spot to fill with a Free Agent.
    diff = len(players_out_ids) - len(players_in_ids)
    
    if diff > 0: # More players leaving than entering (Receiving side needs FA)
        for _ in range(diff):
            in_means.append(rep_mean)
            in_stds.append(rep_std)
    elif diff < 0: # More players entering than leaving (Sending side needs FA)
        for _ in range(abs(diff)):
            out_means.append(rep_mean)
            out_stds.append(rep_std)

    # 4. Monte Carlo Simulation
    # Generate (simulations x num_players) random points and sum each row
    out_sim = np.sum(np.random.normal(out_means, out_stds, (simulations, len(out_means))), axis=1)
    in_sim = np.sum(np.random.normal(in_means, in_stds, (simulations, len(in_means))), axis=1)

    diff_array = in_sim - out_sim

    return {
        "expected_out": round(float(np.mean(out_sim)), 2),
        "expected_in": round(float(np.mean(in_sim)), 2),
        "total_value_diff": round(float(np.mean(diff_array)), 2),
        "win_probability": round(float(np.mean(diff_array > 0)) * 100, 2), # Percentage
        "replacement_level_used": round(rep_mean, 2)
    }
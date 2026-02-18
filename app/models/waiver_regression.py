import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

TEAM_PLAYERS_COL = "team_players"
FREE_AGENTS_COL = "free_agents"

def _doc_to_row(p: dict):
  '''
  Converts Firestore player dict to (features, target) for regression

  Features (X):
  - projected_avg_points (float)
  - posRank (int)
  - injured (0/1)

  Target (y):
  - avg_points (float)
  '''
  x1 = p.get("projected_avg_points")
  x2 = p.get("posRank")
  x3 = p.get("injured")
  y = p.get("avg_points")

  # Drop rows with missing values
  if y is None or x1 is None or x2 is None or x3 is None:
    return None
  
  # Convert injured bool -> 0/1
  injured_num = 1 if x3 else 0

  try:
    X = [float(x1), float(x2), float(injured_num)]
    Y = float(y)
  except (TypeError, ValueError):
    return None
  
  return X, Y


def load_training_data(db):
  '''
  Loads training data from Firestore (team_players + free_agents)

  Returns:
  X: shape (n_samples, 3)
  y: shape (n_samples,)
  '''
  X_rows = []
  y_vals = []

  # team_players
  for doc in db.collection(TEAM_PLAYERS_COL).stream():
    row = _doc_to_row(doc.to_dict())
    if row is None:
      continue
    X, y = row
    X_rows.append(X)
    y_vals.append(y)
  
  # free agents
  for doc in db.collection(FREE_AGENTS_COL).stream():
    row = _doc_to_row(doc.to_dict())
    if row is None:
      continue
    X, y = row
    X_rows.append(X)
    y_vals.append(y)

  return np.array(X_rows, dtype = float), np.array(y_vals, dtype = float)


def train_model(X, y, test_size=0.2, random_state=42):
  '''
  Train a basic Linear Regression model
  Returns:
    model: trained LinearRegression
    metrics: dict with simple evaluation outputs
  '''
  X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, random_state=random_state
  )

  model = LinearRegression()
  model.fit(X_train, y_train)

  r2_train = model.score(X_train, y_train)
  r2_test = model.score(X_test, y_test)

  metrics = {
    "n_samples": len(y),
    "n_features": X.shape[1],
    "r2_train": float(r2_train),
    "r2_test": float(r2_test),
    "coef": model.coef_.tolist(),
    "intercept": float(model.intercept_),
    "feature_order": ["projected_avg_points", "posRank", "injured"]
  }
  return model, metrics


def recommend_best_players(db, model, games_remaining=3, top_n=25, include_injured=False):
  '''Returns top players across team_players + free_agents, ranked by expected points for the rest of the week'''

  seen = set()
  results = []

  def process_collection(col_name):
    for doc in db.collection(col_name).stream():
      p = doc.to_dict()
      pid = p.get("playerId")
      if pid is None or pid in seen:
        continue
      seen.add(pid)

      if not include_injured and p.get("injured"):
        continue

      x1  = p.get("projected_avg_points")
      x2 = p.get("posRank")
      x3 = p.get("injured")
      if x1 is None or x2 is None or x3 is None:
        continue

      injured_num = 1 if x3 else 0
      try:
        X_row = [[float(x1), float(x2), float(injured_num)]]
      except (TypeError, ValueError):
        continue

      pred_ppg = float(model.predict(X_row)[0])
      results.append({
        "playerId": pid,
        "name": p.get("name"),
        "position": p.get("position"),
        "injured": p.get("injured"),
        "predicted_ppg": pred_ppg,
        "games_remaining": games_remaining,
        "expected_week_points": pred_ppg * games_remaining
      })

  process_collection(FREE_AGENTS_COL)
  process_collection(TEAM_PLAYERS_COL)

  results.sort(key=lambda r: r["expected_week_points"], reverse=True)
  return results[:top_n]


def find_player_by_name(db, name):
  '''Search player by name across both collections; returns a player dict or None'''
  query = (name or "").strip().lower()
  if not query:
    return None

  for col in (TEAM_PLAYERS_COL, FREE_AGENTS_COL):
    for doc in db.collection(col).stream():
      p = doc.to_dict()
      pname = (p.get("name") or "").lower()
      if query in pname:
        return p

  return None

def recommend_replacements_by_name(db, model, player_name, games_remaining=3, top_n=25, include_injured=False):
  '''
  Feature flow:
  1) user enters player name
  2) we return top-N players from the overall NBA pool
  '''
  target = find_player_by_name(db, player_name)

  if target is None:
    return [], f"Player not found for name: {player_name}"

  recs = recommend_best_players(db, model, games_remaining=games_remaining, top_n=top_n, include_injured=include_injured)

  target_id = target.get("playerId")
  if target_id is not None:
    recs = [r for r in recs if r.get("playerId") != target_id]

  return recs, None


__all__ = [
  "load_training_data",
  "train_model",
  "recommend_best_players",
  "find_player_by_name",
  "recommend_replacements_by_name",
]
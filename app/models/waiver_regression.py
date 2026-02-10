from firebase_admin import firestore
import numpy as np
from typing import List, Tuple
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
    X = [float(x1), float(x2), float(x3)]
    Y = float(y)
  except (TypeError, ValueError):
    return None
  
  return X, y


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

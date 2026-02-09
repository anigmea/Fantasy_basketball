from espn_api.basketball import League
import firebase_admin
from firebase_admin import firestore
import os
import logging
from datetime import datetime

# Initialize Firebase once
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

BATCH_SIZE = 25  # keep batches small to avoid "Transaction too big"


def serialize(obj):
    """Convert datetimes and nested objects into Firestore-safe data."""
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(v) for v in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def delete_collection(collection_ref, batch_size=500):
    """Iteratively delete a collection (Cloud-safe)."""
    while True:
        docs = list(collection_ref.limit(batch_size).stream())
        if not docs:
            break
        for doc in docs:
            doc.reference.delete()


def write_in_batches(collection_name, documents):
    """Write documents using safe Firestore batch sizes."""
    batch = db.batch()
    count = 0
    total_written = 0

    for doc in documents:
        ref = db.collection(collection_name).document()
        batch.set(ref, doc)
        count += 1

        if count == BATCH_SIZE:
            batch.commit()
            total_written += count
            batch = db.batch()
            count = 0

    if count > 0:
        batch.commit()
        total_written += count

    return total_written


def run_espn_job(request):
    """HTTP Cloud Function entry point (triggered by Cloud Scheduler)."""
    logging.info("Starting ESPN scrape job")

    try:
        league = League(
            league_id=os.environ["LEAGUE_ID"],
            year=2026,
            swid=os.environ["SWID"],
            espn_s2=os.environ["ESPN_S2"],
        )
    except Exception as e:
        logging.exception("Failed to initialize ESPN League")
        return f"Failed to initialize league: {e}", 500

    players_for_db = []
    free_agents_for_db = []

    # TEAM PLAYERS
    for team in league.teams:
        for player in team.roster:
            players_for_db.append({
                "name": player.name,
                "playerId": player.playerId,
                "eligibleSlots": player.eligibleSlots,
                "posRank": player.posRank,
                "acquisitionType": player.acquisitionType,
                "proTeam": player.proTeam,
                "position": player.position,
                "injuryStatus": player.injuryStatus,
                "injured": player.injured,
                "stats": serialize(player.stats),
                "schedule": serialize(player.schedule),
                "lineupSlot": player.lineupSlot,
                "total_points": player.total_points,
                "avg_points": player.avg_points,
                "projected_total_points": player.projected_total_points,
                "projected_avg_points": player.projected_avg_points,
            })

    # FREE AGENTS (IMPORTANT: only once)
    for player in league.free_agents():
        free_agents_for_db.append({
            "name": player.name,
            "playerId": player.playerId,
            "eligibleSlots": player.eligibleSlots,
            "posRank": player.posRank,
            "acquisitionType": player.acquisitionType,
            "proTeam": player.proTeam,
            "position": player.position,
            "injuryStatus": player.injuryStatus,
            "injured": player.injured,
            "stats": serialize(player.stats),
            "schedule": serialize(player.schedule),
            "lineupSlot": player.lineupSlot,
            "total_points": player.total_points,
            "avg_points": player.avg_points,
            "projected_total_points": player.projected_total_points,
            "projected_avg_points": player.projected_avg_points,
        })

    logging.info("Deleting old collections")

    delete_collection(db.collection("team_players"))
    delete_collection(db.collection("free_agents"))

    logging.info("Writing team players")
    team_players_written = write_in_batches(
        "team_players", players_for_db
    )

    logging.info("Writing free agents")
    free_agents_written = write_in_batches(
        "free_agents", free_agents_for_db
    )

    logging.info("ESPN scrape complete")

    return (
        f"ESPN scrape complete. "
        f"Team players written: {team_players_written}, "
        f"Free agents written: {free_agents_written}",
        200,
    )


# This code is not ran as part of the application. It exists only for reference.
# This code has been uploaded to a firebase function via command line.

# 1. cd espn_cron
# 2. gcloud init
# 3. gcloud projects add-iam-policy-binding PROJECT_ID --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" --role="roles/datastore.user"
# 4. gcloud functions deploy run_espn_job --runtime python311 --trigger-http --allow-unauthenticated --timeout=540s --set-env-vars LEAGUE_ID=123456,SWID=your_swid,ESPN_S2=your_cookie

# The firebase function is called by a cloud scheduler cron job every 11 days (0 0 1-31/11 * *).
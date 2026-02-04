# THIS IS AN EXAMPLE OF INTERACTING WITH THE FIRESTORE DATABASE AND PUSHING DATA TO IT
import firebase_admin
from firebase_admin import credentials, firestore
from app import app

# cred = credentials.Certificate(app.config["FIREBASE_CREDENTIALS"]) # THESE 2 LINES ONLY HAVE TO RUN ONCE APPARENTLY
# firebase_admin.initialize_app(cred) 
db = firestore.client()

# players = [
#     {'name': 'LeBron James'},
#     {'name': 'Michael Jordan'}
# ]

# for player in players:
#     doc_ref = db.collection('Players').document()
#     doc_ref.set(player)
#     print('Document ID:', doc_ref.id)

# results = (
#     db.collection("Players").stream()
# )
# players = [doc.to_dict() for doc in results]
# print(results)
# print(players)


def delete_collection(collection_ref, batch_size=500):
    docs = collection_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        delete_collection(collection_ref, batch_size)

# usage
delete_collection(db.collection("Players"))



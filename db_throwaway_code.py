# THIS IS AN EXAMPLE OF INTERACTING WITH THE FIRESTORE DATABASE AND PUSHING DATA TO IT
import firebase_admin
from firebase_admin import credentials, firestore
from app import app

cred = credentials.Certificate(app.config["FIREBASE_CREDENTIALS"])
firebase_admin.initialize_app(cred)
db = firestore.client()

# players = [
#     {'name': 'LeBron James'},
#     {'name': 'Michael Jordan'}
# ]

# for player in players:
#     doc_ref = db.collection('Players').document()
#     doc_ref.set(player)
#     print('Document ID:', doc_ref.id)

results = (
    db.collection("Players").stream()
)
players = [doc.to_dict() for doc in results]
print(results)
print(players)





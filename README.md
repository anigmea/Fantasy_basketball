To Host Application Locally: 

1. python -m venv venv (in vscode terminal)
2. venv/Scripts/Activate.ps1 (in powershell)
3. pip install -r requirements.txt
4. (create a file named .flaskenv in the root directory with FLASK_APP=fantasy.py inside)
5. (after being added to the firestore database, go to project settings -> service accounts -> click generate new private key, and copy absolute path of the json file. Do not put it in the same directory as this repo)
6. (create a .env file in the root directory of this repo with FIREBASE_CREDENTIALS="<path to your json file>" inside)
7. flask run (in powershell with venv activated)

TODO LIST: 

1. Create layout for website UI
2. Create html pages, 1 for each app deliverable (rankings, boom/bust, scheduling, trade, waiver & injury replacements), with a navigation bar on the left
3. Explore basketball data from ESPN and figure out which API routes to pull data from 
4. Set up a database on firebase, create tables to hold data of interest, then integrate the database with this application
5. Use GCP Cloud Scheduler OR GCP Cloud Composer to regularly scrape data from ESPN
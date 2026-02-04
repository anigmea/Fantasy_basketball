To Host Application Locally: 

1. python -m venv venv (in vscode terminal)
2. venv/Scripts/Activate.ps1 (in powershell) (source venv/bin/activate for mac)
3. pip install -r requirements.txt
4. (create a file named .flaskenv in the root directory with FLASK_APP=fantasy.py inside)
5. (after being added to the firestore database, go to project settings -> service accounts -> click generate new private key, and copy absolute path of the json file. Do not put it in the same directory as this repo)
6. (create a .env file in the root directory of this repo with FIREBASE_CREDENTIALS="path to your json file" inside)
7. (this step is optional, but if you want to experiment with espn API, ask for SWID, LEAGUE_ID, and ESPN_S2 and put these variables in the .env file as well)
8. flask run (in powershell with venv activated)

Hosting React App Locally:

1. Make sure Node.js v18+ installed
2. "cd client" -> "npm install"
3. Create .env.local file in client directory with the following:
    VITE_API_URL=http://localhost:5174/api
    VITE_API_BASE_URL=http://localhost:5000/api
    REACT_APP_FIREBASE_API_KEY=your_api_key_here
    REACT_APP_FIREBASE_AUTH_DOMAIN=your_auth_domain_here
    REACT_APP_FIREBASE_PROJECT_ID=your_project_id_here
4. Go to firebase project > project settings > general > your apps > and copy over "apiKey", "authDomain", and "projectId".
5. Run "npm run dev"

NOTE:
may need to replace all instances of "5174" with the matching port your using.

TODO LIST: 

1. Create layout for website UI
2. Create html pages, 1 for each app deliverable (rankings, boom/bust, scheduling, trade, waiver & injury replacements), with a navigation bar on the left
3. Explore basketball data from ESPN and figure out which API routes to pull data from 
4. Set up a database on firebase, create tables to hold data of interest, then integrate the database with this application
5. Use GCP Cloud Scheduler OR GCP Cloud Composer to regularly scrape data from ESPN
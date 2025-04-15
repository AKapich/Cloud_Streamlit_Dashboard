import psycopg2
import soccerdata as sd
from datetime import datetime
import logging
import pandas as pd
import numpy as np
import json
from pandas import DataFrame, concat

def clean_for_postgres(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    for col in cleaned.columns:
        # Convert booleans to integers
        if cleaned[col].dtype == bool:
            cleaned[col] = cleaned[col].astype(int)
        
        # Handle NaNs in numeric columns
        elif np.issubdtype(cleaned[col].dtype, np.number):
            cleaned[col] = cleaned[col].replace({np.nan: None})
        
        # Object columns (may contain strings, lists, dicts, or None)
        elif cleaned[col].dtype == object:
            cleaned[col] = cleaned[col].apply(lambda x: 
                None if pd.isna(x) or x == "NaN" 
                else json.dumps(x) if isinstance(x, (dict, list)) 
                else x
            )

    return cleaned

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Cloud SQL connection setup
def create_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="googlecloud-makeitloud",
        host="34.116.186.20",
        port="5432",
    )
    return conn

# Open connection to Cloud SQL
conn = create_connection()

# Fetch data from Cloud SQL (replace with actual query)
cursor = conn.cursor()
cursor.execute("SELECT * FROM schedule")
schedule = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
cursor.execute("SELECT * FROM events")
events = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

updated_schedule = DataFrame()

# Process the leagues
for league in [
    "ESP-La Liga",
    "ENG-Premier League",
    "FRA-Ligue 1",
    "GER-Bundesliga",
    "ITA-Serie A",
]:
    logger.info(f"Starting to process league: {league}")
    ws = sd.WhoScored(leagues=league, seasons=datetime.today().year - 1)
    new_schedule = ws.read_schedule()
    updated_schedule = concat([updated_schedule, new_schedule.reset_index()])

    new_matches = set(
        new_schedule[new_schedule["started_at_utc"].notna()]["game_id"]
    ) - set(events["game_id"])

    logger.info(f"Found {len(new_matches)} new matches for {league}")

    for match_id in [new_matches.pop()]:
        match_event_data = ws.read_events(match_id=match_id, output_fmt="events")
        match_event_data = match_event_data.reset_index()
        match_event_data = clean_for_postgres(match_event_data)
        
        # Insert match data into Cloud SQL
        columns = match_event_data.columns.tolist()
        insert_query = f"""
        INSERT INTO events ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
        """
        
        cursor.executemany(insert_query, match_event_data.values.tolist())
        conn.commit()
        logger.info(f"Successfully added data about match {match_id} from {league}")

# Insert updated schedule into Cloud SQL
updated_schedule = updated_schedule.reset_index()
columns = updated_schedule.columns.tolist()
insert_query = f"""
INSERT INTO schedule ({', '.join(columns)})
VALUES ({', '.join(['%s'] * len(columns))})
"""
cursor.executemany(insert_query, updated_schedule.values.tolist())
conn.commit()

logger.info("Completed processing all leagues")

# Close the connection
cursor.close()
conn.close()

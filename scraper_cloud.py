from datetime import datetime
import soccerdata as sd
import logging
import pandas as pd
import numpy as np
import json
from pandas import DataFrame, concat
from google.cloud.sql.connector import Connector
import sqlalchemy
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
print(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

# Cloud SQL connection setup
instance_connection_name = "tidal-copilot-372909:europe-central2:football-db"
db_user = "postgres"
db_pass = "googlecloud-makeitloud"
db_name = "postgres"

connector = Connector()

def getconn():
    conn = connector.connect(
        instance_connection_name,
        "pg8000",
        user=db_user,
        password=db_pass,
        db=db_name
    )
    return conn

engine = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

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

conn = engine.connect()

schedule = pd.read_sql("SELECT * FROM schedule", conn)
events = pd.read_sql("SELECT * FROM events", conn)

updated_schedule = DataFrame()

meta_data = sqlalchemy.MetaData()
meta_data.reflect(engine)
events_table = meta_data.tables['events']
schedule_table = meta_data.tables['schedule']

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
        
        insert_stmt = events_table.insert().values(match_event_data.to_dict(orient='records'))

        conn.execute(insert_stmt)

        logger.info(f"Successfully added data about match {match_id} from {league}")


# Insert updated schedule into Cloud SQL
insert_stmt = schedule_table.insert().values(updated_schedule.to_dict(orient='records'))

conn.execute(insert_stmt)

logger.info("Completed processing all leagues")

# Close the connection
conn.close()

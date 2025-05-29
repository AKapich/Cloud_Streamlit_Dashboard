import cloudscraper
import re
import json
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import date
import numpy as np

def camel_to_snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def clean_for_postgres(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    for col in cleaned.columns:
        cleaned[col] = cleaned[col].replace({True: 1, False: 0})
        cleaned[col] = cleaned[col].fillna(0)
        # Convert booleans to integers
        if cleaned[col].dtype == bool:
            cleaned[col] = cleaned[col].astype(int)

        # # Handle NaNs in numeric columns
        # elif np.issubdtype(cleaned[col].dtype, np.number):
        #     cleaned[col] = cleaned[col].replace({np.nan: None})

        # Object columns (may contain strings, lists, dicts, or None)
        elif cleaned[col].dtype == object:
            cleaned[col] = cleaned[col].apply(
                lambda x: (
                    None
                    if (not isinstance(x, (dict, list)) and pd.isna(x)) or x == "NaN"
                    else json.dumps(x) if isinstance(x, (dict, list)) else x
                )
            )

    return cleaned

def create_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="googlecloud-makeitloud",
        host="34.116.186.20",
        port="5432",
    )
    return conn


def insert_dataframe(df, table_name, conn):

    data_tuples = list(df.itertuples(index=False, name=None))

    columns = ', '.join(df.columns)
    values_template = f"({', '.join(['%s'] * len(df.columns))})"

    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES %s"

    with conn.cursor() as cur:
        execute_values(cur, insert_query, data_tuples)
        conn.commit()

def extract_match_centre_data(match_id):
    url = f"https://www.whoscored.com/Matches/{match_id}/Live"
    scraper = cloudscraper.create_scraper()
    html = scraper.get(url).text

    # Find the 'matchCentreData: {' position
    m = re.search(r"matchCentreData\s*:\s*{", html)
    if not m:
        raise ValueError("matchCentreData not found")

    start = m.end() - 1  # position of '{'

    # Function to find the matching closing brace
    def find_matching_brace(s, start_pos):
        stack = []
        for i in range(start_pos, len(s)):
            if s[i] == '{':
                stack.append('{')
            elif s[i] == '}':
                stack.pop()
                if not stack:
                    return i
        raise ValueError("No matching closing brace found")

    end = find_matching_brace(html, start)

    json_str = html[start : end + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        json_str_clean = re.sub(r",\s*}", "}", json_str)
        json_str_clean = re.sub(r",\s*]", "]", json_str_clean)
        data = json.loads(json_str_clean)

    return data

conn = create_connection()

cursor = conn.cursor()
cursor.execute("""
    SELECT e.game_id
    FROM events e
    JOIN schedule s ON e.game_id = s.game_id
    WHERE EXTRACT(MONTH FROM s.date) = EXTRACT(MONTH FROM CURRENT_DATE)
      AND EXTRACT(YEAR FROM s.date) = EXTRACT(YEAR FROM CURRENT_DATE)
""")
events_db = pd.DataFrame(
    cursor.fetchall(), columns=[desc[0] for desc in cursor.description]
)

leagues = [
    "ESP-La Liga",
    "ENG-Premier League",
    "FRA-Ligue 1",
    "GER-Bundesliga",
    "ITA-Serie A"
]

tournament_ids = {"ESP-La Liga": "23401",
    "ENG-Premier League": "23400",
    "FRA-Ligue 1": "23414",
    "GER-Bundesliga": "23471",
    "ITA-Serie A": "23490"}

scraper = cloudscraper.create_scraper()
season="2425"
all_match_info = []
events = pd.DataFrame()
for league in leagues:
    tournament_id = tournament_ids[league]
    year = str(date.today().year)
    month = str(date.today().month)
    if (len(month) < 2):
        month = "0" + month
    response = scraper.get(f"https://www.whoscored.com/tournaments/{tournament_id}/data/?d={year}{month}").text
    json_obj = json.loads(response)
    matches = json_obj["tournaments"][0]["matches"]
    df_matches = pd.DataFrame(matches)

    new_matches = set(
        df_matches[df_matches["startedAtUtc"].notna()]["id"]
    ) - set(events_db["game_id"])
    
    for match in matches:
        if not match["id"] in new_matches:
            print(f"skipping {match['id']}")
            continue 
        match["league"] = league
        match["season"] = season
        match["game"] = f"{match['startTime'][:10]} {match['homeTeamName']}-{match['awayTeamName']}"
        map_team = {match["homeTeamId"]: match["homeTeamName"], match["awayTeamId"]: match["awayTeamName"]}
        all_match_info.append(match)
     
        match_id = match["id"]
        print(f"extracting match {match['game']} with id: {match_id}")    
        match_centre_data = extract_match_centre_data(match_id)
        game_events = match_centre_data["events"]
        map_player = match_centre_data["playerIdNameDictionary"]
        if game_events:
            df_events = pd.DataFrame(game_events)
            df_events["game"] = match["game"]
            df_events["league"] = league
            df_events["season"] = season
            df_events["game_id"] = match["id"]
            df_events["team"] = df_events["teamId"].map(map_team)
            df_events["type"] = df_events["type"].apply(
                lambda x: x["displayName"]
            )
            df_events["outcomeType"] = df_events["outcomeType"].apply(
                lambda x: x["displayName"]
            )
            df_events["period"] = df_events["period"].apply(
                lambda x: x["displayName"]
            )
            df_events["player"] = df_events["playerId"].apply(
                lambda x: map_player[str(int(x))] if pd.notnull(x) else np.nan
            )
            df_events.columns = [camel_to_snake(col) for col in df_events.columns]
            df_events = df_events.drop(columns=["id", "event_id", "satisfied_events_types"])
            if "is_own_goal" in df_events.columns:
                df_events = df_events.drop(columns=["is_own_goal"])
            events = pd.concat([events, df_events], ignore_index=True)
        
all_matches_df = pd.DataFrame(all_match_info)
all_matches_df.columns = [camel_to_snake(col) for col in all_matches_df.columns]
all_matches_df = all_matches_df.rename(columns={"id": "game_id", "home_team_name": "home_team", "away_team_name": "away_team", "start_time_utc": "date"})


insert_dataframe(clean_for_postgres(all_matches_df), "schedule", conn)

insert_dataframe(clean_for_postgres(events), "events", conn)




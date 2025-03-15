import duckdb
import soccerdata as sd
from datetime import datetime
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

conn = duckdb.connect("whoscored.duckdb")
schedule = conn.execute("SELECT * FROM schedule").fetchdf()
events = conn.execute("SELECT * FROM events").fetchdf()


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

    new_matches = set(
        new_schedule[new_schedule["started_at_utc"].notna()]["game_id"]
    ) - set(events["game_id"])

    logger.info(f"Found {len(new_matches)} new matches for {league}")

    for match_id in new_matches:
        match_event_data = ws.read_events(match_id=match_id, output_fmt="events")
        conn.register("temp_match", match_event_data.reset_index())
        conn.execute(
            """
            INSERT INTO events
            SELECT * FROM temp_match
        """
        )
        conn.commit()
        logger.info(f"Successfully added data about match {match_id} from {league}")

    # in case any new match is scheduled
    matches_not_present_in_schedule = set(new_schedule["game_id"]) - set(
        events["game_id"]
    )
    if len(matches_not_present_in_schedule) > 0:
        conn.register(
            "temp_schedule",
            new_schedule[
                new_schedule["game_id"].isin(matches_not_present_in_schedule)
            ].reset_index(),
        )
        conn.execute(
            """
            INSERT INTO schedule 
            SELECT * FROM temp_schedule
        """
        )
        conn.commit()
        logger.info(
            f"Successfully inserted schedule information about {len(matches_not_present_in_schedule)} matches for {league}"
        )


logger.info("Completed processing all leagues")
conn.close()

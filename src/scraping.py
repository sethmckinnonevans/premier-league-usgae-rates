import soccerdata as sd
from pathlib import Path
import pandas as pd
import ScraperFC as sfc

def data_scraper(whoscored_league, whoscored_season,
                 sofascore_league, sofascore_season):

    # Initiate folders
    project_folder = Path(__file__).resolve().parents[1]
    raw_data_folder = project_folder / "data" / "raw"
    raw_data_folder.mkdir(parents=True, exist_ok=True)

    # Whoscored data
    ws = sd.WhoScored(leagues = whoscored_league,
                 seasons = whoscored_season)
    event_data = ws.read_events()

    # Sofascore data
    ss = sfc.Sofascore()
    player_data = ss.scrape_player_league_stats(year = sofascore_season, league = sofascore_league)
    team_data = ss.scrape_team_league_stats(year = sofascore_season, league = sofascore_league)
    player_details = ss.scrape_player_details(year = sofascore_season, league = sofascore_league)


    # Save data
    event_data.to_csv(raw_data_folder / f"{sofascore_league}-{whoscored_season}-event-data.csv")
    player_data.to_csv(raw_data_folder / f"{sofascore_league}-{whoscored_season}-player-data.csv")
    team_data.to_csv(raw_data_folder / f"{sofascore_league}-{whoscored_season}-team-data.csv")
    player_details.to_csv(raw_data_folder / f"{sofascore_league}-{whoscored_season}-player-details.csv")





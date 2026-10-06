import soccerdata as sd
from pathlib import Path
import pandas as pd
import ScraperFC as sfc

def data_scraper(whoscored_league, whoscored_season,
                 sofascore_league, sofascore_season,
                 output_path):

    # Whoscored data
    ws = sd.WhoScored(leagues = whoscored_league,
                 seasons = whoscored_season)
    event_data = ws.read_events()
    event_data.to_csv(output_path / f"{sofascore_league}-{whoscored_season}-event-data.csv", index = False)


    # Sofascore data
    ss = sfc.Sofascore()

    # Player Data
    player_data = ss.scrape_player_league_stats(year = sofascore_season, league = sofascore_league)
    player_data.to_csv(output_path / f"{sofascore_league}-{whoscored_season}-player-data.csv", index = False)

    # Team data
    team_data = ss.scrape_team_league_stats(year = sofascore_season, league = sofascore_league)
    team_data.to_csv(output_path / f"{sofascore_league}-{whoscored_season}-team-data.csv", index = False)

    # PLayer details
    player_details = ss.scrape_player_details(year = sofascore_season, league = sofascore_league)
    player_details = pd.DataFrame(player_details)
    player_details.to_csv(output_path / f"{sofascore_league}-{whoscored_season}-player-details.csv", index = False)





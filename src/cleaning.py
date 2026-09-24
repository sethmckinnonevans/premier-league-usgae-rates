from pathlib import Path
import pandas as pd
import numpy as np


def data_cleaning(event_data, player_data, team_data, player_details):

    # Initiate folders
    project_folder = Path(__file__).resolve().parents[1]
    cleaned_data_folder = project_folder / "data" / "cleaned"
    cleaned_data_folder.mkdir(parents=True, exist_ok=True)

    # 1: Check for duplicate player entries in the data
    if not (player_data["player id"].duplicated().any()): 
        print("No duplicate IDs in player_stats") 
    if not (player_details["id"].duplicated().any()):
        print("No duplicate IDs in player_details")
    
    # Check that the player id in player_stats matches the id in player_details
    if (player_data["player id"].isin(player_details["id"]).all()):
        print("All IDs in player_stats have a corresponding ID in player_details")
    
    # Check the number of unique ids in both data sets
    print("Players in player_stats: ", player_data["player id"].nunique())
    print("Players in player_details: ", player_details["id"].nunique())

    
    # 2: Merge player_stats and player_details on player id 
    players_df = player_data.merge(player_details, 
                                    how = "left",
                                    left_on = "player id",
                                    right_on = "id")

                                   
    # 3: Add the team posession stats to players_df
    # Check every player's team ID exists in team_data
    if (players_df["team id"].isin(team_data["teamId"]).all()):
        print("All teams are accounted for")
    
    # Separate team posession
    team_possession = team_data[["teamId","averageBallPossession"]].copy()
    
    # Round the average possession figures
    team_possession["averageBallPossession"] = team_possession["averageBallPossession"].round(2)
    
    # Merge team possession into players_df
    players_df = players_df.merge(team_possession,
                                 how = "left",
                                 left_on = "team id",
                                 right_on = "teamId")


    # 4: Handle positions, dropping GKs
    # Drop the single row without a detailed position (a Wolves u-21 player)
    players_df = players_df.dropna(subset = ["positions_detailed"]).copy()
    
    # Check the data type
    print(players_df["positions_detailed"].apply(type).value_counts())
    
    # Modify to a list
    import ast
    players_df["positions_detailed"] = players_df["positions_detailed"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    print(players_df["positions_detailed"].apply(type).value_counts())
    
    # Find the detailed primary position
    players_df["primaryPosition"] = players_df["positions_detailed"].apply(lambda x: x[0])
    
    # Define a position map to group players by position
    position_map = {
        "ST": "Striker",
        "LW": "Winger",
        "RW": "Winger",
        "AM": "Midfielder",
        "CM": "Midfielder",
        "DM": "Midfielder",
        "MC": "Midfielder",
        "DL": "Fullback",
        "DR": "Fullback",
        "MR": "Fullback",
        "ML": "Fullback",
        "DC": "Centerback"}
    
    players_df["positionGroup"] = players_df["primaryPosition"].map(position_map)
    
    # Drop goalkeeprs
    players_df = players_df[players_df["primaryPosition"] != "GK"].copy()


    # 5: Derive unsuccessful dribbles 
    # Calculate the total dribbles 
    players_df["totalDribbles"] = np.where(
        players_df["successfulDribblesPercentage"] > 0,
        players_df["successfulDribbles"] / (players_df["successfulDribblesPercentage"] / 100),
        0)
    
    # Derive the unsuccessful dribbles and ensure integer values
    players_df["unsuccessfulDribbles"] = (
        players_df["totalDribbles"] - players_df["successfulDribbles"]).round().astype("Int64")

    # 6: Create a final dataframe with only essential metrics and export it
    # Define the required columns
    feature_cols = ["name","id","team","team id","primaryPosition","positionGroup","minutesPlayed","averageBallPossession","totalShots",
                 "inaccuratePasses", "dispossessed","unsuccessfulDribbles","keyPasses","assists","expectedAssists","goals","expectedGoals",
                 "market_value"]
    
    # Create the final df
    players_cleaned_df = players_df[feature_cols].copy()
    
    # Rename columns for clarity
    players_cleaned_df = players_cleaned_df.rename(columns = {
        "name" : "playerName",
        "id" : "playerId",
        "team" : "teamName",
        "team id" : "teamId",
        "market_value" : "marketValue"})
    
    # Fill nan values with zero
    players_cleaned_df["expectedAssists"] = players_cleaned_df["expectedAssists"].fillna(0)
    players_cleaned_df["expectedGoals"] = players_cleaned_df["expectedGoals"].fillna(0)
    players_cleaned_df["marketValue"] = players_cleaned_df["marketValue"].fillna(0)

    # 7: Clean team_data
    # Define the required columns
    team_cols = ["teamName", "teamId", "goalsScored","averageBallPossession"]
    
    # Create the cleaned data frame
    teams_cleaned_df = team_data[team_cols].copy()
    
    # Round the possession column
    teams_cleaned_df["averageBallPossession"] = teams_cleaned_df["averageBallPossession"].round(2)


    # 8: Export the data
    players_cleaned_df.to_csv(cleaned_data_folder / "player_data_cleaned.csv", index = False)
    teams_cleaned_df.to_csv(cleaned_data_folder/ "team_data_cleaned.csv", index = False)

    return players_cleaned_df, teams_cleaned_df
    
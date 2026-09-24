import pandas as pd
from pathlib import Path
import numpy as np
from difflib import get_close_matches

def find_name_mismatches(players_df, sca_df, cutoff=0.7):
    """
    Find player names present in player data but missing from SCA data
    and provide the closest SCA name match.
    """

    missing_players = players_df[
        ~players_df["playerName"].isin(sca_df["player"])
    ]

    mismatches = []

    sca_names = sca_df["player"].dropna().unique().tolist()

    for player in missing_players["playerName"]:

        match = get_close_matches(
            player,
            sca_names,
            n=1,
            cutoff=cutoff
        )

        mismatches.append({
            "playerName": player,
            "possibleMatch": match[0] if match else None
        })

    return pd.DataFrame(mismatches)

def calculate_metrics(player_data, team_data, sca_data, name_mapping = None):

    players_df = player_data.copy()
    teams_df = team_data.copy()
    sca_df = sca_data.copy()

    # ---------------------------------------------------------
    # 1. Calculate PEA and PEA/90
    # ---------------------------------------------------------

    players_df["PEA"] = (
        players_df["totalShots"]
        + players_df["inaccuratePasses"]
        + players_df["dispossessed"]
        + players_df["unsuccessfulDribbles"]
    )

    players_df["PEA/90"] = (
        players_df["PEA"]
        / players_df["minutesPlayed"]
        * 90
    ).round(2)

    # ---------------------------------------------------------
    # 2. Standardise SCA player names
    # ---------------------------------------------------------

    if name_mapping is not None:
        sca_df["player"] = sca_df["player"].replace(name_mapping)

    # ---------------------------------------------------------
    # 3. Merge SCA data
    # ---------------------------------------------------------

    merged_df = players_df.merge(
        sca_df,
        left_on="playerName",
        right_on="player",
        how="left",
        validate="one_to_one"
    )

    merged_df = merged_df.drop(columns="player")

    merged_df["total_sca"] = (
        merged_df["total_sca"]
        .fillna(0)
        .astype(int)
    )

    # ---------------------------------------------------------
    # 4. Calculate SCA/90
    # ---------------------------------------------------------

    merged_df["SCA/90"] = (
        merged_df["total_sca"]
        / merged_df["minutesPlayed"]
        * 90
    ).round(2)

    # ---------------------------------------------------------
    # 5. Possession-adjusted metrics
    # ---------------------------------------------------------

    merged_df["adjPEA/90"] = (
        merged_df["PEA/90"]
        * (50 / merged_df["averageBallPossession"])
    ).round(2)

    merged_df["adjSCA/90"] = (
        merged_df["SCA/90"]
        * (50 / merged_df["averageBallPossession"])
    ).round(2)

    # ---------------------------------------------------------
    # 6. Calculate team totals
    # ---------------------------------------------------------

    team_totals = (
        merged_df
        .groupby("teamId")[["PEA", "total_sca"]]
        .sum()
        .reset_index()
    )

    team_totals = team_totals.rename(columns={
        "PEA": "teamTotalPEA",
        "total_sca": "teamTotalSCA"
    })

    teams_df = teams_df.merge(
        team_totals,
        on="teamId",
        how="left"
    )

    # ---------------------------------------------------------
    # 7. Calculate usage rates
    # ---------------------------------------------------------

    merged_df = merged_df.merge(
        teams_df[
            ["teamId", "teamTotalPEA", "teamTotalSCA"]
        ],
        on="teamId",
        how="left"
    )

    merged_df["usageRate"] = (
        merged_df["PEA"]
        / merged_df["teamTotalPEA"]
    ).round(3)

    merged_df["attackingInvolvement"] = (
        merged_df["total_sca"]
        / merged_df["teamTotalSCA"]
    ).round(3)

    # ---------------------------------------------------------
    # 8. Relative Creation Efficiency
    # ---------------------------------------------------------

    merged_df["RCE"] = (
        merged_df["attackingInvolvement"]
        / merged_df["usageRate"]
    ).round(3)

    merged_df["RCE"] = (
        merged_df["RCE"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )
    # ---------------------------------------------------------
    # 8. Total G + A and xGI
    # ---------------------------------------------------------
   
    merged_df["GA"] = merged_df["goals"] + merged_df["assists"]
    merged_df["GA"] = merged_df["GA"].astype(int)
    
    merged_df["xGI"] = (merged_df["expectedGoals"] + merged_df["expectedAssists"]).round(2)
    
    # ---------------------------------------------------------
    # 9. Final player metrics
    # ---------------------------------------------------------

    feature_cols = [
        "playerName",
        "playerId",
        "teamName",
        "teamId",
        "primaryPosition",
        "positionGroup",
        "minutesPlayed",
        "PEA",
        "PEA/90",
        "adjPEA/90",
        "total_sca",
        "SCA/90",
        "adjSCA/90",
        "usageRate",
        "attackingInvolvement",
        "RCE",
        "assists",
        "expectedAssists",
        "goals",
        "expectedGoals",
        "GA",
        "xGI",
        "marketValue"
    ]

    player_usage_data = merged_df[feature_cols].copy()

    # Save outputs
    project_folder = Path(__file__).resolve().parents[1]
    data_folder = project_folder / "data"
    
    player_usage_data.to_csv(data_folder / "player_usage_data.csv", index=False)
    
    merged_df.to_csv(data_folder/ "player_data_master.csv", index=False)

    return player_usage_data
    
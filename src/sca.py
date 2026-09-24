import pandas as pd
from pathlib import Path

SCA_TYPES = {
    "Pass",
    "BallTouch",
    "Foul",
    "TakeOn",
    "CornerAwarded",
    "SavedShot",
    "ShotOnPost",
    "GoodSkill"
}


def calculate_sca(match):
    
    # Identify direct and secondary shot-creating actions for one match.

    sca_results = []

    shots = match[match["is_shot"] == True]

    for shot_idx in shots.index:

        shot = match.loc[shot_idx]

        scas = []

        i = shot_idx - 1

        while i >= 0:

            event = match.loc[i]

            # Opposition event
            if event["team_id"] != shot["team_id"]:

                # Successful opposition event ends possession
                if event["outcome_type"] == "Successful":
                    break

                # Unsuccessful opposition event is ignored
                i -= 1
                continue

            # Same-team unsuccessful event
            if event["outcome_type"] != "Successful":
                i -= 1
                continue

            # Event must qualify as a SCA
            if event["type"] not in SCA_TYPES:
                i -= 1
                continue

            # Don't count same player twice
            if any(
                sca["player_id"] == event["player_id"]
                for sca in scas
            ):
                i -= 1
                continue

            # Log SCA
            scas.append({
                "player_id": event["player_id"],
                "player": event["player"],
                "type": event["type"],
                "row": i
            })

            # These events cannot have a secondary SCA
            if event["type"] in {
                "Foul",
                "SavedShot",
                "ShotOnPost"
            }:
                break

            # Maximum of two SCAs
            if len(scas) == 2:
                break

            i -= 1

        # Create result
        result = {
            "game_id": shot["game_id"],
            "shot_player": shot["player"],
            "shot_player_id": shot["player_id"],
            "shot_type": shot["type"],
            "shot_row": shot_idx,

            "direct_sca_player": None,
            "direct_sca_player_id": None,
            "direct_sca_type": None,

            "secondary_sca_player": None,
            "secondary_sca_player_id": None,
            "secondary_sca_type": None
        }

        if len(scas) >= 1:
            result["direct_sca_player"] = scas[0]["player"]
            result["direct_sca_player_id"] = scas[0]["player_id"]
            result["direct_sca_type"] = scas[0]["type"]

        if len(scas) >= 2:
            result["secondary_sca_player"] = scas[1]["player"]
            result["secondary_sca_player_id"] = scas[1]["player_id"]
            result["secondary_sca_type"] = scas[1]["type"]

        sca_results.append(result)

    return pd.DataFrame(sca_results)


def calculate_sca_for_season(event_data):
    
    # Calculate shot-creating actions for every match in the event data.

    all_sca_results = []

    game_ids = event_data["game_id"].unique()

    for game_id in game_ids:

        match = (
            event_data[event_data["game_id"] == game_id]
            .reset_index(drop=True)
        )

        match_sca = calculate_sca(match)

        all_sca_results.append(match_sca)

    return pd.concat(
        all_sca_results,
        ignore_index=True
    )


def create_sca_dataframe(all_sca_results):
    
    # Aggregate shot-level SCA results into player-level SCA statistics.

    sca_types = [
        "Pass",
        "BallTouch",
        "Foul",
        "TakeOn",
        "CornerAwarded",
        "SavedShot",
        "ShotOnPost",
        "GoodSkill"
    ]

    # Direct SCA
    direct_sca = (
        all_sca_results
        .dropna(subset=["direct_sca_player"])
        .groupby([
            "direct_sca_player",
            "direct_sca_type"
        ])
        .size()
        .unstack(fill_value=0)
    )

    direct_sca = direct_sca.reindex(
        columns=sca_types,
        fill_value=0
    )

    direct_sca.columns = [
        f"direct_{sca_type.lower()}_sca"
        for sca_type in direct_sca.columns
    ]

    # Secondary SCA
    secondary_sca = (
        all_sca_results
        .dropna(subset=["secondary_sca_player"])
        .groupby([
            "secondary_sca_player",
            "secondary_sca_type"
        ])
        .size()
        .unstack(fill_value=0)
    )

    secondary_sca = secondary_sca.reindex(
        columns=sca_types,
        fill_value=0
    )

    secondary_sca.columns = [
        f"secondary_{sca_type.lower()}_sca"
        for sca_type in secondary_sca.columns
    ]

    # Merge
    sca_df = direct_sca.join(
        secondary_sca,
        how="outer"
    ).fillna(0)

    sca_df = sca_df.astype(int)

    # Identify direct/secondary columns
    direct_cols = [
        col for col in sca_df.columns
        if col.startswith("direct_")
    ]

    secondary_cols = [
        col for col in sca_df.columns
        if col.startswith("secondary_")
    ]

    # Totals
    sca_df["direct_sca"] = sca_df[direct_cols].sum(axis=1)

    sca_df["secondary_sca"] = sca_df[secondary_cols].sum(axis=1)

    sca_df["total_sca"] = (
        sca_df["direct_sca"] +
        sca_df["secondary_sca"]
    )

    # Rearrange columns
    sca_df = sca_df[
        [
            "total_sca",
            "direct_sca",
            "secondary_sca",

            "direct_pass_sca",
            "direct_balltouch_sca",
            "direct_foul_sca",
            "direct_takeon_sca",
            "direct_cornerawarded_sca",
            "direct_savedshot_sca",
            "direct_shotonpost_sca",
            "direct_goodskill_sca",

            "secondary_pass_sca",
            "secondary_balltouch_sca",
            "secondary_foul_sca",
            "secondary_takeon_sca",
            "secondary_cornerawarded_sca",
            "secondary_savedshot_sca",
            "secondary_shotonpost_sca",
            "secondary_goodskill_sca"
        ]
    ]

    sca_df = sca_df.reset_index()

    sca_df = sca_df.rename(
        columns={"direct_sca_player": "player"})

    # Save
    project_folder = Path(__file__).resolve().parents[1]
    cleaned_data_folder = project_folder / "data" / "cleaned"
    cleaned_data_folder.mkdir(parents=True, exist_ok=True)

    sca_df.to_csv(
        cleaned_data_folder / "SCA.csv",
        index=False)

    return sca_df
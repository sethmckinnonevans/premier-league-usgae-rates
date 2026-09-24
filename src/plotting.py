from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import r2_score
import plotly.graph_objects as go


def plot_positions(df, position_name, kit_colours, minimum_minutes, interactive = False):
    
    # Extract positional data
    data = df[df["positionGroup"] == position_name]

    # Filter for minutes
    data = data[data["minutesPlayed"] >= minimum_minutes]

    # Define folders
    project_folder = Path(__file__).resolve().parents[1]
    figures_folder = project_folder / "figures"
    
    # Define default font
    plt.rcParams["font.family"] = "DIN Alternate"

    # Define the team colours
    point_colours = data["teamId"].map(kit_colours)

    # Linerar regression
    x = data["PEA/90"]
    y = data["SCA/90"]

    slope, intercept = np.polyfit(x,y,1)

    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = slope * x_line + intercept

    # Define y_pred for R^2 score
    y_pred = slope * x + intercept
    
    # ===========================================
    # Interactive
    # ===========================================

    if interactive:

        # Add custom data for hover interaction
        custom_data = data[["playerName", "PEA/90", "SCA/90", "GA"]].to_numpy()

        # Define the marker sizes
        sizes = 10 + data["GA"] * 3

        # Helper function for hover info text colour
        def get_text_colour(hex_colour):
            hex_colour = hex_colour.lstrip("#")
        
            r = int(hex_colour[0:2], 16)
            g = int(hex_colour[2:4], 16)
            b = int(hex_colour[4:6], 16)
    
            brightness = (r * 299 + g * 587 + b * 114) / 1000
        
            return "#404040" if brightness > 160 else "#CCCCCC"

        hover_text_colours = point_colours.apply(get_text_colour)
        
        # Initialise figure
        fig = go.Figure()

        # Scatter data
        fig.add_trace(go.Scatter(x = data["PEA/90"],
                                 y = data["SCA/90"],
                                 mode = "markers+text",

                                 marker = dict(size = sizes,
                                              color = point_colours,
                                              line = dict(color = "#CCCCCC",
                                                          width = 0.5)),

                                 customdata = custom_data,

                                 hovertemplate=("<b>%{customdata[0]}</b><br>"
                                                "PEA / 90: %{customdata[1]:.2f}<br>"
                                                "SCA / 90: %{customdata[2]:.2f}<br>"
                                                "Goals + Assists: %{customdata[3]}"
                                                "<extra></extra>"),

                                 hoverlabel = dict(
                                     bgcolor = point_colours,
                                     bordercolor = "#CCCCCC",
                                     font = dict(color = hover_text_colours,
                                                size = 12,
                                                family = "DIN Alternate")),

                                 showlegend = False))

        # Add a regression line
        fig.add_trace(go.Scatter(x = x_line,
                                 y = y_line,
                                 mode = "lines",
                                 line = dict(color = "#CCCCCC",
                                             dash = "dash",
                                             width = 1),
                                 showlegend = False,
                                 hoverinfo = "skip"))

        fig.update_layout(height = 550,
                          autosize = True,
    
                          margin = dict(l = 10,
                                        r = 10,
                                        t = 30,
                                        b = 10),
    
                          plot_bgcolor = "#404040",
                          paper_bgcolor = "#404040",

                          title=dict(text=f"Premier League {position_name}s 2025/26",
                                    x = 0.05,
                                    xanchor = "left",
                                    y = 0.97,
                                    yanchor = "middle",
                                    font = dict(
                                    size = 18,
                                    color="white",
                                    family = "DIN Alternate")),
                                      
                          xaxis = dict(range=[data["PEA/90"].min() - 1, (data["PEA/90"].max())+0.5],
                                       title = "PEA / 90 mins",
                                       title_font = dict(color = "#CCCCCC",
                                                         size = 14,
                                                         family = "DIN Alternate"),
                                       tickfont = dict(color = "#CCCCCC",
                                                       size = 12,
                                                       family = "DIN Alternate"),
                                       showline = True,
                                       linecolor = "#CCCCCC",
                                       linewidth = 1,
                                       mirror = True,
                                       showgrid = False),
    
                          yaxis = dict(range = [0, (data["SCA/90"].max())+0.5],
                                       title = "SCA / 90 mins",
                                       title_font = dict(color = "#CCCCCC",
                                                         size = 14,
                                                         family = "DIN Alternate"),
                                       tickfont = dict(color = "#CCCCCC",
                                                       size = 12,
                                                       family = "DIN Alternate"),
                                       showline = True,
                                       linecolor = "#CCCCCC",
                                       linewidth = 1,
                                       mirror = True,
                                       showgrid = False))

        fig.write_html(figures_folder / f"html/{position_name}s.html",
                      config = {"responsive" : True})

        fig.show()
        
    
    # ===========================================
    # Non-Interactive
    # ===========================================
    else:

        # Define the marker sizes
        sizes = 10 + data["GA"] * 40
        
        # Initialise the figure
        fig, ax = plt.subplots(1,1, figsize = (12,6), facecolor = "#404040")
        
        # Plot PEA/90 v CC/90 on the first axis
        ax.scatter(data["PEA/90"],
                        data["SCA/90"],
                        s = sizes,
                        alpha = 0.8,
                        c = point_colours,
                        edgecolors = "#CCCCCC",
                        linewidth = 0.5)
    
        # Figure customisation
        ax.set_title(f"Premier League {position_name}s 2025/26",
                          fontsize = 16,
                          pad = 10,
                          color = "white",
                          loc = "left")
        ax.set_xlabel("PEA / 90 mins",
                          fontsize = 12,
                          color = "#CCCCCC")
        ax.set_ylabel("SCA / 90 mins",
                          fontsize = 12,
                          color = "#CCCCCC")
        ax.set_facecolor("#404040")
        ax.tick_params(axis = "both",
                      labelsize = 12,
                      labelcolor = "#CCCCCC",
                      color = "#CCCCCC")
        for spine in ax.spines.values():
            spine.set_color("#CCCCCC")
            spine.set_linewidth(1)
    
    
        # Define the top 10 players in PEA and CC per 90 to annotate on the figure
        top_players = set(pd.concat([data.nlargest(10, "PEA/90"),
                                     data.nlargest(10, "SCA/90")])["playerName"])
        for _, player in data[data["playerName"].isin(top_players)].iterrows():
            ax.annotate(
                player["playerName"],
                (player["PEA/90"], player["SCA/90"]),
                xytext=(0, -12),
                textcoords="offset points",
                ha = "center",
                color = "#CCCCCC",
                fontsize = 10)
        
        
        
        ax.plot(x_line, y_line, 
                     linestyle = "--", 
                     linewidth = 1, 
                     c = "#CCCCCC",
                     alpha = 1)
        
        plt.savefig(figures_folder / "positions" / f"{position_name}.jpg",
                   format = "jpg",
                   dpi = 150)

        plt.show()



def plot_team(df,team_name, team_colour):

    # Find the team specific data
    team_data = df[df["teamName"] == team_name].copy()

    # Remove players with less than 5 matches played
    team_data = team_data[team_data["minutesPlayed"] >= 450]

    # Define default font
    plt.rcParams["font.family"] = "DIN Alternate"
    
    # Initialise the figure
    fig,ax = plt.subplots(1,1, figsize = (12,6), facecolor = "#404040")

    # Define the marker sizes
    sizes = 10 + team_data["GA"] * 40

    # Plot the data
    ax.scatter(team_data["usageRate"] * 100,
               team_data["attackingInvolvement"] *100,
               s = sizes,
               c = team_colour,
               alpha = 0.8,
               edgecolor = "#CCCCCC",
               linewidth = 0.5)

    # Figure customisation
    ax.set_title(f"{team_name} Player Usage Rates",
                      fontsize = 16,
                      pad = 10,
                      color = "white",
                      loc = "left")
    ax.set_xlabel("Usage Rate %",
                      fontsize = 12,
                      color = "#CCCCCC")
    ax.set_ylabel("Attacking Involvement %",
                      fontsize = 12,
                      color = "#CCCCCC")
    ax.set_facecolor("#404040")
    ax.tick_params(axis = "both",
                  labelsize = 12,
                  labelcolor = "#CCCCCC",
                  color = "#CCCCCC")
    for spine in ax.spines.values():
        spine.set_color("#CCCCCC")
        spine.set_linewidth(1)

    
    # Annotate player names
    for _, player in team_data.iterrows():

        ax.annotate(
            player["playerName"],
            (player["usageRate"] *100, player["attackingInvolvement"]*100),
            xytext = (0, -12),
            ha = "center",
            textcoords = "offset points",
            fontsize = 8,
            color = "#CCCCCC")

    # Plot an x=y line
    max_value = max((team_data["usageRate"]*100).max(),
                   (team_data["attackingInvolvement"]*100).max())
    ax.plot([0,max_value],
            [0, max_value],
            linestyle = "--",
            linewidth = 1,
            color = "#CCCCCC")

    # Save fig
    project_folder = Path(__file__).resolve().parents[1]
    figures_folder = project_folder / "figures"
    
    plt.savefig(figures_folder/ "teams" / f"{team_name}-usage-rates.png",
               format = "png",
               dpi = 150)
    plt.show()
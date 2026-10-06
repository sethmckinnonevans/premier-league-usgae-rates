from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import r2_score
import plotly.graph_objects as go


def plot_positions(df, position_name, kit_colours, minimum_minutes, league_name, output_path, interactive = False):
    
    # Extract positional data
    data = df[df["positionGroup"] == position_name]

    # Filter for minutes
    data = data[data["minutesPlayed"] >= minimum_minutes]
    
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
        custom_data = data[["playerName", "PEA/90", "SCA/90", "RCE", "GA"]].to_numpy()

        # Define the marker sizes
        sizes = 10 + data["GA"] * 2

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
                                                "RCE: %{customdata[3]:.2f}<br>"
                                                "Goals + Assists: %{customdata[4]}"
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

                          title=dict(text=f"{league_name} {position_name}s 2025/26",
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

        fig.write_html(output_path/ f"{position_name}s.html",
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
        ax.set_title(f"{league_name} {position_name}s 2025/26",
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
        
        plt.savefig(output_path /f"{position_name}.jpg",
                   format = "jpg",
                   dpi = 150)

        plt.show()


def plot_team(df,team_name, team_colour, output_path):

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
    
    plt.savefig(output_path/ f"{team_name}-usage-rates.png",
               format = "png",
               dpi = 150)
    plt.show()




def plot_transfers(df, team_name, players_out, players_in, kit_colours, output_path):

    # Get team data
    team_data = df[df["teamName"] == team_name].copy()

    # Find transferred in players 
    transfers_in = df[df["playerName"].isin(players_in)].copy()

    # Add transferred players to team data
    team_data = pd.concat([team_data, transfers_in], ignore_index = True)

    # PLayer status
    team_data["status"] = "stayed"
    team_data.loc[team_data["playerName"].isin(players_out), "status"] = "out"
    team_data.loc[team_data["playerName"].isin(players_in), "status"] = "in"
    
    # Remove players with less than 5 matches played
    team_data = team_data[team_data["minutesPlayed"] >= 450]

    # Define original and new squads
    original_squad = team_data[team_data["status"] != "in"]
    new_squad = team_data[team_data["status"] != "out"]
    
    # Define default font
    plt.rcParams["font.family"] = "DIN Alternate"

    # Original squad plotting data
    original_custom_data = original_squad[["playerName","usageRate","attackingInvolvement","RCE","GA"]]
    original_custom_data["usageRate"] *= 100
    original_custom_data["attackingInvolvement"] *= 100
    original_custom_data = original_custom_data.to_numpy()
    original_sizes = 10 + original_squad["GA"] * 3
    original_colours = original_squad["teamId"].map(kit_colours)

    # New squad plotting data
    new_custom_data = new_squad[["playerName","usageRate","attackingInvolvement","RCE","GA"]]
    new_custom_data["usageRate"] *= 100
    new_custom_data["attackingInvolvement"] *= 100
    new_custom_data = new_custom_data.to_numpy()
    new_sizes = 10 + new_squad["GA"] * 3
    new_colours = new_squad["teamId"].map(kit_colours)

    # Establish figure
    fig = go.Figure()

    # Scatter Original Squad
    fig.add_trace(go.Scatter(x = original_squad["usageRate"] * 100,
                             y = original_squad["attackingInvolvement"] * 100,
                             mode = "markers+text",
                            
                             marker = dict(size = original_sizes,
                                              color = original_colours,
                                              line = dict(color = "#CCCCCC",
                                                          width = 0.5)),
                             customdata = original_custom_data,

                             hovertemplate=("<b>%{customdata[0]}</b><br>"
                                            "Usage Rate: %{customdata[1]:.1f}%<br>"
                                            "Att Inv: %{customdata[2]:.1f}%<br>"
                                            "RCE: %{customdata[3]:.2f}<br>"
                                            "Goals + Assists: %{customdata[4]}"
                                            "<extra></extra>"),

                             hoverlabel = dict(bgcolor = original_colours,
                                               bordercolor = "#CCCCCC",
                                               font = dict(color = "#CCCCCC",
                                                           size = 12,
                                                           family = "DIN Alternate")),

                             showlegend = False,
                             hoverinfo = "skip",
                             visible = True))
    
    # Scatter New Squad
    fig.add_trace(go.Scatter(x = new_squad["usageRate"] * 100,
                             y = new_squad["attackingInvolvement"] * 100,
                             mode = "markers+text",
                            
                             marker = dict(size = new_sizes,
                                              color = new_colours,
                                              line = dict(color = "#CCCCCC",
                                                          width = 0.5)),
                             customdata = new_custom_data,

                             hovertemplate=("<b>%{customdata[0]}</b><br>"
                                            "Usage Rate: %{customdata[1]:.1f}%<br>"
                                            "Att Inv: %{customdata[2]:.1f}%<br>"
                                            "RCE: %{customdata[3]:.2f}<br>"
                                            "Goals + Assists: %{customdata[4]}"
                                            "<extra></extra>"),

                             hoverlabel = dict(bgcolor = new_colours,
                                               bordercolor = "#CCCCCC",
                                               font = dict(color = "#CCCCCC",
                                                           size = 12,
                                                           family = "DIN Alternate")),

                             showlegend = False,
                             hoverinfo = "skip",
                             visible = False))

    # Plot an x=y line
    max_value = max((team_data["usageRate"]*100).max(),
                   (team_data["attackingInvolvement"]*100).max())

    fig.add_trace(go.Scatter(x = [0, max_value],
                             y = [0, max_value],
                             mode = "lines",
                             line = dict(color = "#CCCCCC",
                                         dash = "dash",
                                         width = 1),
                             showlegend = False,
                             hoverinfo = "skip",
                             visible = True))

    fig.update_layout(height = 550,
                      autosize = True,

                      margin = dict(l = 10,
                                    r = 10,
                                    t = 30,
                                    b = 10),

                      plot_bgcolor = "#404040",
                      paper_bgcolor = "#404040",

                      title=dict(text=f"{team_name} Player Usage Rates",
                                x = 0.05,
                                xanchor = "left",
                                y = 0.97,
                                yanchor = "middle",
                                font = dict(
                                size = 18,
                                color="white",
                                family = "DIN Alternate")),

                      updatemenus = [dict(type = "buttons",
                                          direction = "right",
                                          x = 0.99,
                                          y = 0.05,
                                          xanchor="right",
                                          yanchor="middle",

                                          bgcolor = "#404040",
                                          bordercolor = "#CCCCCC",
                                          borderwidth = 1,
                                          font = dict(color = "#CCCCCC",
                                                      size = 12,
                                                      family = "DIN Alternate"),
                                          
                                          buttons=[dict(label="25/26 Squad",
                                                        method="update",
                                                        args=[{"visible": [True, False, True]}]),
                                                   dict(label="26/27 Squad*",
                                                        method="update",
                                                        args=[{"visible": [False, True, True]}])])],
                                  
                      xaxis = dict(range=[0, ((team_data["usageRate"] * 100 ).max()) + 0.5],
                                   title = "Usage Rate %",
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

                      yaxis = dict(range = [0, ((team_data["attackingInvolvement"]*100).max())+0.5],
                                   title = "Attacking Involvement %",
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

    # Save fig
    fig.write_html(output_path / f"{team_name}-transfers.html",
                      config = {"responsive" : True})
    
    
    fig.show()
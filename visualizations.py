from mplsoccer.pitch import Pitch, VerticalPitch
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as pat
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
from scipy.spatial import ConvexHull
from scipy.ndimage import gaussian_filter1d
from utils import *
from constants import colors


def passing_sonars(main_df, team, inverse=False):
    startingXI = getStartingXI(main_df, team)
    df = main_df[
        (main_df["team"] == team)
        & (main_df["player"].isin(startingXI))
        & (main_df["type"] == "Pass")
    ].copy()
    df["length"] = np.sqrt((df["end_x"] - df["x"]) ** 2 + (df["end_y"] - df["y"]) ** 2)
    df["angle"] = np.arctan2(df["end_y"] - df["y"], df["end_x"] - df["x"])

    df["angle_bin"] = pd.cut(
        df["angle"],
        bins=np.linspace(-np.pi, np.pi, 21),
        labels=False,
        include_lowest=True,
    )

    pass_sonar = df.groupby(["player", "angle_bin"], as_index=False)
    pass_sonar = pass_sonar.agg({"length": "mean"})
    # count occurances of passes in particular bins
    counter = (
        df.groupby(["player", "angle_bin"]).size().to_frame(name="amount").reset_index()
    )
    pass_sonar = pd.concat([pass_sonar, counter["amount"]], axis=1)

    average_location = df.groupby("player").agg({"x": ["mean"], "y": ["mean"]})
    average_location.columns = ["x", "y"]

    if inverse:
        average_location["x"] = 100 - average_location["x"]
        average_location["y"] = 100 - average_location["y"]
        pass_sonar["angle_bin"] = (pass_sonar["angle_bin"] + 10) % 20

    pass_sonar = pass_sonar.merge(average_location, left_on="player", right_index=True)

    fig, ax = plt.subplots(figsize=(12, 8), constrained_layout=False, tight_layout=True)
    fig.set_facecolor("#0e1117")
    ax.patch.set_facecolor("#0e1117")
    pitch = Pitch(pitch_type="opta", pitch_color="#0e1117", line_color="#c7d5cc")
    pitch.draw(ax=ax)

    for player in startingXI:
        for _, row in pass_sonar[pass_sonar.player == player].iterrows():
            theta_left_start = 198

            opacity = 0.4 if row.amount < 3 else 0.77 if row.amount < 5 else 1

            theta_left = theta_left_start + (360 / 20) * (row.angle_bin)
            theta_right = theta_left - (360 / 20)

            pass_wedge = pat.Wedge(
                center=(row.x, row.y),
                r=row.length * 0.2,
                theta1=theta_right,
                theta2=theta_left,
                facecolor=colors[team],
                edgecolor="black",
                alpha=opacity,
            )
            ax.add_patch(pass_wedge)

    for _, row in average_location.iterrows():
        annotation_text = row.name.split(" ")[-1]
        pitch.annotate(
            annotation_text,
            xy=(row.x, row.y + 4.5),
            c="white",
            va="center",
            ha="center",
            size=9,
            fontweight="bold",
            ax=ax,
        )

    ax.set_title(
        f"{team} Passing Sonars",
        color="white",
        fontsize=20,
        fontweight="bold",
        fontfamily="Monospace",
        pad=-5,
    )

    return fig, ax


def pass_heatmap(main_df, team, inverse=False):
    passes = main_df[(main_df["team"] == team) & (main_df["type"] == "Pass")].copy()
    passes = passes.query(f'team == "{team}"')

    fig, ax = plt.subplots(figsize=(12, 8), constrained_layout=False, tight_layout=True)
    fig.set_facecolor("#0e1117")
    ax.patch.set_facecolor("#0e1117")
    pitch = Pitch(pitch_type="opta", pitch_color="#0e1117", line_color="#c7d5cc")
    pitch.draw(ax=ax)

    if inverse:
        passes["x"] = 100 - passes["x"]
        passes["y"] = 100 - passes["y"]

    sns.kdeplot(
        x=passes["x"],
        y=passes["y"],
        fill=True,
        shade_lowest=False,
        alpha=0.6,
        n_levels=10,
        cmap=LinearSegmentedColormap.from_list(
            "",
            [lighten_hex_color(colors[team], 0.45), colors[team]],
            N=100,
        ),
        ax=ax,
    )
    ax.set_xlim(0, 100)
    ax.set_ylim(100, 0)

    ax.set_title(f"{team} Passes Heatmap", color="white", size=20, fontweight="bold")

    return fig, ax


def voronoi(main_df, home_team, away_team):

    subs = main_df[main_df["type"] == "SubstitutionOn"]
    min_threshold = min(subs["minute"])
    sec_threshold = min(subs["second"])
    df = main_df[
        (main_df["minute"] < min_threshold)
        | ((main_df["minute"] == min_threshold) & (main_df["second"] < sec_threshold))
    ].copy()
    df = df[(df["x"].notna()) & (df["y"].notna())]

    # average location
    df = df.groupby(["player", "team"]).agg({"x": ["mean"], "y": ["mean"]})
    df.columns = ["x", "y"]
    df = df.reset_index()
    # the column responsible for voronoi division must be boolean
    df["team_id"] = df["team"] == home_team

    # reverse the coords of one team
    for i in range(len(df)):
        if not (df["team_id"][i]):
            df.loc[:, "x"][i] = 100 - df["x"][i]
            df.loc[:, "y"][i] = 100 - df["y"][i]

    fig, ax = plt.subplots(figsize=(12, 8), constrained_layout=False, tight_layout=True)
    fig.set_facecolor("#0e1117")
    ax.patch.set_facecolor("#0e1117")
    pitch = Pitch(pitch_type="opta", pitch_color="#0e1117", line_color="#c7d5cc")
    pitch.draw(ax=ax)

    pitch.voronoi(df.x, df.y, df.team)
    team1, team2 = pitch.voronoi(df.x, df.y, df.team_id)

    pitch.polygon(team1, ax=ax, fc=colors[home_team], ec="white", lw=3, alpha=0.5)
    pitch.polygon(team2, ax=ax, fc=colors[away_team], ec="white", lw=3, alpha=0.5)

    # Plot players
    for i in range(len(df["x"])):
        pitch.scatter(df["x"][i], df["y"][i], ax=ax, color=colors[df["team"][i]])

        annotation_text = df["player"][i].split(" ")[-1]

        pitch.annotate(
            annotation_text,
            xy=(df["x"][i], df["y"][i] + 2),
            c="black",
            va="center",
            ha="center",
            size=7.5,
            fontweight="bold",
            ax=ax,
        )

    ax.set_title(
        f"Voronoi Diagram",
        color="white",
        fontsize=20,
        fontweight="bold",
        fontfamily="Monospace",
        pad=-5,
    )
    return fig, ax


def progressive_passes(main_df, team, inverse=False):

    df = main_df[(main_df["team"] == team) & (main_df["type"] == "Pass")].copy()

    if not inverse:
        df["beginning"] = np.sqrt(np.square(100 - df["x"]) + np.square(50 - df["y"]))
        df["end"] = np.sqrt(np.square(100 - df["end_x"]) + np.square(50 - df["end_y"]))
    else:
        df["x"] = 100 - df["x"]
        df["y"] = 100 - df["y"]
        df["end_x"] = 100 - df["end_x"]
        df["end_y"] = 100 - df["end_y"]
        df["beginning"] = np.sqrt(np.square(df["x"]) + np.square(df["y"]))
        df["end"] = np.sqrt(np.square(df["end_x"]) + np.square(df["end_y"]))

    # according to definiton pass is progressive if it brings the ball closer to the goal by at least 25%
    df["progressive"] = df["end"] < 0.75 * df["beginning"]

    fig, ax = plt.subplots(figsize=(12, 8), constrained_layout=False, tight_layout=True)
    fig.set_facecolor("#0e1117")
    ax.patch.set_facecolor("#0e1117")
    pitch = Pitch(pitch_type="opta", pitch_color="#0e1117", line_color="#c7d5cc")
    pitch.draw(ax=ax)

    df = df[df["progressive"] == True]
    df.index = range(len(df))
    pitch.lines(
        xstart=df["x"],
        ystart=df["y"],
        xend=df["end_x"],
        yend=df["end_y"],
        ax=ax,
        comet=True,
        color=colors[team],
    )

    ax.set_title(
        f"{team} Progressive Passes",
        color="white",
        fontsize=20,
        fontweight="bold",
        fontfamily="Monospace",
        pad=-5,
    )

    return fig, ax


def final_3rd_passes(main_df, team, inverse=False):

    df = main_df[(main_df["team"] == team) & (main_df["type"] == "Pass")].copy()

    if inverse:
        df["x"] = 100 - df["x"]
        df["y"] = 100 - df["y"]
        df["end_x"] = 100 - df["end_x"]
        df["end_y"] = 100 - df["end_y"]

    df["to_final_3rd"] = (
        ((df["end_x"] > 66.7) & (df["x"] <= 66.7))
        if not inverse
        else ((df["end_x"] < 33.3) & (df["x"] >= 33.3))
    )

    fig, ax = plt.subplots(figsize=(12, 8), constrained_layout=False, tight_layout=True)
    fig.set_facecolor("#0e1117")
    ax.patch.set_facecolor("#0e1117")
    pitch = Pitch(pitch_type="opta", pitch_color="#0e1117", line_color="#c7d5cc")
    pitch.draw(ax=ax)

    df = df[df["to_final_3rd"] == True]
    df.index = range(len(df))
    pitch.lines(
        xstart=df["x"],
        ystart=df["y"],
        xend=df["end_x"],
        yend=df["end_y"],
        ax=ax,
        comet=True,
        color=colors[team],
    )

    ax.set_title(
        f"{team} Passes to Final 3rd",
        color="white",
        fontsize=20,
        fontweight="bold",
        fontfamily="Monospace",
        pad=-5,
    )

    return fig, ax


def penalty_area_passes(main_df, team, inverse=False):

    df = main_df[(main_df["team"] == team) & (main_df["type"] == "Pass")].copy()

    if inverse:
        df["x"] = 100 - df["x"]
        df["y"] = 100 - df["y"]
        df["end_x"] = 100 - df["end_x"]
        df["end_y"] = 100 - df["end_y"]

    df["to_penalty"] = (
        (df["end_x"].between(83, 100) & df["end_y"].between(21, 79))
        if not inverse
        else (df["end_x"].between(0, 17) & df["end_y"].between(21, 79))
    )

    fig, ax = plt.subplots(figsize=(12, 8), constrained_layout=False, tight_layout=True)
    fig.set_facecolor("#0e1117")
    ax.patch.set_facecolor("#0e1117")
    pitch = Pitch(pitch_type="opta", pitch_color="#0e1117", line_color="#c7d5cc")
    pitch.draw(ax=ax)

    df = df[df["to_penalty"] == True]
    df.index = range(len(df))
    pitch.lines(
        xstart=df["x"],
        ystart=df["y"],
        xend=df["end_x"],
        yend=df["end_y"],
        ax=ax,
        comet=True,
        color=colors[team],
    )

    ax.set_title(
        f"{team} Passes to Final 3rd",
        color="white",
        fontsize=20,
        fontweight="bold",
        fontfamily="Monospace",
        pad=-5,
    )

    return fig, ax


def shot_types(main_df, home_team, away_team):

    outcome_dict = {
        "SavedShot": "s",
        "Goal": "*",
        "MissedShots": "X",
        "ShotOnPost": "v",
    }

    fig, ax = plt.subplots(figsize=(12, 8), constrained_layout=False, tight_layout=True)
    fig.set_facecolor("#0e1117")
    ax.patch.set_facecolor("#0e1117")
    pitch = VerticalPitch(
        pitch_type="opta", pitch_color="#0e1117", line_color="#c7d5cc"
    )
    pitch.draw(ax=ax)

    shots = main_df[main_df["is_shot"] == 1]

    shots.index = range(len(shots))

    for i in range(len(shots)):
        if shots.iloc[i].team == home_team:
            ax.scatter(
                shots["y"][i],
                shots["x"][i],
                color=colors[home_team],
                edgecolors="white",
                marker=outcome_dict[shots["type"][i]],
                s=120,
            )
        else:
            # vertical pitch, therefore y and coords exchanged
            ax.scatter(
                100 - shots["y"][i],
                100 - shots["x"][i],
                color=colors[away_team],
                edgecolors="white",
                marker=outcome_dict[shots["type"][i]],
                s=120,
            )

    legend_elements = [
        Line2D(
            [],
            [],
            marker="s",
            linestyle="None",
            markersize=10,
            label="Blocked/Saved",
            markerfacecolor="white",
            markeredgecolor="black",
        ),
        Line2D(
            [],
            [],
            marker="*",
            linestyle="None",
            markersize=10,
            label="Goal",
            markerfacecolor="white",
            markeredgecolor="black",
        ),
        Line2D(
            [],
            [],
            marker="X",
            linestyle="None",
            markersize=10,
            label="Off Target",
            markerfacecolor="white",
            markeredgecolor="black",
        ),
        Line2D(
            [],
            [],
            marker="v",
            linestyle="None",
            markersize=10,
            label="Post",
            markerfacecolor="white",
            markeredgecolor="black",
        ),
    ]
    ax.legend(
        handles=legend_elements,
        loc="center",
    )

    ax.set_title(
        f"Shot Map",
        color="white",
        fontsize=20,
        fontweight="bold",
        fontfamily="Monospace",
        pad=-5,
    )

    home_team_text = ax.text(
        50,
        60,
        home_team,
        fontsize=8,
        ha="center",
        fontfamily="Monospace",
        fontweight="bold",
        color="white",
    )
    home_team_text.set_bbox(
        dict(
            facecolor=colors[home_team], alpha=0.5, edgecolor="white", boxstyle="round"
        )
    )
    away_team_text = ax.text(
        50,
        39,
        away_team,
        fontsize=8,
        ha="center",
        fontfamily="Monospace",
        fontweight="bold",
        color="white",
    )
    away_team_text.set_bbox(
        dict(
            facecolor=colors[away_team], alpha=0.5, edgecolor="white", boxstyle="round"
        )
    )

    return fig, ax


def team_convex_hull(main_df, team, inverse=False):
    startingXI = getStartingXI(main_df, team)
    events = main_df[
        (main_df["team"] == team)
        & (main_df["player"].isin(startingXI))
        & (main_df["is_touch"] == 1)
    ].copy()

    events = events[events["x"].notna()]
    if inverse:
        events["x"] = 100 - events["x"]
        events["y"] = 100 - events["y"]

    fig, ax = plt.subplots(
        figsize=(12, 12), constrained_layout=False, tight_layout=True
    )
    fig.set_facecolor("#0e1117")
    ax.patch.set_facecolor("#0e1117")
    pitch = Pitch(pitch_type="opta", pitch_color="#0e1117", line_color="#c7d5cc")
    pitch.draw(ax=ax)

    colors_ = [
        "#eb4034",
        "#ebdb34",
        "#98eb34",
        "#34eb77",
        "#be9cd9",
        "#5797e6",
        "#fbddad",
        "#de34eb",
        "#eb346b",
        "#34ebcc",
        "#dbd5d5",
    ]
    colordict = dict(zip(startingXI, colors_))

    for player in startingXI:
        tempdf = events[events["player"] == player]
        # threshold of 0.2 sd
        tempdf = tempdf[np.abs(stats.zscore(tempdf[["x", "y"]])) < 0.2]
        actions = tempdf[["x", "y"]].dropna().values

        annotation_text = player.split(" ")[-1]

        pitch.annotate(
            annotation_text,
            xy=(np.mean(tempdf.x), np.mean(tempdf.y)),
            c=colordict[player],
            va="center",
            ha="center",
            size=10,
            fontweight="bold",
            ax=ax,
        )

        try:
            hull = ConvexHull(actions)
        except:
            pass
        try:
            for i in hull.simplices:
                ax.plot(actions[i, 0], actions[i, 1], colordict[player])
                ax.fill(
                    actions[hull.vertices, 0],
                    actions[hull.vertices, 1],
                    c=colordict[player],
                    alpha=0.03,
                )
        except:
            pass

    ax.set_title(
        f"{team} Action Territories",
        color="white",
        fontsize=20,
        fontweight="bold",
        fontfamily="Monospace",
        pad=-5,
    )

    return fig, ax


def pass_xT_momentum(
    main_df, home_team, away_team, window_size=4, decay_rate=0.25, sigma=1
):
    df = main_df.copy()

    xT = pd.read_csv(
        "https://raw.githubusercontent.com/AKapich/WorldCup_App/main/app/xT_Grid.csv",
        header=None,
    )
    xT = np.array(xT)
    xT_rows, xT_cols = xT.shape

    def get_xT(df):
        df = df[df["type"] == "Pass"]

        df[f"start_x_bin"] = pd.cut(df["x"], bins=xT_cols, labels=False)
        df[f"start_y_bin"] = pd.cut(df["y"], bins=xT_rows, labels=False)
        df[f"end_x_bin"] = pd.cut(df["end_x"], bins=xT_cols, labels=False)
        df[f"end_y_bin"] = pd.cut(df["end_x"], bins=xT_rows, labels=False)
        df["start_zone_value"] = df[[f"start_x_bin", f"start_y_bin"]].apply(
            lambda z: xT[z[1]][z[0]], axis=1
        )
        df["end_zone_value"] = df[[f"end_x_bin", f"end_y_bin"]].apply(
            lambda z: xT[z[1]][z[0]], axis=1
        )
        df["xT"] = df["end_zone_value"] - df["start_zone_value"]

        return df[["xT", "minute", "second", "team", "type"]]

    xT_data = get_xT(df=df)
    xT_data["xT_clipped"] = np.clip(xT_data["xT"], 0, 0.1)

    max_xT_per_minute = (
        xT_data.groupby(["team", "minute"])["xT_clipped"].max().reset_index()
    )

    minutes = sorted(xT_data["minute"].unique())
    weighted_xT_sum = {team: [] for team in max_xT_per_minute["team"].unique()}
    momentum = []

    for current_minute in minutes:
        for team in weighted_xT_sum:
            recent_xT_values = max_xT_per_minute[
                (max_xT_per_minute["team"] == team)
                & (max_xT_per_minute["minute"] <= current_minute)
                & (max_xT_per_minute["minute"] > current_minute - window_size)
            ]

            weights = np.exp(
                -decay_rate * (current_minute - recent_xT_values["minute"].values)
            )
            weighted_sum = np.sum(weights * recent_xT_values["xT_clipped"].values)
            weighted_xT_sum[team].append(weighted_sum)

        momentum.append(weighted_xT_sum[home_team][-1] - weighted_xT_sum[away_team][-1])

    momentum_df = pd.DataFrame({"minute": minutes, "momentum": momentum})

    fig, ax = plt.subplots(figsize=(18, 12))
    fig.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")

    ax.tick_params(axis="x", colors="white")
    ax.tick_params(axis="y", which="both", left=False, right=False, labelleft=False)
    for spine in ["top", "right", "bottom", "left"]:
        ax.spines[spine].set_visible(False)
    ax.set_xticks([0, 15, 30, 45, 60, 75, 90])
    ax.margins(x=0)
    ax.set_ylim(-0.08, 0.08)

    momentum_df["smoothed_momentum"] = gaussian_filter1d(
        momentum_df["momentum"], sigma=sigma
    )
    ax.plot(momentum_df["minute"], momentum_df["smoothed_momentum"], color="white")

    ax.axhline(0, color="white", linestyle="--", linewidth=0.5)
    ax.fill_between(
        momentum_df["minute"],
        momentum_df["smoothed_momentum"],
        where=(momentum_df["smoothed_momentum"] > 0),
        color=colors[home_team],
        alpha=0.5,
        interpolate=True,
    )
    ax.fill_between(
        momentum_df["minute"],
        momentum_df["smoothed_momentum"],
        where=(momentum_df["smoothed_momentum"] < 0),
        color=colors[away_team],
        alpha=0.5,
        interpolate=True,
    )

    ax.set_xlabel(
        "Minute", color="white", fontsize=15, fontweight="bold", fontfamily="Monospace"
    )
    ax.set_ylabel(
        "Momentum",
        color="white",
        fontsize=15,
        fontweight="bold",
        fontfamily="Monospace",
    )

    home_team_text = ax.text(
        7,
        0.064,
        home_team,
        fontsize=12,
        ha="center",
        fontfamily="Monospace",
        fontweight="bold",
        color="white",
    )
    home_team_text.set_bbox(
        dict(
            facecolor=colors[home_team], alpha=0.5, edgecolor="white", boxstyle="round"
        )
    )
    away_team_text = ax.text(
        7,
        -0.064,
        away_team,
        fontsize=12,
        ha="center",
        fontfamily="Monospace",
        fontweight="bold",
        color="white",
    )
    away_team_text.set_bbox(
        dict(
            facecolor=colors[away_team], alpha=0.5, edgecolor="white", boxstyle="round"
        )
    )

    goals = df[df["type"] == "Goal"][["minute", "team"]]
    for _, row in goals.iterrows():
        ymin, ymax = (0.5, 0.8) if row["team"] == home_team else (0.2, 0.5)
        ax.axvline(
            row["minute"],
            color="white",
            linestyle="--",
            linewidth=0.8,
            alpha=0.5,
            ymin=ymin,
            ymax=ymax,
        )
        ax.scatter(
            row["minute"],
            (1 if row["team"] == home_team else -1) * 0.049,
            color="white",
            s=100,
            zorder=10,
            alpha=0.7,
        )
        ax.text(
            row["minute"] + 0.1,
            (1 if row["team"] == home_team else -1) * 0.053,
            "Goal",
            fontsize=10,
            ha="center",
            va="center",
            fontfamily="Monospace",
            color="white",
        )

    ax.set_title(
        "Momentum (based on Pass xT)",
        color="white",
        fontsize=20,
        fontweight="bold",
        fontfamily="Monospace",
        pad=-5,
    )

    return fig, ax


def pitch_event_scatter(
    main_df, team, event_type, players=None, heatmap=False, inverse=False
):
    df = main_df[(main_df["team"] == team) & (main_df["type"] == event_type)]
    if players is not None:
        df = df[df["player"].isin(players)]

    fig, ax = plt.subplots(figsize=(12, 8), constrained_layout=False, tight_layout=True)
    fig.set_facecolor("#0e1117")
    ax.patch.set_facecolor("#0e1117")
    pitch = Pitch(pitch_type="opta", pitch_color="#0e1117", line_color="#c7d5cc")
    pitch.draw(ax=ax)

    if not heatmap:
        for idx, row in df.iterrows():
            ax.scatter(
                row["x"],
                row["y"],
                color=colors[team],
                s=100,
                edgecolor="black",
                zorder=3,
            )
    else:
        bin_statistic = pitch.bin_statistic(
            df.x, df.y, statistic="count", bins=(8, 6), normalize=False
        )
        pitch.heatmap(
            bin_statistic,
            edgecolor="#323b49",
            ax=ax,
            alpha=0.55,
            cmap=LinearSegmentedColormap.from_list(
                "custom_cmap", ["#f3f9ff", colors[team]], N=100
            ),
        )
        pitch.label_heatmap(
            bin_statistic,
            color="#323b49",
            fontsize=12,
            ax=ax,
            ha="center",
            va="center",
            fontweight="bold",
            family="monospace",
        )

    if not inverse:
        pitch.annotate(
            text="The direction of play  ",
            xytext=(40, -4),
            xy=(70, -4),
            ha="center",
            va="center",
            ax=ax,
            arrowprops=dict(facecolor="white"),
            fontsize=12,
            color="white",
            fontweight="bold",
            family="monospace",
        )
    else:
        pitch.annotate(
            text="  The direction of play",
            xytext=(60, -4),
            xy=(30, -4),
            ha="center",
            va="center",
            ax=ax,
            arrowprops=dict(facecolor="white"),
            fontsize=12,
            color="white",
            fontweight="bold",
            family="monospace",
        )

    title_event_dict = {
        "Pass": "Passes",
        "BallRecovery": "Ball Recoveries",
        "Foul": "Fouls",
        "Aerial": "Aerial Duels",
        "TakeOn": "Take-Ons",
        "Tackle": "Tackles",
        "Clearance": "Cleareances",
        "Interception": "Interceptions",
        "Dispossessed": "Dispossessed",
    }

    if players is not None and len(players) == 1:
        title = f"{team}: {title_event_dict[event_type]} map for {players[0]}"
    else:
        title = f"{team}: {title_event_dict[event_type]} map"
    ax.set_title(
        title,
        color="white",
        fontsize=20,
        fontweight="bold",
        fontfamily="Monospace",
        pad=-5,
    )

    return fig, ax


def overview(main_df, home_team, away_team):
    metrics = {}
    for team in [home_team, away_team]:
        metrics[team] = {
            "Field Tilt (%)": round(
                len(
                    main_df[
                        (main_df["is_touch"] == True)
                        & (main_df["x"] >= 66.7)
                        & (main_df["team"] == team)
                    ]
                )
                / len(main_df[(main_df["is_touch"] == True) & (main_df["x"] >= 66.7)])
                * 100,
                1,
            ),
            "Passes": str(
                len(main_df[(main_df["team"] == team) & (main_df["type"] == "Pass")])
            ),
            "Pass Accuracy (%)": round(
                len(
                    main_df[
                        (main_df["team"] == team)
                        & (main_df["type"] == "Pass")
                        & (main_df["outcome_type"] == "Successful")
                    ]
                )
                / len(main_df[(main_df["team"] == team) & (main_df["type"] == "Pass")])
                * 100,
                1,
            ),
            "Shots": str(
                len(main_df[(main_df["team"] == team) & (main_df["is_shot"].notna())])
            ),
            "Corners": str(
                len(
                    main_df[
                        (main_df["type"] == "CornerAwarded")
                        & (main_df["team"] == team)
                        & (main_df["outcome_type"] == "Successful")
                    ]
                )
            ),
            "Yellow Cards": str(
                len(
                    main_df[
                        (main_df["team"] == team) & (main_df["card_type"] == "Yellow")
                    ]
                )
            ),
            "Red Cards": str(
                len(
                    main_df[(main_df["team"] == team) & (main_df["card_type"] == "Red")]
                )
            ),
        }

    return pd.DataFrame(metrics)

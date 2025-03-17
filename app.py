import streamlit as st
import pandas as pd
import duckdb
import atexit
from constants import *
from utils import *
from visualizations import *


st.set_page_config(page_title="Football Analytics", page_icon="⚽", layout="wide")


def create_connection():
    conn = duckdb.connect(database="whoscored.duckdb")
    return conn


if "conn" not in st.session_state:
    st.session_state.conn = create_connection()


def close_connection():
    if "conn" in st.session_state:
        st.session_state.conn.close()
        st.write("Connection closed.")


atexit.register(close_connection)


# TODO to change for cloud storage
schedule = st.session_state.conn.execute("SELECT * FROM schedule").fetchdf()
events = st.session_state.conn.execute("SELECT * FROM events").fetchdf()
featured_matches = set(events["game_id"])

with st.sidebar:
    with st.sidebar.expander("Filters", expanded=False):
        date_range = st.date_input(
            "Date Range",
            value=(pd.Timestamp("2024-07-01"), pd.Timestamp.now()),
        )
        if len(date_range) != 2:
            date_range = (pd.Timestamp("2024-07-01"), pd.Timestamp.now())

    st.divider()

    st.title("⚽ Match Selection")
    selected_league = st.selectbox("Select League", list(leagues.keys()), index=0)
    selected_league_value = leagues[selected_league]

    matches_dict = {
        " - ".join(g[11:].split("-", 1)): g
        for g in schedule[
            (schedule["game_id"].isin(featured_matches))
            & (schedule["league"] == selected_league_value)
        ]["game"].values
        if pd.Timestamp(date_range[0])
        <= pd.Timestamp(g[:10])
        <= pd.Timestamp(date_range[1])
    }

    matches = sorted(
        matches_dict.keys(),
        key=lambda x: pd.Timestamp(matches_dict[x][:10]),
        reverse=True,
    )

    if not matches:
        st.warning("No matches found for the selected league and date range.")
        selected_match = None
    else:
        if (
            "selected_match" not in st.session_state
            or st.session_state.selected_match not in matches
        ):
            st.session_state.selected_match = matches[0]

        selected_match = st.selectbox(
            "Select Match",
            matches,
            index=matches.index(st.session_state.selected_match),
        )

    st.divider()
    st.title(f"Latest {selected_league} results:")

    for idx, row in (
        schedule[
            (schedule["game_id"].isin(featured_matches))
            & (schedule["league"] == selected_league_value)
        ]
        .sort_values("date", ascending=False)
        .head(3)
        .iterrows()
    ):
        match_label = f"{row['home_team']} - {row['away_team']}"
        home_logo = f"./logos/{row['league'].split('-')[-1]}/{row['home_team']}.png"
        away_logo = f"./logos/{row['league'].split('-')[-1]}/{row['away_team']}.png"

        col1, col2, col3 = st.columns([1, 4, 1])

        with col1:
            st.image(home_logo, width=30)
        with col2:
            if st.button(
                f"{row['home_team']} {int(row['home_score'])} : {int(row['away_score'])} {row['away_team']}",
                key=f"match_{idx}",
            ):
                st.session_state.selected_match = match_label
                st.rerun()
        with col3:
            st.image(away_logo, width=30)

if not selected_match:
    st.warning("No match selected.")
    st.stop()

home_team, away_team = selected_match.split(" - ", 1)
original_game = matches_dict[selected_match]

match_info = schedule[schedule["game"] == original_game].squeeze()

home_logo_url = f"./logos/{selected_league}/{home_team}.png"
away_logo_url = f"./logos/{selected_league}/{away_team}.png"
match_date = original_game[:10]

st.markdown(
    f"""
    <div style='text-align: center; font-size: 0.1rem;'>
        <h3>{match_date}</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([3, 2, 3])
img_height = 10

with col1:
    st.markdown(
        f"""
        <div style='text-align: center;'>
            <img src='{get_base64_image(home_logo_url)}' style='height:{img_height}rem;' />
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"<h2 style='text-align: center; margin: 0; font-size: 4rem;'>{int(match_info['home_score'])} : {int(match_info['away_score'])}</h2>",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""
        <div style='text-align: center;'>
            <img src='{get_base64_image(away_logo_url)}' style='height:{img_height}rem;' />
        </div>
        """,
        unsafe_allow_html=True,
    )

col4, col5, col6 = st.columns([3, 2, 3])
with col4:
    st.markdown(
        f"<div style='height: 50px; display: flex; justify-content: center; align-items: flex-end; font-weight: bold;'>{home_team}</div>",
        unsafe_allow_html=True,
    )

with col5:
    st.markdown("<div style='height: 50px;'>&nbsp;</div>", unsafe_allow_html=True)

with col6:
    st.markdown(
        f"<div style='height: 50px; display: flex; justify-content: center; align-items: flex-end; font-weight: bold;'>{away_team}</div>",
        unsafe_allow_html=True,
    )

st.divider()

st.subheader("Match Analysis")
main_df = events[events["game_id"] == match_info["game_id"]].copy()


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Event Map", "Pitch Control", "Passing", "Shooting"]
)

with tab1:
    pass

with tab2:
    event_dict = {
        "Passes": "Pass",
        "Ball Recoveries": "BallRecovery",
        "Fouls": "Foul",
        "Aerial Duels": "Aerial",
        "Take-Ons": "TakeOn",
        "Tackles": "Tackle",
        "Cleareances": "Clearance",
        "Interceptions": "Interception",
        "Dispossessed": "Dispossessed",
    }

    tab2_col1, tab2_col2 = st.columns([1, 1])
    with tab2_col1:
        analysed_team_tab2 = st.radio(
            "Select Team",
            [home_team, away_team],
            horizontal=True,
            key="team_selector_tab2",
        )
        inverse_tab2 = analysed_team_tab2 == away_team

    with tab2_col2:
        show_heatmap = st.checkbox("Show Heatmap", value=False)

    event_type = st.selectbox(
        "Select Event Type",
        list(event_dict.keys()),
        index=0,
    )

    players = [
        p
        for p in list(main_df[main_df["team"] == analysed_team_tab2]["player"].unique())
        if p is not None
    ]
    with st.expander("Player Selection", expanded=False):
        grid = st.multiselect(
            "Select Players",
            players,
            default=players,
            placeholder="Choose players to display (default: all)",
        )

    if not grid:
        grid = players

    with st.spinner(f"Loading {event_type} visualization..."):
        fig, ax = pitch_event_scatter(
            main_df=main_df,
            event_type=event_dict[event_type],
            team=analysed_team_tab2,
            players=grid,
            heatmap=show_heatmap,
            inverse=inverse_tab2,
        )
        st.pyplot(fig)

with tab3:
    tab3_col1, tab3_col2 = st.columns([1, 1])
    with tab3_col1:
        analysed_team_tab3 = st.radio(
            "Select Team (applicable for player territories)",
            [home_team, away_team],
            horizontal=True,
            key="team_selector_tab3",
        )
        inverse_tab3 = analysed_team_tab3 == away_team

    with tab3_col2:
        plot_type_tab3 = st.radio(
            "Select Plot Type",
            ["Player Territories", "Voronoi Diagram"],
            horizontal=True,
            key="plot_type_tab3",
        )

    if plot_type_tab3 == "Player Territories":
        with st.spinner(f"Loading Player Territories visualization..."):
            fig, ax = team_convex_hull(main_df, analysed_team_tab3, inverse_tab3)
            st.pyplot(fig)
    else:  # Voronoi Diagram
        with st.spinner(f"Loading Voronoi Diagram visualization..."):
            fig, ax = voronoi(main_df, home_team, away_team)
            st.pyplot(fig)

with tab4:
    analysed_team_tab4 = st.radio(
        "Select Team", [home_team, away_team], horizontal=True, key="team_selector_tab4"
    )
    inverse_tab4 = analysed_team_tab4 == away_team

    pass_plotting_dict = {
        "Passing Sonars": passing_sonars,
        "Pass Heatmap": pass_heatmap,
        "Progressive Passes": progressive_passes,
        "Passes into Final 3rd": final_3rd_passes,
        "Passes into Penalty Area": penalty_area_passes,
    }

    plot_type = st.selectbox(
        "Select Plot Type",
        pass_plotting_dict.keys(),
        index=0,
    )

    plot_func_tab4 = pass_plotting_dict[plot_type]

    with st.spinner(f"Loading {plot_type} visualization..."):
        fig, ax = plot_func_tab4(
            main_df=main_df,
            team=analysed_team_tab4,
            inverse=inverse_tab4,
        )
        st.pyplot(fig)


with tab5:
    with st.spinner(f"Loading Shot Map..."):
        fig, ax = shot_types(main_df, home_team, away_team)
        st.pyplot(fig, use_container_width=False)

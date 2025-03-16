import streamlit as st
import pandas as pd
import duckdb
from constants import *
from utils import *
import atexit
from datetime import datetime


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

    if (
        "selected_match" not in st.session_state
        or st.session_state.selected_match not in matches
    ) and len(matches) > 0:
        st.session_state.selected_match = matches[0]
        selected_match_index = matches.index(st.session_state.selected_match)
    else:
        selected_match_index = 0

    selected_match = st.selectbox("Select Match", matches, index=selected_match_index)

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


st.subheader("Match Statistics")
chart_placeholder = st.empty()


tab1, tab2, tab3 = st.tabs(["Overview", "Player Stats", "Team Comparison"])

with tab1:
    pass

with tab2:
    pass

with tab3:
    pass

import streamlit as st
import pandas as pd
import duckdb
from constants import *
from utils import *
import atexit


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
            value=(pd.Timestamp.now() - pd.Timedelta(days=7), pd.Timestamp.now()),
        )

    st.divider()

    st.title("⚽ Match Selection")
    selected_league = st.selectbox("Select League", list(leagues.keys()), index=0)
    selected_league_value = leagues[selected_league]

    matches_dict = {
        " - ".join(g[11:].split("-")): g
        for g in schedule[
            (schedule["game_id"].isin(featured_matches))
            & (schedule["league"] == selected_league_value)
        ]["game"].values
    }

    matches = list(matches_dict.keys())
    selected_match = st.selectbox(f"Select Match", matches, index=0)

if selected_match is not None:
    home_team, away_team = selected_match.split(" - ")
    original_game = matches_dict[selected_match]

    match_info = schedule[schedule["game"] == original_game].squeeze()

    home_logo_url = f"./logos/{selected_league}/{home_team}.png"
    away_logo_url = f"./logos/{selected_league}/{away_team}.png"
    match_date = original_game[:11]

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

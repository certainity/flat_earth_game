# leaderboard_tab.py - Rankings
# Version: v0.001
# Notes: Displays leaderboard with filters.

import streamlit as st, json
from db import get_leaderboard

def render():
    st.subheader("🏆 Leaderboard")
    clan_filter = st.radio("Filter by:", ["All", "Flat Earthers 🌐", "Globies 🌍"])
    sort_choice = st.radio("Sort by:", ["Points", "Followers", "Level", "Wins", "Losses"])
    leaders = get_leaderboard(sort_choice.lower())

    if clan_filter != "All":
        leaders = [row for row in leaders if row[11] == clan_filter]

    if leaders:
        st.table([{
            "Username": row[1],
            "Level": row[5],
            "Points": row[4],
            "Followers": row[6],
            "Clan": row[11],
            "Items": len(json.loads(row[7])) if row[7] else 0,
            "Wins": row[9],
            "Losses": row[10],
            "W/L": round(row[9] / max(1, row[10]), 2) if row[10] > 0 else row[9]
        } for row in leaders])
    else:
        st.info("No players yet.")


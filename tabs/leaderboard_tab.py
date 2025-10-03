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
        leaders = [row for row in leaders if row[-1]==clan_filter]

    if leaders:
        st.table([{
            "Username": row[0], "Level": row[1], "Points": row[2],
            "Followers": row[3], "Clan": row[-1], "Items": len(json.loads(row[4])),
            "Wins": row[5], "Losses": row[6],
            "W/L": round(row[5]/max(1,row[6]),2) if row[6]>0 else row[5]
        } for row in leaders])
    else:
        st.info("No players yet.")

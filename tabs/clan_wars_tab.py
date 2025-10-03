# clan_wars_tab.py - Clan Stats
# Version: v0.001
# Notes: Displays clan war progress.

import streamlit as st
from db import get_clan_stats

def render():
    st.subheader("⚔️ Clan Wars")
    stats = get_clan_stats()
    if stats:
        table = []
        for clan_name, total_points, members, total_wins, total_losses in stats:
            avg_points = round(total_points / max(1,members),2)
            table.append({"Clan": clan_name,"Total Points": total_points,
                          "Members": members,"Avg Points": avg_points,
                          "Wins": total_wins,"Losses": total_losses})
        st.table(table)
    else:
        st.info("No clans yet.")

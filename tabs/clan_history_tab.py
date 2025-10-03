# clan_history_tab.py - Clan War History
# Version: v0.001
# Notes: Shows history of winning clans.

import streamlit as st, time
from db import get_clan_history, get_clan_streak

def render():
    st.subheader("📜 Clan War History")
    history = get_clan_history(10)
    if history:
        for clan,ts in history:
            ts_fmt = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
            st.write(f"🏆 {clan} won on {ts_fmt}")
        streak_clan,streak_count=get_clan_streak()
        if streak_count>1:
            st.success(f"🔥 {streak_clan} are on a {streak_count}-week streak!")
    else:
        st.info("No history yet.")

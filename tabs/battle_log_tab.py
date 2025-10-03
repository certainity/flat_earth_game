# battle_log_tab.py - Battle History
# Version: v0.001
# Notes: Shows logs of fights.

import streamlit as st, time
from db import get_battle_log

def render(username):
    st.subheader("📜 Battle Log")
    logs = get_battle_log(username)
    if logs:
        for log in logs:
            attacker, defender, outcome, f_change, p_change, ts = log
            ts_fmt = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
            if outcome == "win" and attacker == username:
                st.success(f"[{ts_fmt}] You beat {defender} ➜ +{f_change} followers, +{p_change} points")
            elif outcome == "lose" and attacker == username:
                st.error(f"[{ts_fmt}] You lost vs {defender} ➜ {p_change} points")
    else:
        st.info("No battles yet.")

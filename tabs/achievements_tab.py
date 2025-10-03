# achievements_tab.py - Player Badges
# Version: v0.001
# Notes: Shows unlocked/locked achievements.

import streamlit as st
from db import get_achievements

def render(username):
    st.subheader("🏅 Achievements")
    achs = get_achievements(username)
    if achs:
        for badge,achieved,ts in achs:
            st.write(f"🏅 {badge} ({'Unlocked' if achieved else 'Locked'})")
    else:
        st.info("No achievements yet.")

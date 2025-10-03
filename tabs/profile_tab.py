# profile_tab.py - Profile Display
# Version: v0.003
# Notes:
# - Fixed unpacking issue (quests has 8 columns now)
# - Uses object-style access for clarity

import streamlit as st
import time
from db import get_quests

def render(username, energy, points, level, followers, wins, losses, clan, items, last_login):
    # ✅ Override with live session values if available
    energy = st.session_state.get("energy", energy)
    points = st.session_state.get("points", points)
    followers = st.session_state.get("followers", followers)
    level = st.session_state.get("level", level)
    wins = st.session_state.get("wins", wins)
    losses = st.session_state.get("losses", losses)
    items = st.session_state.get("items", items)
    clan = st.session_state.get("clan", clan)
    last_login = st.session_state.get("last_login", last_login)

    st.subheader(f"Welcome, {username}!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Energy", energy)
    col2.metric("Credibility Points", points)
    col3.metric("Followers", followers)

    col4, col5, col6 = st.columns(3)
    col4.metric("Level", level)
    col5.metric("Wins", wins)
    col6.metric("Losses", losses)

    total_battles = wins + losses
    win_rate = round((wins / total_battles) * 100, 1) if total_battles > 0 else 0
    st.write(f"**Clan:** {clan}")
    st.write(f"**Inventory:** {', '.join(items) if items else 'No items'}")
    st.write(f"**Battles Fought:** {total_battles} (Win Rate: {win_rate}%)")

    # Account age (days since first login)
    days_old = round((time.time() - last_login) / 86400, 1)
    st.write(f"**Account Age:** {days_old} days")

    # Quest snapshot
    quests = get_quests(username)
    if quests:
        st.write("**Active Quests:**")
        for q in quests:
            qid = q.id
            qtype = q.quest_type
            prog = q.progress
            goal = q.goal
            reward = q.reward
            done = q.completed

            status = "✅ Completed" if done else f"{prog}/{goal}"
            st.write(f"• {qtype.title()} Quest → {status} (Reward: {reward} followers)")
    else:
        st.info("No active quests right now.")

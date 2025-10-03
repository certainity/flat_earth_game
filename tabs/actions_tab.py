# actions_tab.py - Player Actions
# Version: v0.002
# Notes:
# - Updates both session_state and DB instantly
# - Fix: profile tab shows updated stats right away

import streamlit as st
from db import get_quests, update_quest_progress, complete_quest, update_player
from game_logic import post_meme, debate_globie, level_up

def render(username, energy, points, followers, level, items):
    st.subheader("🎯 Actions")

    # Load from session_state if available
    energy = st.session_state.get("energy", energy)
    points = st.session_state.get("points", points)
    followers = st.session_state.get("followers", followers)
    level = st.session_state.get("level", level)
    items = st.session_state.get("items", items)
    wins = st.session_state.get("wins", 0)
    losses = st.session_state.get("losses", 0)

    if st.button("📢 Post a Meme"):
        energy, points, followers, msg = post_meme(energy, points, followers, items)
        if "⚠️" in msg:
            st.warning(msg)
        else:
            st.success(msg)
        for q in get_quests(username):
            if q[1] == "meme" and not q[5]:
                update_quest_progress(q[0], 1)
                if q[2]+1 >= q[3]:
                    complete_quest(q[0])

    if st.button("⚔️ Debate a Globie"):
        energy, points, followers, msg = debate_globie(energy, points, followers, items)
        if "WON" in msg:
            st.success(msg)
        elif "⚠️" in msg:
            st.warning(msg)
        else:
            st.error(msg)
        for q in get_quests(username):
            if q[1] == "debate" and not q[5]:
                update_quest_progress(q[0], 1)
                if q[2]+1 >= q[3]:
                    complete_quest(q[0])

    # Level up check
    level, energy, lvl_msg = level_up(points, level, energy)
    if lvl_msg:
        st.balloons()
        st.success(lvl_msg)

    # ✅ Save to session_state
    st.session_state.energy = energy
    st.session_state.points = points
    st.session_state.followers = followers
    st.session_state.level = level
    st.session_state.items = items
    st.session_state.wins = wins
    st.session_state.losses = losses

    # ✅ Save to DB immediately
    update_player(username, energy, points, level, followers, items, wins, losses)

    return energy, points, followers, level

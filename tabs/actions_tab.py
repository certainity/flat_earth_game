# actions_tab.py - Player Actions
# Version: v0.001
# Notes: Handles memes, debates, and leveling.


import streamlit as st
from db import get_quests, update_quest_progress, complete_quest
from game_logic import post_meme, debate_globie, level_up

def render(username, energy, points, followers, level, items):
    st.subheader("🎯 Actions")

    if st.button("📢 Post a Meme"):
        energy, points, followers, msg = post_meme(energy, points, followers, items)
        if "⚠️" in msg: st.warning(msg)
        else: st.success(msg)
        for q in get_quests(username):
            if q[1] == "meme" and not q[5]:
                update_quest_progress(q[0], 1)
                if q[2]+1 >= q[3]: complete_quest(q[0])

    if st.button("⚔️ Debate a Globie"):
        energy, points, followers, msg = debate_globie(energy, points, followers, items)
        if "WON" in msg: st.success(msg)
        elif "⚠️" in msg: st.warning(msg)
        else: st.error(msg)
        for q in get_quests(username):
            if q[1] == "debate" and not q[5]:
                update_quest_progress(q[0], 1)
                if q[2]+1 >= q[3]: complete_quest(q[0])

    level, energy, lvl_msg = level_up(points, level, energy)
    if lvl_msg:
        st.balloons()
        st.success(lvl_msg)

    return energy, points, followers, level

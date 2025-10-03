# quests_tab.py - Daily Quests
# Version: v0.002
# Notes: Fixed unpacking issue (quests has 8 columns)

import streamlit as st
from db import (
    get_quests, complete_quest, update_quest_progress, generate_daily_quests
)

def render(username, followers, level):
    st.subheader("🎯 Daily Quests")

    # Generate daily quests (scales with level)
    generate_daily_quests(username, level)

    quests = get_quests(username)
    if quests:
        for q in quests:
            qid = q.id
            qtype = q.quest_type
            prog = q.progress
            goal = q.goal
            reward = q.reward
            completed = q.completed

            if completed:
                st.success(f"✅ {qtype.title()} Quest — Completed (Reward: {reward} followers)")
                if st.button(f"Claim {reward} Followers", key=f"claim{qid}"):
                    followers += int(reward)
                    st.info(f"You claimed {reward} followers!")
            else:
                st.write(f"- {qtype.title()} Quest: {prog}/{goal} (Reward: {reward} followers)")
                progress_bar = int((prog / goal) * 100)
                st.progress(progress_bar)
                if prog < goal:
                    if st.button(f"Update Progress ({qtype})", key=f"upd{qid}"):
                        update_quest_progress(qid, prog + 1)
                        st.rerun()
    else:
        st.info("No active quests right now. Come back tomorrow for new quests!")

    return followers

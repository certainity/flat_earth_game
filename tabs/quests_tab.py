# quests_tab.py - Daily Quests System
# Version: v0.005
# Notes:
# - Quests vary by level (Battle, Meme, Debate, Boss)
# - Banner shows how many quests left to unlock next level
# - Rewards = Followers (scales by level) + Credibility Points (per quest type)

import streamlit as st
from db import (
    get_quests, update_quest_progress, complete_quest, 
    generate_daily_quests, reset_user_quests, update_player
)
import time

def render(username, followers, level, energy, points):
    st.header("🎯 Daily Quests")

    # --- Admin Reset Button ---
    # if st.button("🔄 Reset My Quests (Admin Only)"):
    #     reset_user_quests(username)
    #     generate_daily_quests(username, level)
    #     st.success("✅ Quests have been reset!")
    #     st.rerun()

    # --- Ensure quests exist ---
    quests = get_quests(username)
    if not quests:
        generate_daily_quests(username, level)
        quests = get_quests(username)

    # --- Banner: how many quests left ---
    incomplete = sum(1 for q in quests if not q.completed)
    if incomplete > 0:
        st.info(f"Complete {incomplete} more quest(s) to unlock the next level!")

    # --- Quest loop ---
    for q in quests:
        qid, q_username, qtype, prog, goal, reward, completed, ts = q

        # Display progress
        st.markdown(f"**{qtype.capitalize()} Quest** — {prog}/{goal} complete")
        st.progress(min(prog / goal, 1.0))

        if completed:
            st.success(f"✅ Completed (Reward: {reward} Followers)")
        else:
            # Button label by quest type
            if qtype == "battle":
                btn_label = f"⚔️ Battle Quest (-3 Energy)"
                cost = 3
                points_gain = 5
            elif qtype == "meme":
                btn_label = f"📢 Post Meme (-1 Energy)"
                cost = 1
                points_gain = 2
            elif qtype == "debate":
                btn_label = f"🗣️ Debate Globie (-2 Energy)"
                cost = 2
                points_gain = 3
            elif qtype == "boss":
                btn_label = f"👹 Boss Fight (-5 Energy)"
                cost = 5
                points_gain = 10
            else:
                btn_label = f"🌀 Do Quest"
                cost = 1
                points_gain = 1

            # Quest button
            if st.button(btn_label, key=f"quest_{qid}"):
                if energy < cost:
                    st.warning("⚠️ Not enough energy!")
                else:
                    # Deduct energy & progress
                    energy -= cost
                    prog += 1

                    if prog >= goal:
                        complete_quest(qid)
                        followers += reward
                        points += points_gain
                        st.success(f"🎉 Quest Completed! +{reward} Followers, +{points_gain} Points")
                    else:
                        update_quest_progress(qid, prog, 0)
                        st.info(f"Progress updated: {prog}/{goal}")

                    # Save stats
                    update_player(username, energy, points, level, followers, "[]", 0, 0)

                    # Force refresh so UI updates without double click
                    st.rerun()

    return followers, energy, points

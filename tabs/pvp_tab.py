# pvp_tab.py - PvP Battles
# Version: v0.002
# Notes:
# - Updated to handle structured PvP results from game_logic
# - Displays battle messages cleanly
# - Updates energy, points, followers, wins, losses

import streamlit as st, json
from db import get_leaderboard, add_battle
from game_logic import pvp_battle, safe_items

def render(username, clan, energy, points, followers, items, wins, losses):
    st.subheader("🥊 PvP Battles")

    # --- Get possible opponents ---
    all_players = get_leaderboard("points")
    # st.write("DEBUG: Players in DB →", all_players)

    opponents = [p for p in all_players if p[0] != username and p[-1] != clan]

    if opponents:
        opponent_choice = st.selectbox("Choose an enemy:", [p[0] for p in opponents])

        if st.button("⚔️ Attack! (Cost: 3 Energy)"):
            if energy >= 3:
                # Load opponent stats
                opp_row = [p for p in all_players if p[0] == opponent_choice][0]
                opponent = {
                    "username": opp_row[0],
                    "points": opp_row[2],
                    "followers": opp_row[3],
                    "items": safe_items(opp_row[4]),
                }
                attacker = {
                    "username": username,
                    "points": points,
                    "followers": followers,
                    "items": safe_items(items),
                }

                # Run battle
                outcome, result = pvp_battle(attacker, opponent)
                energy -= 3

                if outcome == "win":
                    followers += result["followers_gain"]
                    points += result["points_gain"]
                    wins += 1
                    add_battle(username, opponent_choice, "win",
                               result["followers_gain"], result["points_gain"])
                    st.success(result["message"])

                else:  # lose
                    points -= result["points_loss"]
                    losses += 1
                    add_battle(username, opponent_choice, "lose", 0, -result["points_loss"])
                    st.error(result["message"])

            else:
                st.warning("⚠️ Not enough energy for PvP!")

    else:
        st.info("No enemies available!")

    return energy, points, followers, wins, losses

# pvp_tab.py - PvP Battles
# Version: v0.001
# Notes: Handles player vs player fights.

import streamlit as st, json
from db import get_leaderboard, add_battle
from game_logic import pvp_battle

def render(username, clan, energy, points, followers, items, wins, losses):
    st.subheader("🥊 PvP Battles")
    all_players = get_leaderboard("points")
    opponents = [p for p in all_players if p[0] != username and p[-1] != clan]

    if opponents:
        opponent_choice = st.selectbox("Choose an enemy:", [p[0] for p in opponents])
        if st.button("⚔️ Attack! (Cost: 3 Energy)"):
            if energy >= 3:
                opp_row = [p for p in all_players if p[0] == opponent_choice][0]
                opponent = {"username": opp_row[0], "points": opp_row[2],
                            "followers": opp_row[3], "items": json.loads(opp_row[4])}
                attacker = {"username": username, "points": points,
                            "followers": followers, "items": items}
                outcome, value = pvp_battle(attacker, opponent)
                energy -= 3
                if outcome == "win":
                    followers += value; points += 20; wins += 1
                    add_battle(username, opponent_choice, "win", value, 20)
                    st.success(f"🎉 You defeated {opponent_choice}! +{value} followers, +20 points.")
                else:
                    points -= value; losses += 1
                    add_battle(username, opponent_choice, "lose", 0, -value)
                    st.error(f"💢 You lost against {opponent_choice}... -{value} points.")
            else:
                st.warning("Not enough energy for PvP!")
    else:
        st.info("No enemies available!")

    return energy, points, followers, wins, losses

# app.py - Flat Earth Wars
# Version: v0.002
# Notes:
# - Fixed missing `last_login` argument for profile_tab.render
# - Stable with modular tabs (quests, shop, PvP, etc.)

import streamlit as st, json
from db import (
    init_db, migrate_db, get_player, add_player, update_player,
    reset_clan_war
)
from game_logic import regenerate_energy

# --- Import Tabs ---
from tabs import (
    profile_tab, actions_tab, shop_tab, pvp_tab,
    leaderboard_tab, battle_log_tab, clan_wars_tab,
    clan_history_tab, quests_tab, achievements_tab,
    market_tab, events_tab, template_tab
)

# --- Init DB ---
init_db()
migrate_db()

# --- Weekly Clan War Reset ---
winner = reset_clan_war()
if winner:
    st.success(f"🎉 Weekly reset complete! {winner} received +50 Followers and +5 Energy each!")

# --- Header ---
st.markdown("# 🌍 Flat Earth Wars 🌎")
st.markdown("A Mafia Wars-style Flat Earth vs Globie game.")

# --- Login ---
username = st.text_input("Enter your username:")

if username:
    player = get_player(username)

    if not player:
        st.subheader("Choose Your Clan")
        clan_choice = st.radio("Pick a side:", ["Flat Earthers 🌐", "Globies 🌍"])
        if st.button("Join Clan"):
            add_player(username, clan_choice)
            st.success(f"You joined {clan_choice}!")
            st.rerun()
    else:
        # Unpack player
        (player_id, username, energy, points, level, followers,
         items_json, last_login, wins, losses, clan) = player
        items = json.loads(items_json)

        # Energy regen
        energy, last_login = regenerate_energy(energy, level, last_login)

        # --- Tabs ---
        tabs = st.tabs([
            "📋 Profile", "🎯 Actions", "🛒 Shop", "🥊 PvP",
            "🏆 Leaderboard", "📜 Battle Log", "⚔️ Clan Wars",
            "📜 Clan War History", "🎯 Quests", "🏅 Achievements",
            "💱 Market", "🌍 Events", "🆕 Template"
        ])

        with tabs[0]:
            # ✅ Added last_login
            profile_tab.render(username, energy, points, level, followers, wins, losses, clan, items, last_login)

        with tabs[1]:
            energy, points, followers, level = actions_tab.render(username, energy, points, followers, level, items)

        with tabs[2]:
            followers, items = shop_tab.render(followers, items)

        with tabs[3]:
            energy, points, followers, wins, losses = pvp_tab.render(username, clan, energy, points, followers, items, wins, losses)

        with tabs[4]:
            leaderboard_tab.render()

        with tabs[5]:
            battle_log_tab.render(username)

        with tabs[6]:
            clan_wars_tab.render()

        with tabs[7]:
            clan_history_tab.render()

        with tabs[8]:
            followers = quests_tab.render(username, followers, level)

        with tabs[9]:
            achievements_tab.render(username)

        with tabs[10]:
            followers, items = market_tab.render(username, followers, items)

        with tabs[11]:
            events_tab.render()

        with tabs[12]:
            followers = template_tab.render(username=username, followers=followers, items=items)

        # --- Save Player ---
        update_player(username, energy, points, level, followers, items, wins, losses)

# app.py - Flat Earth Wars Main App
# Version: v0.008
# Notes:
# - Persistent login across refresh using .login_state.json
# - Permanent login until manual logout
# - Fixed live stat sync across tabs
# - Added Boss table auto-init + auto-spawn

import streamlit as st, json, os
from db import (
    init_db, migrate_db, get_player, add_player, patch_old_players, update_player,
    reset_clan_war, get_player_by_credentials,
    get_active_boss, spawn_boss
)
from game_logic import regenerate_energy

# --- Import Tabs ---
from tabs import (
    profile_tab, actions_tab, shop_tab, pvp_tab,
    leaderboard_tab, battle_log_tab, clan_wars_tab,
    clan_history_tab, quests_tab, achievements_tab,
    market_tab, events_tab, template_tab, boss_battle_tab
)

LOGIN_FILE = ".login_state.json"

# --- Helpers ---
def save_login_state(username):
    with open(LOGIN_FILE, "w") as f:
        json.dump({"logged_in": True, "username": username}, f)

def load_login_state():
    if os.path.exists(LOGIN_FILE):
        try:
            with open(LOGIN_FILE, "r") as f:
                return json.load(f)
        except:
            return {"logged_in": False, "username": None}
    return {"logged_in": False, "username": None}

def clear_login_state():
    if os.path.exists(LOGIN_FILE):
        os.remove(LOGIN_FILE)

# --- Init DB ---
init_db()
migrate_db()
patch_old_players()

# --- Ensure Boss Table + Spawn a Boss ---
if not get_active_boss():
    spawn_boss("Globie Overlord 👹", hp=1000, reward_followers=200, reward_points=100)

# --- Weekly Clan War Reset ---
winner = reset_clan_war()
if winner:
    st.success(f"🎉 Weekly reset complete! {winner} received +50 Followers and +5 Energy each!")

# --- Load login state ---
if "logged_in" not in st.session_state:
    state = load_login_state()
    st.session_state.logged_in = state.get("logged_in", False)
    st.session_state.username = state.get("username", None)

# --- Login Page ---
if not st.session_state.logged_in:
    st.title("🔐 Login to Flat Earth Wars")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    # --- Login Tab ---
    with tab_login:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            player = get_player_by_credentials(login_user, login_pass)
            if player:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                save_login_state(login_user)   # ✅ persist login
                st.success(f"✅ Welcome back, {login_user}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    # --- Register Tab ---
    with tab_register:
        reg_user = st.text_input("New Username", key="reg_user")
        reg_pass = st.text_input("New Password", type="password", key="reg_pass")
        reg_clan = st.radio("Choose Your Clan", ["Flat Earthers 🌐", "Globies 🌍"])
        if st.button("Register"):
            if reg_user and reg_pass:
                add_player(reg_user, reg_pass, reg_clan)
                st.session_state.logged_in = True
                st.session_state.username = reg_user
                save_login_state(reg_user)   # ✅ auto login + persist
                st.success(f"✅ Account created! Welcome, {reg_user}!")
                st.rerun()
            else:
                st.warning("⚠️ Please enter a username and password.")

# --- Game Page ---
else:
    username = st.session_state.username
    player = get_player(username)

    if not player:
        st.error("⚠️ Player not found. Please register again.")
    else:
        try:
            (player_id, username, password, energy, points, level, followers,
             items_json, last_login, wins, losses, clan) = player
        except Exception as e:
            st.error(f"⚠️ DB mismatch: {e}")
            st.stop()

        try:
            items = json.loads(items_json) if isinstance(items_json, str) else []
        except:
            items = []

        # Energy regen
        energy, last_login = regenerate_energy(energy, level, last_login)

        # --- Sync with session_state (always current) ---
        st.session_state.energy = energy
        st.session_state.points = points
        st.session_state.followers = followers
        st.session_state.level = level
        st.session_state.wins = wins
        st.session_state.losses = losses
        st.session_state.items = items
        st.session_state.clan = clan
        st.session_state.last_login = last_login

        # --- Tabs ---
        tabs = st.tabs([
            "📋 Profile", "🎯 Actions", "🛒 Shop", "🥊 PvP",
            "🏆 Leaderboard", "📜 Battle Log", "⚔️ Clan Wars",
            "📜 Clan War History", "🎯 Quests", "🏅 Achievements",
            "💱 Market", "🌍 Events", "🆕 Template", "👹 Boss Battle" 
        ])

        with tabs[0]:
            profile_tab.render(username,
                               st.session_state.energy,
                               st.session_state.points,
                               st.session_state.level,
                               st.session_state.followers,
                               st.session_state.wins,
                               st.session_state.losses,
                               st.session_state.clan,
                               st.session_state.items,
                               st.session_state.last_login)

        with tabs[1]:
            st.session_state.energy, st.session_state.points, st.session_state.followers, st.session_state.level = actions_tab.render(
                username, st.session_state.energy, st.session_state.points, st.session_state.followers, st.session_state.level, st.session_state.items
            )

        with tabs[2]:
            st.session_state.followers, st.session_state.items = shop_tab.render(
                st.session_state.followers, st.session_state.items
            )

        with tabs[3]:
            st.session_state.energy, st.session_state.points, st.session_state.followers, st.session_state.wins, st.session_state.losses = pvp_tab.render(
                username, st.session_state.clan, st.session_state.energy, st.session_state.points, st.session_state.followers, st.session_state.items, st.session_state.wins, st.session_state.losses
            )

        with tabs[4]:
            leaderboard_tab.render()

        with tabs[5]:
            battle_log_tab.render(username)

        with tabs[6]:
            clan_wars_tab.render()

        with tabs[7]:
            clan_history_tab.render()

        with tabs[8]:
            st.session_state.followers = quests_tab.render(username, st.session_state.followers, st.session_state.level)

        with tabs[9]:
            achievements_tab.render(username)

        with tabs[10]:
            st.session_state.followers, st.session_state.items = market_tab.render(username, st.session_state.followers, st.session_state.items)

        with tabs[11]:
            events_tab.render()

        with tabs[12]:
            st.session_state.followers = template_tab.render(username=username, followers=st.session_state.followers, items=st.session_state.items)

        with tabs[13]:
            st.session_state.energy, st.session_state.points, st.session_state.followers = boss_battle_tab.render(
                username, st.session_state.energy, st.session_state.points, st.session_state.followers, st.session_state.items
            )

        # --- Save Player ---
        update_player(
            username,
            st.session_state.energy,
            st.session_state.points,
            st.session_state.level,
            st.session_state.followers,
            st.session_state.items,
            st.session_state.wins,
            st.session_state.losses
        )

        # --- Logout ---
        with st.sidebar:
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.username = None
                clear_login_state()   # ✅ clear file
                st.rerun()

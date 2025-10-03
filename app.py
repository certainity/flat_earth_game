# app.py - Flat Earth Wars Main App
# Version: v0.014
# Notes:
# - Uses EncryptedCookieManager for persistent login (works across refresh)
# - Ordered tabs: Profile, Quests, Battles, Clan, Shop, Others
# - Postgres-ready (no migrate_db needed)
# - Clan War + Patch players stubs included

import streamlit as st, json
from streamlit_cookies_manager import EncryptedCookieManager
from db import (
    init_db, get_player, add_player, patch_old_players, update_player,
    reset_clan_war, get_player_by_credentials,
    get_active_boss, spawn_boss
)
from game_logic import regenerate_energy

# --- Import Tabs ---
from tabs import (
    profile_tab, quests_tab, pvp_tab, boss_battle_tab,
    clan_wars_tab, clan_history_tab, shop_tab,
    leaderboard_tab, battle_log_tab, achievements_tab,
    market_tab, events_tab, template_tab
)

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Flat Earth Wars",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Cookies setup (persistent login) ---
cookies = EncryptedCookieManager(
    prefix="flat_earth_wars", 
    password="super-secret-key"  # ⚠️ change to a strong secret in production
)
if not cookies.ready():
    st.stop()

# --- Init DB ---
try:
    init_db()
    patch_old_players()
    db_status = "✅ Connected to Postgres Database"
except Exception as e:
    db_status = f"❌ Database connection failed: {e}"

# --- Ensure Boss Table + Spawn if Missing ---
if not get_active_boss():
    spawn_boss("Globie Overlord 👹", hp=1000, reward_followers=200, reward_points=100)

# --- Weekly Clan War Reset ---
winner = reset_clan_war()
if winner:
    st.success(f"🎉 Weekly reset complete! {winner} received +50 Followers and +5 Energy each!")

# --- Restore session from cookies ---
if "logged_in" not in st.session_state:
    if "username" in cookies and cookies["username"]:
        st.session_state.logged_in = True
        st.session_state.username = cookies["username"]
    else:
        st.session_state.logged_in = False
        st.session_state.username = None

# --- Login Page ---
if not st.session_state.logged_in:
    st.title("🔐 Login to Flat Earth Wars")
    st.caption(db_status)

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
                cookies["username"] = login_user  # ✅ persist cookie
                cookies.save()
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
                cookies["username"] = reg_user  # ✅ persist cookie
                cookies.save()
                st.success(f"✅ Account created! Welcome, {reg_user}!")
                st.rerun()
            else:
                st.warning("⚠️ Please enter a username and password.")

# --- Game Page ---
else:
    username = st.session_state.username
    player = get_player(username)

    if not player:
        st.error("⚠️ Player not found. Please login or register again.")
        st.session_state.logged_in = False
        st.session_state.username = None
        cookies["username"] = ""   # clear cookie
        cookies.save()
        st.rerun()
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

        # --- Sync with session_state ---
        st.session_state.energy = energy
        st.session_state.points = points
        st.session_state.followers = followers
        st.session_state.level = level
        st.session_state.wins = wins
        st.session_state.losses = losses
        st.session_state.items = items
        st.session_state.clan = clan
        st.session_state.last_login = last_login

        # ✅ Ensure cookie stays updated
        cookies["username"] = username
        cookies.save()

        # --- Tabs (Reordered) ---
        tabs = st.tabs([
            "📋 Profile",
            "🎯 Quests",
            "⚔️ Battles",
            "🏰 Clan",
            "🛒 Shop",
            "📜 Others"
        ])

        # --- Profile ---
        with tabs[0]:
            profile_tab.render(
                username,
                st.session_state.energy,
                st.session_state.points,
                st.session_state.level,
                st.session_state.followers,
                st.session_state.wins,
                st.session_state.losses,
                st.session_state.clan,
                st.session_state.items,
                st.session_state.last_login
            )

        # --- Quests ---
        with tabs[1]:
            st.session_state.followers = quests_tab.render(
                username, st.session_state.followers, st.session_state.level
            )

        # --- Battles (PvP + Boss + Logs) ---
        with tabs[2]:
            st.session_state.energy, st.session_state.points, st.session_state.followers, st.session_state.wins, st.session_state.losses = pvp_tab.render(
                username, st.session_state.clan, st.session_state.energy,
                st.session_state.points, st.session_state.followers,
                st.session_state.items, st.session_state.wins, st.session_state.losses
            )
            st.divider()
            st.session_state.energy, st.session_state.points, st.session_state.followers = boss_battle_tab.render(
                username, st.session_state.energy, st.session_state.points,
                st.session_state.followers, st.session_state.items
            )
            st.divider()
            battle_log_tab.render(username)

        # --- Clan (Wars + History) ---
        with tabs[3]:
            st.session_state.show_clan = st.radio("Clan Menu", ["⚔️ Clan Wars", "📜 History"])
            if st.session_state.show_clan == "⚔️ Clan Wars":
                clan_wars_tab.render()
            else:
                clan_history_tab.render()

        # --- Shop (Items + Market) ---
        with tabs[4]:
            st.session_state.followers, st.session_state.items = shop_tab.render(
                st.session_state.followers, st.session_state.items
            )
            st.divider()
            st.session_state.followers, st.session_state.items = market_tab.render(
                username, st.session_state.followers, st.session_state.items
            )

        # --- Others (leaderboard, achievements, events, template) ---
        with tabs[5]:
            leaderboard_tab.render()
            st.divider()
            achievements_tab.render(username)
            st.divider()
            events_tab.render()
            st.divider()
            st.session_state.followers = template_tab.render(
                username=username,
                followers=st.session_state.followers,
                items=st.session_state.items
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
            st.caption(db_status)
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.username = None
                cookies["username"] = ""  # clear cookie
                cookies.save()
                st.rerun()

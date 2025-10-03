# boss_battle_tab.py - Boss Battle Feature
# Version: v0.001
# Notes:
# - Inspired by "Kingdoms at War" style epic battles
# - Allows all players to attack a global boss
# - Shows HP bar, rewards when defeated

import streamlit as st
from db import get_active_boss, damage_boss, spawn_boss, update_player

def render(username, energy, points, followers, items):
    st.subheader("👹 Boss Battle")

    # Fetch current boss
    boss = get_active_boss()

    if not boss:
        st.warning("⚠️ No boss is currently active.")
        if st.button("⚡ Spawn New Boss (Admin Only)"):
            spawn_boss()
            st.success("A new boss has spawned! 👹")
            st.rerun()
        return energy, points, followers

    boss_id, name, max_hp, hp, reward_followers, reward_points = boss

    # Boss status
    st.write(f"**{name}** - HP: {hp}/{max_hp}")
    st.progress(hp / max_hp)

    if hp <= 0:
        st.success(f"🎉 {name} has been defeated! Every participant earns "
                   f"{reward_followers} Followers and {reward_points} Points!")
        # Reward current player (simple distribution)
        followers += reward_followers
        points += reward_points
        update_player(username, energy, points, 1, followers, items)
        return energy, points, followers

    # Attack button
    if st.button("⚔️ Attack Boss (-2 Energy)"):
        if energy < 2:
            st.warning("⚠️ Not enough energy to attack!")
        else:
            dmg = 50  # flat damage for now, can be scaled later
            energy -= 2
            st.success(f"💥 You hit {name} for {dmg} damage!")
            damage_boss(dmg)

            # Save after attack
            update_player(username, energy, points, 1, followers, items)
            st.rerun()

    return energy, points, followers

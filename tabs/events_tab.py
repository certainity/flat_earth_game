# events_tab.py - Global Events
# Version: v0.002
# Notes:
# - Fixed indexing for db.events table
# - Displays event name, description, and effect correctly

import streamlit as st
from db import get_active_event

def render():
    st.subheader("🌍 Global Events")
    event = get_active_event()
    if event:
        _, name, description, effect, active, ts = event
        st.write(f"**{name}**")
        st.caption(description)
        st.info(f"✨ Effect: {effect}")
    else:
        st.info("No active events right now.")

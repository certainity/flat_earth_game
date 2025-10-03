# events_tab.py - Global Events
# Version: v0.001
# Notes: Shows special events from db.events.

import streamlit as st
from db import get_active_event

def render():
    st.subheader("🌍 Global Events")
    event = get_active_event()
    if event:
        st.write(f"**{event[0]}**: {event[1]}")
        st.info(f"Effect: {event[2]}")
    else:
        st.info("No active events right now.")

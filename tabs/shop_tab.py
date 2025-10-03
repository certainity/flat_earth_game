import streamlit as st
from shop import shop_items, buy_item, upgrade_item, upgrade_paths

def render(followers, items):
    st.subheader("🛒 Item Shop")

    for item, data in shop_items.items():
        if st.button(f"Buy {item} ({data['cost']} followers)", key=f"buy{item}"):
            followers, items, msg = buy_item(item, followers, items)
            if "✅" in msg: st.success(msg)
            else: st.warning(msg)

    st.divider()
    st.subheader("🔧 Upgrade Items")

    if items:
        upgrade_choice = st.selectbox("Choose item to upgrade", items)
        if upgrade_choice in upgrade_paths:
            target = upgrade_paths[upgrade_choice]["target"]
            cost = upgrade_paths[upgrade_choice]["cost"]
            st.write(f"➡️ Upgrade {upgrade_choice} → {target} ({cost} followers)")
            if st.button(f"Upgrade {upgrade_choice}", key=f"upgrade{upgrade_choice}"):
                followers, items, msg = upgrade_item(upgrade_choice, followers, items)
                if "✨" in msg: st.success(msg)
                else: st.warning(msg)
        else:
            st.info("This item cannot be upgraded.")
    else:
        st.info("No items available to upgrade.")

    return followers, items

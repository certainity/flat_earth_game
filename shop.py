# shop.py - Item Shop & Upgrades
# Version: v0.002
# Notes:
# - Fixed bug: items always treated as list
# - Safe JSON handling
# - Upgrade paths supported

import json

# --- Shop Items ---
shop_items = {
    "Meme Book 📖": {"cost": 30},
    "Telescope 🔭": {"cost": 50},
    "Laptop 💻": {"cost": 80},
    "Banner 🚩": {"cost": 40}
}

# --- Upgrade Paths ---
upgrade_paths = {
    "Meme Book 📖": {"target": "Advanced Meme Book 📚", "cost": 60},
    "Telescope 🔭": {"target": "Space Telescope 🛰️", "cost": 100},
    "Laptop 💻": {"target": "Supercomputer 🖥️", "cost": 150},
    "Banner 🚩": {"target": "War Banner 🏴", "cost": 90}
}


# --- Buy Item ---
def buy_item(item, followers, items):
    # Normalize items
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except:
            items = []
    elif not isinstance(items, list):
        items = []

    cost = shop_items[item]["cost"]
    if followers < cost:
        return followers, items, f"⚠️ Not enough followers to buy {item}."

    if item in items:
        return followers, items, f"⚠️ You already own {item}."

    followers -= cost
    items.append(item)
    return followers, items, f"✅ Bought {item}!"


# --- Upgrade Item ---
def upgrade_item(item, followers, items):
    # Normalize items
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except:
            items = []
    elif not isinstance(items, list):
        items = []

    if item not in upgrade_paths:
        return followers, items, f"⚠️ {item} cannot be upgraded."

    path = upgrade_paths[item]
    target, cost = path["target"], path["cost"]

    if followers < cost:
        return followers, items, f"⚠️ Not enough followers to upgrade {item}."

    if target in items:
        return followers, items, f"⚠️ You already upgraded to {target}."

    # Perform upgrade
    followers -= cost
    items.remove(item)
    items.append(target)

    return followers, items, f"✨ {item} upgraded → {target}!"

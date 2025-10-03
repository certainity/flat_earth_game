# shop_tab.py - Item Shop UI
# Version: v0.001
# Notes: Buy/Upgrade items from shop.py

# --- Shop Items ---
shop_items = {
    "Meme Book 📖": {"cost": 30, "effect": {"points": 10, "followers": 5}},
    "Telescope 🔭": {"cost": 50, "effect": {"debate_bonus": 10}},
    "Laptop 💻": {"cost": 80, "effect": {"meme_bonus": 15}},
    "Banner 🚩": {"cost": 40, "effect": {"followers": 20}},
}

# --- Upgrade Map ---
upgrade_paths = {
    "Meme Book 📖": {"target": "Meme Encyclopedia 📚", "cost": 50},
    "Telescope 🔭": {"target": "Golden Telescope ✨", "cost": 75},
    "Laptop 💻": {"target": "Supercomputer 🖥️", "cost": 120},
    "Banner 🚩": {"target": "Mega Banner 🏴", "cost": 60},
}

# --- Buy Item ---
def buy_item(item, followers, items):
    if item not in shop_items:
        return followers, items, "⚠️ Item not found."
    if followers < shop_items[item]["cost"]:
        return followers, items, "⚠️ Not enough followers."

    followers -= shop_items[item]["cost"]
    items.append(item)
    return followers, items, f"✅ You bought {item}!"

# --- Upgrade Item ---
def upgrade_item(item, followers, items):
    if item not in items:
        return followers, items, "⚠️ You don't own this item."

    if item not in upgrade_paths:
        return followers, items, "⚠️ This item cannot be upgraded."

    upgrade_info = upgrade_paths[item]
    if followers < upgrade_info["cost"]:
        return followers, items, f"⚠️ Not enough followers (Need {upgrade_info['cost']})."

    # Do the upgrade
    followers -= upgrade_info["cost"]
    items.remove(item)
    items.append(upgrade_info["target"])

    return followers, items, f"✨ {item} upgraded into {upgrade_info['target']}!"

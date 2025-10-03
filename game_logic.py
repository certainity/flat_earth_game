# game_logic.py - Core Game Mechanics
# Version: v0.002
# Notes:
# - Added safe_items() to fix JSON string/method issues
# - Improved PvP battle with consistent outcomes
# - Items always checked safely

import random, time, json

# --- Helpers ---
def safe_items(items):
    """Ensure items is always a Python list."""
    if isinstance(items, str):  # JSON string from DB
        try:
            return json.loads(items)
        except:
            return []
    elif isinstance(items, list):  # already a list
        return items
    return []  # fallback


# --- Energy ---
def regenerate_energy(energy, level, last_login):
    regen_rate = 120  # 1 energy every 120s
    now = time.time()
    elapsed = now - last_login
    regenerated = int(elapsed // regen_rate)
    if regenerated > 0:
        energy = min(10 + level * 5, energy + regenerated)
        last_login = now
    return energy, last_login


# --- Actions ---
def post_meme(energy, points, followers, items):
    items = safe_items(items)

    if energy <= 0:
        return energy, points, followers, "⚠️ No energy left!"

    gain = random.randint(5, 15)
    follower_gain = random.randint(1, 5)

    if "Shades 🕶️" in items:
        gain = int(gain * 1.1)
    if "Rocket Poster 🚀" in items:
        gain += 50

    points += gain
    followers += follower_gain
    energy -= 1
    return energy, points, followers, f"📢 Meme posted! +{gain} points, +{follower_gain} followers"


def debate_globie(energy, points, followers, items):
    items = safe_items(items)

    if energy < 2:
        return energy, points, followers, "⚠️ Not enough energy!"

    outcome = random.choice(["win", "lose"])
    if "Flat Map 🧭" in items and random.random() < 0.2:
        outcome = "win"

    if outcome == "win":
        points += 25
        followers += 10
        result = "⚔️ You WON the debate! +25 points, +10 followers"
    else:
        points -= 10
        result = "💢 You lost the debate... -10 points"

    energy -= 2
    return energy, points, followers, result


# --- Leveling ---
def level_up(points, level, energy):
    if points >= level * 100:
        level += 1
        energy += 5
        return level, energy, f"🎉 Congrats! You reached Level {level}!"
    return level, energy, None


# --- PvP Battles ---
def pvp_battle(attacker, defender):
    """
    attacker & defender are dicts:
    {"username": str, "points": int, "followers": int, "items": list|json}
    Returns: ("win"/"lose", details dict)
    """
    attacker_items = safe_items(attacker.get("items", []))
    defender_items = safe_items(defender.get("items", []))

    atk_score = attacker["points"] + random.randint(0, 20)
    def_score = defender["points"] + random.randint(0, 20)

    # --- Item boosts ---
    if "Rocket Poster 🚀" in attacker_items:
        atk_score += 30
    if "Shades 🕶️" in attacker_items:
        atk_score += 10
    if "Flat Map 🧭" in defender_items:
        def_score += 15

    # --- Outcome ---
    if atk_score >= def_score:
        steal = max(1, int(defender["followers"] * 0.1))
        return "win", {
            "followers_gain": steal,
            "points_gain": 20,
            "message": f"🏆 Victory! You stole {steal} followers and gained 20 points."
        }
    else:
        penalty = 15
        return "lose", {
            "followers_loss": 0,
            "points_loss": penalty,
            "message": f"💢 Defeat! You lost {penalty} points."
        }

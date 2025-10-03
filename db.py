# db.py - Database Manager for Flat Earth Wars
# Version: v0.003
# Notes:
# - Added password field to players table
# - Added persistent login support
# - Added Boss Battles (with init inside init_db)
# - Kept all existing systems (quests, clans, events, market, etc.)

import sqlite3
import json
import time


# --- Init DB ---
def init_db():
    conn = sqlite3.connect("game.db")
    c = conn.cursor()

    # --- Players table (with password) ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            energy INTEGER,
            points INTEGER,
            level INTEGER,
            followers INTEGER,
            items TEXT,
            last_login REAL,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            clan TEXT DEFAULT 'Flat Earthers 🌐'
        )
    """)

    # --- Battles ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS battles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attacker TEXT,
            defender TEXT,
            outcome TEXT,
            followers_change INTEGER,
            points_change INTEGER,
            timestamp REAL
        )
    """)

    # --- Settings ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # --- Clan history ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS clan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clan TEXT,
            timestamp REAL
        )
    """)

    # --- Quests ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            quest_type TEXT,
            progress INTEGER,
            goal INTEGER,
            reward TEXT,
            completed INTEGER DEFAULT 0,
            timestamp REAL
        )
    """)

    # --- Achievements ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            badge TEXT,
            achieved INTEGER DEFAULT 0,
            timestamp REAL
        )
    """)

    # --- Market ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS market (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller TEXT,
            item TEXT,
            price INTEGER,
            status TEXT DEFAULT 'active',
            buyer TEXT,
            timestamp REAL
        )
    """)

    # --- Events ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            effect TEXT,
            active INTEGER DEFAULT 0,
            timestamp REAL
        )
    """)

    conn.commit()
    conn.close()

    # ✅ Ensure Boss table also exists
    init_boss()


def migrate_db():
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    try: c.execute("ALTER TABLE players ADD COLUMN password TEXT DEFAULT ''")
    except: pass
    try: c.execute("ALTER TABLE players ADD COLUMN wins INTEGER DEFAULT 0")
    except: pass
    try: c.execute("ALTER TABLE players ADD COLUMN losses INTEGER DEFAULT 0")
    except: pass
    try: c.execute("ALTER TABLE players ADD COLUMN clan TEXT DEFAULT 'Flat Earthers 🌐'")
    except: pass
    conn.commit()
    conn.close()


# --- Player Management ---
def get_player(username):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT * FROM players WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row


def get_player_by_credentials(username, password):
    """Validate login by checking username + password"""
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT * FROM players WHERE username=? AND password=?", (username, password))
    row = c.fetchone()
    conn.close()
    return row


def add_player(username, password, clan):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO players
        (username, password, energy, points, level, followers, items, last_login, wins, losses, clan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, password, 10, 0, 1, 0, json.dumps([]), time.time(), 0, 0, clan))
    conn.commit(); conn.close()


def update_player(username, energy, points, level, followers, items, wins=None, losses=None):
    conn = sqlite3.connect("game.db"); c = conn.cursor()

    # --- SAFETY FIX ---
    try:
        if not isinstance(items, (list, dict, str)):
            items = []
        if isinstance(items, str):
            json.loads(items)  # valid json? ok
        items_str = json.dumps(items) if not isinstance(items, str) else items
    except Exception:
        items_str = "[]"

    query = "UPDATE players SET energy=?, points=?, level=?, followers=?, items=?, last_login=?"
    params = [energy, points, level, followers, items_str, time.time()]
    if wins is not None:
        query += ", wins=?"; params.append(wins)
    if losses is not None:
        query += ", losses=?"; params.append(losses)
    query += " WHERE username=?"; params.append(username)
    c.execute(query, tuple(params))
    conn.commit(); conn.close()



def get_leaderboard(order_by="points"):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    if order_by not in ["points","followers","level","wins","losses"]:
        order_by="points"
    c.execute(f"""
        SELECT username, level, points, followers, items, wins, losses, clan
        FROM players ORDER BY {order_by} DESC LIMIT 20
    """)
    rows = c.fetchall()
    conn.close()
    return rows


# --- Battles ---
def add_battle(attacker, defender, outcome, followers_change, points_change):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("""
        INSERT INTO battles (attacker, defender, outcome, followers_change, points_change, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (attacker, defender, outcome, followers_change, points_change, time.time()))
    conn.commit(); conn.close()


def get_battle_log(username):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("""
        SELECT attacker, defender, outcome, followers_change, points_change, timestamp
        FROM battles WHERE attacker=? OR defender=?
        ORDER BY timestamp DESC LIMIT 20
    """, (username, username))
    rows = c.fetchall()
    conn.close()
    return rows


# --- Clan Wars ---
def get_clan_stats():
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT clan, SUM(points), COUNT(*), SUM(wins), SUM(losses) FROM players GROUP BY clan")
    rows = c.fetchall(); conn.close(); return rows


def get_setting(key):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone(); conn.close()
    return row[0] if row else None


def set_setting(key, value):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (key,str(value)))
    conn.commit(); conn.close()


def add_clan_history(clan):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("INSERT INTO clan_history (clan, timestamp) VALUES (?,?)", (clan,time.time()))
    conn.commit(); conn.close()


def get_clan_history(limit=10):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT clan, timestamp FROM clan_history ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall(); conn.close(); return rows


def get_clan_streak():
    history = get_clan_history(20)
    if not history: return None,0
    last_clan = history[0][0]; streak=1
    for clan, ts in history[1:]:
        if clan==last_clan: streak+=1
        else: break
    return last_clan, streak


def reset_clan_war():
    last_reset = get_setting("last_reset"); now = time.time()
    if last_reset and now - float(last_reset) < 7*24*3600: return None
    stats = get_clan_stats()
    if not stats: return None
    top_clan = max(stats, key=lambda x: x[1]); winning_clan = top_clan[0]
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT username, energy, followers FROM players WHERE clan=?", (winning_clan,))
    players = c.fetchall()
    for username, energy, followers in players:
        c.execute("UPDATE players SET energy=?, followers=? WHERE username=?",
                  (energy+5, followers+50, username))
    conn.commit(); conn.close()
    add_clan_history(winning_clan); set_setting("last_reset", now)
    return winning_clan


# --- Quests ---
def add_quest(username, quest_type, goal, reward):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("""INSERT INTO quests (username, quest_type, progress, goal, reward, completed, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (username, quest_type, 0, goal, reward, 0, time.time()))
    conn.commit(); conn.close()


def get_quests(username):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT id, quest_type, progress, goal, reward, completed FROM quests WHERE username=?", (username,))
    rows = c.fetchall(); conn.close(); return rows


def update_quest_progress(qid, amount=1):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("UPDATE quests SET progress=progress+? WHERE id=?", (amount,qid))
    conn.commit(); conn.close()


def complete_quest(qid):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("UPDATE quests SET completed=1 WHERE id=?", (qid,))
    conn.commit(); conn.close()


def generate_daily_quests(username, level=1):
    """Generate daily quests for a player if 24h passed"""
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (f"last_quests_{username}",))
    row = c.fetchone(); now = time.time()
    if row and now - float(row[0]) < 24*3600:
        conn.close(); return

    # Clear old quests
    c.execute("DELETE FROM quests WHERE username=?", (username,))

    # Add new quests
    quest_list = [
        ("meme", min(3 + level//2, 10), str(10+2*level)),
        ("debate", min(2 + level//3, 8), str(15+3*level)),
        ("pvp", min(1 + level//4, 5), str(25+5*level))
    ]
    for qtype, goal, reward in quest_list:
        c.execute("""INSERT INTO quests (username,quest_type,progress,goal,reward,completed,timestamp)
                     VALUES (?,?,?,?,?,?,?)""",
                  (username,qtype,0,goal,reward,0,now))

    c.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)",
              (f"last_quests_{username}", str(now)))
    conn.commit(); conn.close()


# --- Achievements ---
def add_achievement(username, badge):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("INSERT INTO achievements (username,badge,achieved,timestamp) VALUES (?,?,1,?)",
              (username,badge,time.time()))
    conn.commit(); conn.close()


def get_achievements(username):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT badge,achieved,timestamp FROM achievements WHERE username=?", (username,))
    rows = c.fetchall(); conn.close(); return rows


# --- Market ---
def list_item(seller, item, price):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("INSERT INTO market (seller,item,price,status,timestamp) VALUES (?,?,?,?,?)",
              (seller,item,price,'active',time.time()))
    conn.commit(); conn.close()


def get_market():
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT id,seller,item,price,status,buyer FROM market WHERE status='active'")
    rows = c.fetchall(); conn.close(); return rows


def buy_market_item(mid, buyer):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("UPDATE market SET status='sold', buyer=? WHERE id=?", (buyer, mid))
    conn.commit(); conn.close()


# --- Events ---
def add_event(name, description, effect):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("INSERT INTO events (name,description,effect,active,timestamp) VALUES (?,?,?,?,?)",
              (name,description,effect,1,time.time()))
    conn.commit(); conn.close()


def get_active_event():
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT name,description,effect FROM events WHERE active=1 ORDER BY timestamp DESC LIMIT 1")
    row = c.fetchone(); conn.close(); return row


# --- Patch Old Players ---
def patch_old_players():
    """Fix old player records so they match the new schema (items as JSON string, last_login set)."""
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("SELECT username, items, last_login FROM players")
    rows = c.fetchall()

    for username, items, last_login in rows:
        # Fix items
        try:
            if not isinstance(items, str):  # old bug stored it as float/int
                items = "[]"
            else:
                json.loads(items)  # check if valid JSON
        except Exception:
            items = "[]"

        # Fix last_login
        if not last_login or isinstance(last_login, str):
            last_login = time.time()

        c.execute("UPDATE players SET items=?, last_login=? WHERE username=?",
                  (items, last_login, username))

    conn.commit()
    conn.close()
    print("✅ Old player records patched!")


# --- Boss Battles ---
def init_boss():
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS boss (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            max_hp INTEGER,
            hp INTEGER,
            reward_followers INTEGER,
            reward_points INTEGER,
            active INTEGER DEFAULT 1
        )
    """)
    conn.commit(); conn.close()


def get_active_boss():
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("SELECT id, name, max_hp, hp, reward_followers, reward_points FROM boss WHERE active=1 LIMIT 1")
    boss = c.fetchone(); conn.close()
    return boss


def spawn_boss(name="Globie Overlord 👹", hp=1000, reward_followers=200, reward_points=100):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("DELETE FROM boss")  # Only 1 active boss
    c.execute("INSERT INTO boss (name, max_hp, hp, reward_followers, reward_points, active) VALUES (?,?,?,?,?,1)",
              (name, hp, hp, reward_followers, reward_points))
    conn.commit(); conn.close()


def damage_boss(dmg):
    conn = sqlite3.connect("game.db"); c = conn.cursor()
    c.execute("UPDATE boss SET hp = MAX(0, hp-?) WHERE active=1", (dmg,))
    conn.commit(); conn.close()

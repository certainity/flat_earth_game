# db.py - Database Manager for Flat Earth Wars
# Version: v0.013
# Notes:
# - Postgres + SQLAlchemy (Render + Codespaces ready)
# - Full helpers for players, battles, quests, achievements, market, events, clan, boss
# - Includes stubs for reset/patch (for backward compatibility)

import os, json, time
from sqlalchemy import (
    create_engine, Table, Column, Integer, String, Float,
    Text, MetaData, select, insert, update, delete, func
)
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

# --- Load .env for local dev ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL not set. Please add it to your .env or Render.")

# Normalize for psycopg2
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+psycopg2" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Ensure sslmode
if "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()

# --- Tables ---
players = Table(
    "players", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),
    Column("password", String),
    Column("energy", Integer, default=10),
    Column("points", Integer, default=0),
    Column("level", Integer, default=1),
    Column("followers", Integer, default=0),
    Column("items", Text, default="[]"),
    Column("last_login", Float, default=time.time),
    Column("wins", Integer, default=0),
    Column("losses", Integer, default=0),
    Column("clan", String, default="Flat Earthers 🌐"),
)

battles = Table(
    "battles", metadata,
    Column("id", Integer, primary_key=True),
    Column("attacker", String),
    Column("defender", String),
    Column("outcome", String),
    Column("followers_change", Integer),
    Column("points_change", Integer),
    Column("timestamp", Float, default=time.time),
)

quests = Table(
    "quests", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String),
    Column("quest_type", String),
    Column("progress", Integer),
    Column("goal", Integer),
    Column("reward", String),
    Column("completed", Integer, default=0),
    Column("timestamp", Float, default=time.time),
)

achievements = Table(
    "achievements", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String),
    Column("badge", String),
    Column("achieved", Integer, default=0),
    Column("timestamp", Float, default=time.time),
)

market = Table(
    "market", metadata,
    Column("id", Integer, primary_key=True),
    Column("seller", String),
    Column("item", String),
    Column("price", Integer),
    Column("status", String, default="active"),
    Column("buyer", String),
    Column("timestamp", Float, default=time.time),
)

events = Table(
    "events", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("description", String),
    Column("effect", String),
    Column("active", Integer, default=0),
    Column("timestamp", Float, default=time.time),
)

clan_history = Table(
    "clan_history", metadata,
    Column("id", Integer, primary_key=True),
    Column("clan", String),
    Column("timestamp", Float),
)

boss = Table(
    "boss", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("max_hp", Integer),
    Column("hp", Integer),
    Column("reward_followers", Integer),
    Column("reward_points", Integer),
    Column("active", Integer, default=1),
)

# --- Init ---
def init_db():
    metadata.create_all(engine)

# --- Player ---
def get_player(username):
    with engine.begin() as conn:
        return conn.execute(select(players).where(players.c.username == username)).fetchone()

def get_player_by_credentials(username, password):
    with engine.begin() as conn:
        return conn.execute(
            select(players).where(
                (players.c.username == username) & (players.c.password == password)
            )
        ).fetchone()

def add_player(username, password, clan):
    with engine.begin() as conn:
        try:
            conn.execute(insert(players).values(
                username=username, password=password,
                energy=10, points=0, level=1, followers=0,
                items="[]", last_login=time.time(),
                wins=0, losses=0, clan=clan
            ))
        except IntegrityError:
            pass

def update_player(username, energy, points, level, followers, items, wins, losses):
    # Ensure items is always a JSON string
    try:
        if isinstance(items, (list, dict)):
            items = json.dumps(items)
        elif isinstance(items, str):
            # already JSON string
            pass
        else:
            # fallback in case items is wrong type (e.g. method, None, int)
            items = "[]"
    except Exception:
        items = "[]"

    with engine.begin() as conn:
        conn.execute(update(players).where(players.c.username == username).values(
            energy=energy,
            points=points,
            level=level,
            followers=followers,
            items=items,
            wins=wins,
            losses=losses,
            last_login=time.time()
        ))

def get_leaderboard(order_by="points"):
    if order_by not in ["points", "followers", "level", "wins", "losses"]:
        order_by = "points"
    with engine.begin() as conn:
        return conn.execute(
            select(players).order_by(getattr(players.c, order_by).desc()).limit(20)
        ).fetchall()

# --- Battles ---
def add_battle(attacker, defender, outcome, followers_change, points_change):
    with engine.begin() as conn:
        conn.execute(insert(battles).values(
            attacker=attacker, defender=defender, outcome=outcome,
            followers_change=followers_change, points_change=points_change,
            timestamp=time.time()
        ))

def get_battle_log(username):
    with engine.begin() as conn:
        return conn.execute(
            select(battles).where(
                (battles.c.attacker == username) | (battles.c.defender == username)
            ).order_by(battles.c.timestamp.desc()).limit(20)
        ).fetchall()

# --- Quests ---
def get_quests(username):
    with engine.begin() as conn:
        return conn.execute(
            select(quests).where(quests.c.username == username)
        ).fetchall()

def add_quest(username, quest_type, goal, reward):
    with engine.begin() as conn:
        conn.execute(insert(quests).values(
            username=username, quest_type=quest_type,
            progress=0, goal=goal, reward=reward,
            completed=0, timestamp=time.time()
        ))

def update_quest_progress(quest_id, progress, completed=0):
    with engine.begin() as conn:
        conn.execute(
            update(quests).where(quests.c.id == quest_id).values(
                progress=progress, completed=completed
            )
        )

def complete_quest(quest_id):
    with engine.begin() as conn:
        conn.execute(
            update(quests).where(quests.c.id == quest_id).values(completed=1)
        )

# --- Achievements ---
def get_achievements(username):
    with engine.begin() as conn:
        return conn.execute(
            select(achievements).where(achievements.c.username == username)
        ).fetchall()

def add_achievement(username, badge):
    with engine.begin() as conn:
        conn.execute(insert(achievements).values(
            username=username, badge=badge, achieved=1, timestamp=time.time()
        ))

# --- Market ---
def get_market_items():
    with engine.begin() as conn:
        return conn.execute(select(market).where(market.c.status == "active")).fetchall()

def add_market_item(seller, item, price):
    with engine.begin() as conn:
        conn.execute(insert(market).values(
            seller=seller, item=item, price=price,
            status="active", buyer=None, timestamp=time.time()
        ))

def buy_market_item(item_id, buyer):
    with engine.begin() as conn:
        conn.execute(
            update(market).where(market.c.id == item_id).values(
                status="sold", buyer=buyer
            )
        )

# --- Events ---
def get_events():
    with engine.begin() as conn:
        return conn.execute(select(events)).fetchall()

def activate_event(event_id, active=1):
    with engine.begin() as conn:
        conn.execute(
            update(events).where(events.c.id == event_id).values(active=active)
        )

# --- Boss ---
def get_active_boss():
    with engine.begin() as conn:
        return conn.execute(select(boss).where(boss.c.active == 1)).fetchone()

def spawn_boss(name="Globie Overlord 👹", hp=1000, reward_followers=200, reward_points=100):
    with engine.begin() as conn:
        conn.execute(delete(boss))  # only 1 active
        conn.execute(insert(boss).values(
            name=name, max_hp=hp, hp=hp,
            reward_followers=reward_followers,
            reward_points=reward_points, active=1
        ))

def damage_boss(dmg):
    with engine.begin() as conn:
        conn.execute(
            update(boss).where(boss.c.active == 1).values(
                hp=func.greatest(boss.c.hp - dmg, 0)
            )
        )

# --- Clan ---
def get_clan_stats():
    with engine.begin() as conn:
        return conn.execute(
            select(
                players.c.clan,
                func.count(players.c.id).label("members"),
                func.sum(players.c.followers).label("followers"),
                func.sum(players.c.wins).label("wins"),
                func.sum(players.c.losses).label("losses"),
            ).group_by(players.c.clan)
        ).fetchall()

def get_clan_history(limit=20):
    with engine.begin() as conn:
        return conn.execute(
            select(clan_history).order_by(clan_history.c.timestamp.desc()).limit(limit)
        ).fetchall()

def add_clan_history(clan_name):
    with engine.begin() as conn:
        conn.execute(insert(clan_history).values(
            clan=clan_name, timestamp=time.time()
        ))

def get_clan_streak(clan_name):
    with engine.begin() as conn:
        rows = conn.execute(
            select(clan_history).order_by(clan_history.c.timestamp.desc())
        ).fetchall()
        streak = 0
        for row in rows:
            if row.clan == clan_name:
                streak += 1
            else:
                break
        return streak

# --- Compatibility Stubs ---
def patch_old_players():
    return True

def reset_clan_war():
    return None

# --- Daily Quests ---
def generate_daily_quests(username, level):
    """Generate daily quests based on player level."""
    with engine.begin() as conn:
        # Check if player already has quests today
        existing = conn.execute(
            select(quests).where(quests.c.username == username)
        ).fetchall()

        if not existing:
            # Example: scale quest goal with level
            conn.execute(insert(quests).values(
                username=username,
                quest_type="battle",
                progress=0,
                goal=3 + level,  # harder for higher level
                reward=10 + (2 * level),
                completed=0,
                timestamp=time.time()
            ))

# --- Market ---
def list_item(seller, item, price):
    """List an item for sale in the market."""
    with engine.begin() as conn:
        conn.execute(insert(market).values(
            seller=seller,
            item=item,
            price=price,
            status="active",
            buyer=None,
            timestamp=time.time()
        ))

def get_market():
    """Fetch all active items from the market."""
    with engine.begin() as conn:
        return conn.execute(
            select(market).where(market.c.status == "active").order_by(market.c.timestamp.desc())
        ).fetchall()

def buy_market_item(item_id, buyer):
    """Mark an item as bought and assign buyer."""
    with engine.begin() as conn:
        conn.execute(
            update(market)
            .where(market.c.id == item_id)
            .values(status="sold", buyer=buyer)
        )
# --- Events ---
# --- Events ---
def get_active_event():
    """Return the currently active global event (if any)."""
    with engine.begin() as conn:
        return conn.execute(
            select(events).where(events.c.active == 1).limit(1)
        ).fetchone()

def add_event(name, description, effect, active=1):
    """Create a new event. Set active=1 to make it current."""
    with engine.begin() as conn:
        if active == 1:
            # deactivate old events
            conn.execute(update(events).values(active=0))
        conn.execute(insert(events).values(
            name=name,
            description=description,
            effect=effect,
            active=active,
            timestamp=time.time()
        ))

def deactivate_event(event_id):
    """Deactivate a specific event by ID."""
    with engine.begin() as conn:
        conn.execute(
            update(events)
            .where(events.c.id == event_id)
            .values(active=0)
        )

import sqlite3
from datetime import datetime

DB_PATH = "bgs.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS pets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            rarity      TEXT    NOT NULL,   -- Limited | Secret | Legendary | Rare
            value       REAL    NOT NULL DEFAULT 0,
            shiny_value REAL,
            note        TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS value_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id      INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
            pet_name    TEXT    NOT NULL,
            old_value   REAL    NOT NULL,
            new_value   REAL    NOT NULL,
            old_shiny   REAL,
            new_shiny   REAL,
            changed_by  TEXT    NOT NULL DEFAULT 'admin',
            reason      TEXT,
            changed_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS admin_users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)

    conn.commit()
    conn.close()


# ── Seed with all BGS pets at value 0 ────────────────────────────────────────
SEED_PETS = [
    # (name, rarity, value, shiny_value, note)
    ("Giant Robot",       "Limited",   0, 0,    "Only 7 in existence"),
    ("Leviathan",         "Limited",   0, None, None),
    ("Demonator",         "Limited",   0, 0,    None),
    ("Sinister Lord",     "Limited",   0, 0,    None),
    ("Robot 2.0",         "Limited",   0, 0,    None),
    ("Radiance",          "Limited",   0, 0,    None),
    ("Easter Basket",     "Limited",   0, 0,    None),
    ("Trophy",            "Limited",   0, 0,    None),
    ("Lord Shock",        "Limited",   0, 0,    None),
    ("Pot O' Gold",       "Limited",   0, 0,    None),
    ("Kraken",            "Limited",   0, 0,    None),
    ("Soul Heart",        "Limited",   0, 0,    None),
    ("Immortal One",      "Limited",   0, 0,    None),
    ("Patriotic Robot",   "Limited",   0, 0,    None),
    ("Wolflord",          "Limited",   0, 0,    None),
    ("Holy Bell",         "Limited",   0, 0,    None),
    ("Frost Sentinel",    "Limited",   0, 0,    None),
    ("Duality",           "Limited",   0, 0,    None),
    ("Giant C. Chicken",  "Limited",   0, 0,    None),
    ("Immortal Trophy",   "Limited",   0, 0,    None),
    ("Shard",             "Limited",   0, 0,    None),
    ("Plasma Wolflord",   "Limited",   0, 0,    None),
    ("Pyramidium",        "Limited",   0, 0,    None),
    ("Ultimate Clover",   "Limited",   0, 0,    None),
    ("Ultimate Trophy",   "Limited",   0, 0,    None),
    ("Dark Guardian",     "Limited",   0, 0,    None),
    ("Eternal Heart",     "Limited",   0, 0,    None),
    ("Rainbow Gryphon",   "Limited",   0, 0,    None),
    ("Rainbow DogCat",    "Limited",   0, 0,    None),
    ("Crystal Teddy",     "Limited",   0, 0,    None),
    ("King Doggy",        "Secret",    0, 0,    None),
    ("Fire Champion",     "Secret",    0, 0,    None),
    ("Dark Champion",     "Secret",    0, 0,    None),
    ("Giant Pearl",       "Secret",    0, 0,    None),
    ("Gryphon",           "Secret",    0, 0,    None),
    ("Fallen Angel",      "Secret",    0, 0,    None),
    ("Sea Star",          "Secret",    0, 0,    None),
    ("OwOLord",           "Secret",    0, 0,    None),
    ("Dogcat",            "Secret",    0, 0,    None),
    ("OG Overlord",       "Secret",    0, 0,    None),
    ("2018 Overlord",     "Legendary", 0, 0,    None),
    ("Diamond Overlord",  "Legendary", 0, 0,    None),
    ("Valentium",         "Legendary", 0, 0,    None),
    ("Patriotic Penguin", "Legendary", 0, 0,    None),
    ("Chocolate Bunny",   "Legendary", 0, 0,    None),
    ("Super Hexarium",    "Legendary", 0, 0,    None),
    ("Platinum Overlord", "Legendary", 0, 0,    None),
    ("Queen Overlord",    "Legendary", 0, 0,    None),
    ("Radiant Protector", "Legendary", 0, 0,    None),
    ("Lucky Overlord",    "Legendary", 0, 0,    None),
    ("Summer Cerberus",   "Legendary", 0, 0,    None),
    ("Easter Guardian",   "Legendary", 0, 0,    None),
    ("Iridium Prisma",    "Legendary", 0, 0,    None),
    ("Glitch",            "Legendary", 0, 0,    None),
    ("Toxic Shock",       "Legendary", 0, 0,    None),
    ("Galantic Bunny",    "Legendary", 0, 0,    None),
    ("Diamond Tamer",     "Legendary", 0, 0,    None),
    ("King Snowman",      "Legendary", 0, 0,    None),
    ("Dark Omen",         "Legendary", 0, 0,    None),
    ("Valentine Shock",   "Legendary", 0, 0,    None),
    ("Arctic Fox",        "Rare",      0, 0,    None),
    ("Coral Panda",       "Rare",      0, 0,    None),
    ("Crystal Dragon",    "Rare",      0, 0,    None),
    ("Amethyst Golem",    "Rare",      0, 0,    None),
    ("Clown Dragon",      "Rare",      0, 0,    None),
    ("Dark Bat",          "Rare",      0, 0,    None),
]


def seed_db():
    """Insert pets only if they don't already exist."""
    conn = get_conn()
    cur = conn.cursor()
    for name, rarity, value, shiny, note in SEED_PETS:
        cur.execute(
            """
            INSERT OR IGNORE INTO pets (name, rarity, value, shiny_value, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, rarity, value, shiny, note),
        )
    conn.commit()
    conn.close()

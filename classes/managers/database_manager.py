"""
database_manager.py

Handles SQLite3 database operations such as
loading or creating the database, 
loading tables, appending information to tables.

Author(s): Braeden, Myles
Created: 2026-01-22
"""

import sqlite3
import classes.constants as c

def load_database(self) -> None:
    """
    Establishes a connection to the database, creates one if not existing.
    Creates a profiles table if not existing.
    """
    self.connection = sqlite3.connect(c.DB_PATH)
    self.cursor = self.connection.cursor()

    tables = [
        "profiles",
        "user_level_progress",
        "antiparticle_properties",
        "element_properties"
    ]

    for table in tables:
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        result = self.cursor.fetchone()

    if not result:
        load_tables(self)

    self.connection.commit()

def load_tables(self) -> None:
    elements = [
        ("hydrogen", 50, 20, 10, 150, 400, "Gas", "Fires projectiles at a steady rate.", 1, 10, 0, 0, 0, 0, 0),
        ("oxygen", 50, 100, 50, 75, 3000, "Gas", "Heals nearby elements & compounds.", 0, 0, 1, 15, 0, 0, 0),
        ("silicon", 50, 100, 50, 0, 1000, "Solid", "Can be placed on energy tiles to gain energy.", 0, 0, 0, 0, 1, 1, 0),
        ("lead", 50, 350, 175, 600, 5000, "Solid", "Slowly fires powerful projectiles from a long range.", 1, 250, 0, 0, 0, 0, 0)
    ]

    antiparticles = [
        ("down_antiquark", 25, 2.5, 1, 50, 1000, "The most basic antiparticle. Weak stats, decent speed", "Low", "Medium"),
        ("up_antiquark", 100, 2.0, 6, 50, 1500, "A counterpart to the Down Antiquark, has more HP but less speed. Overall stronger.", "Medium", "Low"),
        ("top_antiquark", 1000, 0.75, 20, 50, 2000, "A massive particle, moves very slowly, but has a TON of HP.", "Very High", "Very Low"),
        ("bottom_antiquark", 250, 2.0, 4, 50, 1000, "A larger Down Antiquark. Solid bulk with a solid speed.", "High", "Low"),
        ("positron", 15, 4.0, 2, 150, 300, "Weak but agile, not to mention that they can attack your molecules from a distance.", "Low", "Fast"),
        ("photon", 10, 8.0, 1, 100, 200, "Can blitz through your defenses if you haven't prepared walls. In addition, they glow, obscuring nearby antiparticles or brightening up dark levels.", "Very Low", "Extremely Fast")
    ]

    self.cursor.execute("PRAGMA foreign_keys = ON")

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )          
    ''')

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_level_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tutorial_completed INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES profiles(user_id)       
        )                                   
    ''')

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS element_properties (
            element_id INTEGER PRIMARY KEY AUTOINCREMENT,
            element_name TEXT NOT NULL UNIQUE,
            element_health INTEGER NOT NULL,
            element_buy_cost INTEGER NOT NULL,
            element_upgrade_cost INTEGER NOT NULL,
            element_range INTEGER NOT NULL,
            element_cooldown INTEGER NOT NULL,
            element_state TEXT NOT NULL,
            element_desc TEXT NOT NULL,
            element_can_damage INTEGER NOT NULL,
            element_damage INTEGER NOT NULL,
            element_can_heal INTEGER NOT NULL,
            element_healing INTEGER NOT NULL,
            element_can_energy INTEGER NOT NULL,
            element_energy_generation INTEGER NOT NULL,
            element_radioactive INTEGER NOT NULL
        )          
    ''')

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS antiparticle_properties (
            antiparticle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            antiparticle_name TEXT NOT NULL UNIQUE,
            antiparticle_health INTEGER NOT NULL,
            antiparticle_speed REAL NOT NULL,
            antiparticle_damage INTEGER NOT NULL,
            antiparticle_range INTEGER NOT NULL,
            antiparticle_cooldown INTEGER NOT NULL,
            antiparticle_description TEXT NOT NULL,
            antiparticle_health_category TEXT NOT NULL,
            antiparticle_speed_category TEXT NOT NULL
        )          
    ''')

    element_query = '''
        INSERT OR IGNORE INTO element_properties (
            element_name, element_health, element_buy_cost, element_upgrade_cost,
            element_range, element_cooldown, element_state, element_desc,
            element_can_damage, element_damage, element_can_heal, element_healing,
            element_can_energy, element_energy_generation, element_radioactive
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    antiparticle_query = '''
        INSERT INTO antiparticle_properties (
            antiparticle_name, antiparticle_health, antiparticle_speed,
            antiparticle_damage, antiparticle_range, antiparticle_cooldown,
            antiparticle_description, antiparticle_health_category,
            antiparticle_speed_category
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    self.cursor.executemany(element_query, elements)
    self.cursor.executemany(antiparticle_query, antiparticles)

def insert_user_level_progress(self, user_id):
    self.cursor.execute("INSERT INTO user_level_progress (tutorial_completed, user_id) VALUES (?, ?)", (1, user_id))
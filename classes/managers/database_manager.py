"""
database_manager.py

Handles SQLite3 database operations such as
loading or creating the database, 
loading tables, appending information to tables.

Author(s): Braeden, Myles
Created: 2026-01-22
"""

import classes.constants as c
import sqlite3

def load_database(self) -> None:
    """
    Establishes a connection to the database, creates one if not existing.
    Creates a profiles table if not existing.
    """
    self.connection = sqlite3.connect(c.DB_PATH)
    self.cursor = self.connection.cursor()
    self.cursor.execute("PRAGMA foreign_keys = ON")

    tables = [
        "profiles",
        "user_research",
        "user_level_progress",
        "antiparticle_properties",
        "element_properties",
        "question_properties"
    ]

    missing = False

    for table in tables:
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        if not self.cursor.fetchone():
            missing = True
            break

    if missing:
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

    questions = [
        ("What is at the center of an atom?", 1, "Nucleus", "Electrons", "A Ball", "Gas", 1),
        ("Which of these elements is a Noble Gas?", 1, "Iron", "Hydrogen", "Neon", "Carbon", 3),
        ("What is the compound, H₂O, commonly known as?", 1, "Hydrochloric Acid", "Water", "Bleach", "Ammonia", 2),
        ("What is the valence shell?", 1, "The outermost shell", "The first shell", "The shell with the most number of electrons", "The shell with a Valentine's card", 1),
        ("What resides inside the nucleus of an atom?", 1, "Protons & Electrons", "Neutrons Only", "Protons & Neutrons", "Neutrons & Electrons", 3),
        ("What is the symbol for Silicon?", 1, "S", "Sc", "Sx", "Si", 4),
        ("Which of these is not a real element?", 1, "Lithium (Li)", "Carbon (C)", "Palaeon (Pn)", "Helium (He)", 3),
        ("Which of these is a real element?", 1, "Copper (Cu)", "Unobtanium (Ub)", "Steel (St)", "Extremium (Ex)", 1),
        ("How many valence electrons are in Sodium (Na)?", 2, "1", "2", "3", "4", 1),
        ("Which of the following is the most electronegative element?", 2, "Francium (Fr)", "Carbon (C)", "Fluorine (F)", "Neon (N)", 3),
        ("What is the classification of the element Lead?", 2, "Metalloid", "Transition Metal", "Alkali Metal", "Heavy Metal", 2),
        ("Isotopes of elements vary in the amount of which particle?", 2, "Photons", "Protons", "Neutrons", "Electrons", 3),
        ("What is electronegativity?", 2, "A chemical compound consisting of an assembly of positively charged ions", "The tendency to attract electrons in a bond", "The tendency to attract protons in a bond", "Atoms that conduct an electric current", 2),
        ("Which is the S.I unit of temperature?", 2, "Fahrenheit", "Celsius", "Kelvin", "Rankine", 3),
        ("Who made the Bohr model of the atom?", 2, "Erwin Schrödinger", "J.J. Thompson", "Bohr Machina", "Niels Bohr", 4),
        ("What is an antiparticle?", 3, "Atoms of the same element that contain different numbers of neutrons.", "Opposite counterparts to each type of elementary particle.", "An alternate version of a photon.", "Any atom or group of atoms that bears one or more positive or negative electrical charges.", 2),
        ("What is normally the oxidation state of Oxygen?", 3, "1", "0", "-1", "-2", 4),
        ("What is a reagent?", 3, "A chemical that controls the amount of product formed in a chemical rxn.", "A substance added to a system to cause a chemical reaction.", "A chemical substance that neutralizes alkalis and dissolves some metals.", "A substance used to improve the transfer of heat between two surfaces.", 2),
        ("Out of the elements listed, what can Carbon (C) bond with?", 3, "Neon (Ne)", "Argon (Ar)", "Helium (He)", "Phosphorus (P)", 4),
        ("Among isomeric amines, tertiary amines have the lowest boiling points because:", 4, "They have highest molecular mass.", "They are most basic in nature.", "They are more polar in nature.", "They do not form hydrogen bonds.", 4),
        ("What is the electron configuration of Manganese (Mn)?", 4, "[Ar] 4s^2 3d^5", "[Rn] 7s^2 5f^3 6d^1", "[Kr] 5s^2 4d^10 5p^3", "[Xe] 6s^2 4f^6", 1),
        ("Which of the following compounds has a shape that is NOT trigonal planar?", 4, "BF3", "NO3-", "BClF2", "PCl3", 4),
        ("1 mole of K4[Fe(CN)6] contains carbon = 6g atoms. 0.5 mole of K4[Fe(CN)6] contain carbon = 3g atoms. The mass of carbon present in 0.5 mole of K4[Fe(CN)6] is:", 4, "36g", "18g", "3.6g", "1.8g", 1),
        ("What is the normality of a 1M solution of H3PO4?", 4, "0.5 N", "3.0 N", "2.0 N", "1.0 N", 2),
        ("Who was the first American chemist to receive a Nobel Prize?", 4, "Edward Frankland", "Theodore Richard", "John Bardeen", "Paul Dirac", 2)
    ]

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )          
    ''')

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            research_amount INTEGER NOT NULL
        )          
    ''')

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_level_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tutorial_completed INTEGER NOT NULL,
            user_id INTEGER NOT NULL UNIQUE,
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

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_properties (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_question TEXT NOT NULL UNIQUE,
            question_difficulty INTEGER NOT NULL,
            question_answer_one TEXT NOT NULL,
            question_answer_two TEXT NOT NULL,
            question_answer_three TEXT NOT NULL,
            question_answer_four TEXT NOT NULL,
            question_correct_answer INTEGER NOT NULL
        )          
    ''')

    element_insert = '''
        INSERT OR IGNORE INTO element_properties (
            element_name, element_health, element_buy_cost, element_upgrade_cost,
            element_range, element_cooldown, element_state, element_desc,
            element_can_damage, element_damage, element_can_heal, element_healing,
            element_can_energy, element_energy_generation, element_radioactive
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    antiparticle_insert = '''
        INSERT OR IGNORE INTO antiparticle_properties (
            antiparticle_name, antiparticle_health, antiparticle_speed,
            antiparticle_damage, antiparticle_range, antiparticle_cooldown,
            antiparticle_description, antiparticle_health_category,
            antiparticle_speed_category
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    question_insert = '''
        INSERT OR IGNORE INTO question_properties (
            question_question, question_difficulty, question_answer_one,
            question_answer_two, question_answer_three, question_answer_four,
            question_correct_answer
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    '''

    self.cursor.executemany(element_insert, elements)
    self.cursor.executemany(antiparticle_insert, antiparticles)
    self.cursor.executemany(question_insert, questions)

def insert_user_level_progress(self, user_id):
    self.cursor.execute(
        "SELECT tutorial_completed FROM user_level_progress WHERE user_id = ?",
        (user_id,)
    )
    row = self.cursor.fetchone()
    if row is None:
        self.cursor.execute(
            "INSERT INTO user_level_progress (tutorial_completed, user_id) VALUES (?, ?)",
            (1, user_id)
        )
    elif row[0] != 1:
        self.cursor.execute(
            "UPDATE user_level_progress SET tutorial_completed = ? WHERE user_id = ?",
            (1, user_id)
        )

    self.connection.commit()

def get_user_level_progress(self, user_id):
    self.cursor.execute(
        "SELECT tutorial_completed FROM user_level_progress WHERE user_id = ?",
        (user_id,)
    )
    row = self.cursor.fetchone()

    return {
        "tutorial": bool(row[0]) if row else False
    }

def ensure_user_research_record(self, user_id, default_amount=0):
    self.cursor.execute(
        "SELECT research_amount FROM user_research WHERE user_id = ?",
        (user_id,)
    )
    row = self.cursor.fetchone()

    if row is None:
        self.cursor.execute(
            "INSERT INTO user_research (user_id, research_amount) VALUES (?, ?)",
            (user_id, default_amount)
        )
        self.connection.commit()
        return default_amount

    return row[0]

def get_user_research(self, user_id):
    return ensure_user_research_record(self, user_id, 0)

def add_user_research(self, user_id, amount):
    current = ensure_user_research_record(self, user_id, 0)
    new_amount = current + amount

    self.cursor.execute(
        "UPDATE user_research SET research_amount = ? WHERE user_id = ?",
        (new_amount, user_id)
    )
    self.connection.commit()

    return new_amount

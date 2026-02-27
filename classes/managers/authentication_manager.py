"""
authentication_manager.py

Module for verifying the user login info and adding a new user.
Is appended into the database.

Author(s): Alan
Created: 2026-01-22
"""

import bcrypt
import classes.constants as c
import classes.managers.database_manager as database_manager
import pygame
import sqlite3

from classes.ui.game_error import GameError

def handle_signup(self) -> None:
    """
    Gets username and password from user if new user
    """
    username = self.menu.username_input.text
    password = self.menu.password_input.text

    if username == "":
        self.active_error = GameError("Username cannot be empty")
        self.error_start_time = pygame.time.get_ticks()
        return

    if len(password) < 8:
        self.active_error = GameError("Password must be at least 8 characters")
        self.error_start_time = pygame.time.get_ticks()
        return

    try:
        bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(bytes, salt)

        self.cursor.execute("INSERT INTO profiles (username, password) VALUES (?, ?)", (username, hashed_password))
        user_id = self.cursor.lastrowid
        database_manager.ensure_user_research_record(self, user_id, 0)
        self.connection.commit()
        self.state = c.LOGIN
    except sqlite3.IntegrityError:
        self.active_error = GameError("Username already exists")
        self.error_start_time = pygame.time.get_ticks()

def handle_login(self):
    """
    Gets username and password and adds it to the database
    """
    username = self.menu.username_input.text
    password = self.menu.password_input.text

    if username == "":
        self.active_error = GameError("Username cannot be empty")
        self.error_start_time = pygame.time.get_ticks()
        return
    
    if password == "":
        self.active_error = GameError("Password cannot be empty")
        self.error_start_time = pygame.time.get_ticks()
        return

    bytes = password.encode("utf-8")

    self.cursor.execute("SELECT password FROM profiles WHERE username = ?", (username, ))
    actualPassword = self.cursor.fetchone()

    if actualPassword is None:
        self.active_error = GameError("User not found")
        self.error_start_time = pygame.time.get_ticks()
        return

    result = bcrypt.checkpw(bytes, actualPassword[0])

    if result:
        self.cursor.execute("SELECT user_id FROM profiles WHERE username = ?", (username, ))
        self.user_id = self.cursor.fetchone()
        self.research_amount = database_manager.get_user_research(self, self.user_id[0])

        self.state = c.MAIN_MENU
    else:
        self.active_error = GameError("Incorrect password")
        self.error_start_time = pygame.time.get_ticks()

#AI STUDY PLANNER 
# basic task manager
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
from datetime import datetime, date, timedelta
from pathlib import Path

#==========================
# app settings
#==========================
APP_NAME = "AI Study Planner"
DATABASE_FILE = Path(__file__).with_name( "study_planner.db")


BG = "#10131D"
PANEL = "#191E2B"
PANEL_LIGHT = "#222A3B"
ACCENT = "#8B7CFF"
TEXT = "#F2F4FA"
MUTED = "#A0A8BB"
GREEN = "#5DD6A0"
RED = "#FF7777"
YELLOW = "#FFD166"

DEFAULT_GOAL_MINUTES = 180
#=========================
# now i make dataabse for app 
#============================

def connect_db():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    with connect_db() as db:
        db.execute("""
             CREATE TABLE IF NOT EXISTS tasks ()
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            priority TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            due_date TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL)
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS sessions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                minutes INTEGER NOT NULL,
                session_data TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
                ) 
                """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS settings(
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL 
                )
                """)
        db.execute("""
            INSERT OR IGNORE INTO settings (key, value)
            VALUES ('daily_goal', '180')
                   """)
        
        def get_setting(key, value):
            with connect_db() as db:
                db.execute("""
                           INSERT INTO settings (key, value)
                           VALUES (?, ?)
                           ON CONFLICT(key) DO UPDATE SET value = excluded.value
                           """,(key, str(value)))
           
        def get_all_task():
            with connect_db() as db:
                return db.execute("""
                    SELECT * FROM tasks
                    ORDER BY completed ASC,
                    CASE priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    ELSE 3
                    END, 
                    due_date ASC 
                    
                    """).fetchall()
                
                
        def add_task_to_db(subject, topic, priority, minutes, due_date):
          with connect_db() as db:
            db.execute("""
                INSERT INTO 
                (subject, topic, priority, minutes, due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    subject, topic, priority, minutes, due_date,
                      datetime.now().isoformat(timespec="seconds")
                      
                ))
            def toggle_task_inDB(task_id, completed):
                with connect_db() as db:
                    db.execute(
                        "UPDATE tasks SET completed = ? WHERE id = ?", 
                        (int(completed), task_id)
                    )
                            
                def delete_task_from_db(task_id):
                    with connect_db() as db:
                        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                      
                def save_study_session(task_id, minutes):
                    with connect_db() as db:
                        db.execute("""
                                   INSERT INTO sessions (task_id, minutes, session_date)
                                   VALUES (?, ?, ?)
                                   """, (task_id, minutes,  date.today().isoformat()))
                        
                        
                def get_today_minutes():
                    with connect_db() as db:
                        row = db.execute("""
                               SELECT COALESCE(SUM(minutes), 0) As total
                               FROM sessions
                               WHERE session_date = ?
                               """, (date.today().isoformat(),)).fetchone()
                                  return row["total"]
                              
                              
                def get_today_session_count():
                    with connect_db() as db:
                        row = db.execute("""
                               SELECT COUNT(*) As total 
                               FROM sessions WHERE session_date = ?
                               """, (date.today().isoformat(),)).fetchone()
                                  return row["total"]              
                              
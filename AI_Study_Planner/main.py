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
            CREATE TABLE IF NOT EXISTS tasks(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              subject TEXT NOT NULL,
              topic TEXT NOT NULL,
              priority TEXT NOT NULL,
              minutes INTEGER NOT NULL,
              due_date TEXT NOT NULL,
              completed INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL
            ) 
        """)
        
        db.execute(""" 
            CREATE TABLE IF NOT EXISTS sessions(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              task_id INTEGER,
              minutes INTEGER NOT NULL,
              session_date TEXT NOT NULL,
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
def get_setting(key, default=""):
    with connect_db() as db:
        row = db.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default
                
        
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
                INSERT INTO tasks (subject, topic, priority, minutes, due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                subject, topic, priority, minutes, due_date,
                datetime.now().isoformat(timespec="seconds")
                      
            ))
def toggle_task_in_db(task_id, completed):
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
             
             
 # smart study assistant
 
def recommend_task(tasks):
    pending = [task for task in tasks if not task["completed"]]
    if not pending:
        return (
            "All caught up!",
            "Add a new task or review something  you have studied."
           
        )
    today = date.today()
    def score(task):
        priority_score = {
            "High": 30,
            "Medium": 20,
             "Low":10,
        
        } .get(task["priority"],10)
        try:
            days_left = (
                date.fromisoformat(task["due_date"]) - today
            
        ).days
        except ValueError:
            day_left = 7 
         
        if days_left < 0:
            deadline_score = 40
        elif days_left == 0:
            deadline_score = 35
        elif days_left == 1: 
            deadline_score =  25
        elif days_left <= 3:
            deadline_score = 15
        else:
            deadline_score = 5
            
        duration_score = max(0, 10 - task["minutes"] // 15)
            
        return priority_score + deadline_score + duration_score
        
    selected = max(pending,key=score)
    return  (
            f"Study {selected['subject']}",
            f"Start: {selected['topic']}"
            f"({selected['minutes']} min, {selected['priority']} priority)."
        )
class StudyPlannerAPP:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1150x760")
        self.root.minsize(900, 620)
        self.root.configure(bg=BG)
        
        self.timer_after_id = None
        self.timer_running = False
        self.timer_remaining = 25 * 60
        self.timer_mode = "Focus"
        self.selected_task_id = None
        
        self.configure_styles()
        self.build_layout()
        self.refresh_dashboard()
        self.refresh_tasks()
        self.refresh_recommendation()
        self.update_timer_display()
        
          
#  visual_style

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Treeview",
            background=PANEL,
            foreground=TEXT,
            fieldbackground=PANEL,
            rowheight=34,
            borderwidth=0,
            font=("Segoe UI", 10, )
        )
        style.configure(
            "Treeview.Headling",
            background=PANEL_LIGHT,
            foreground=TEXT,
            relief="flat",
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "Treeview",
            background=[("selected",ACCENT)],
            foreground=[("selected","white")]
        )   
        style.configure(
            "TCombobox",
            fieldbackground=PANEL_LIGHT,
            background=PANEL_LIGHT,
            foreground=TEXT,
            arrowcolor=TEXT
        )
        style.configure(
            "TProgressbar",
            troughcolor=PANEL_LIGHT,
            background=GREEN,
            thickness=12 
        )    
        
    def make_button(self, parent, text, command,
                     color=ACCENT,  fg="White"):
        return tk.Button(
             parent,
             text=text,
             command=command,
             bg=color,
             fg=fg,
             activebackground=color,
             activeforeground=fg,
             relief="flat",
             bd=0,
             padx=14,
             pady=9,
             cursor="hand2",
             font=("Sege UI", 10, "bold")
         )   
    def make_label(self, parent, text, size=11,
                    color=TEXT, bold=False):   
        return tk.Label(
             parent,
             text=text, 
             bg=parent.cget("bg"),
             fg=color,
             fort=(
                 "Segoe UI",
                 size,
                 "bold" if bold else "normal"
             ),
             anchor="w"
             
         )    
    def made_card(self, parent, padding=16):
        returrn ttk.Frame(
            parent,
            bg=PANEL,
            padx=padding,
            pady=padding,
            hightlightthickness=1,
            highttlightbackground="#2B33455"
        )
        
        
        
    
    
    
            
             
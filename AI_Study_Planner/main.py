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


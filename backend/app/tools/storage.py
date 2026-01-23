import os
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models.core import MaterialConfig

DB_PATH = "data/matultimate.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # History table
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  grade TEXT,
                  topic TEXT,
                  material_type TEXT,
                  content TEXT,
                  format TEXT,
                  config TEXT,
                  timestamp TEXT)''')
    
    # Exercise bank
    c.execute('''CREATE TABLE IF NOT EXISTS exercise_bank
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  topic TEXT,
                  grade TEXT,
                  content TEXT,
                  solution TEXT,
                  difficulty TEXT,
                  tags TEXT,
                  timestamp TEXT)''')
    
    conn.commit()
    conn.close()

def save_to_history(title: str, grade: str, topic: str, material_type: str, content: str, output_format: str, config: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO history (title, grade, topic, material_type, content, format, config, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (title, grade, topic, material_type, content, output_format, json.dumps(config), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_history(limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM history ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_to_exercise_bank(title: str, topic: str, grade: str, content: str, solution: str, difficulty: str, tags: List[str] = []):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO exercise_bank (title, topic, grade, content, solution, difficulty, tags, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (title, topic, grade, content, solution, difficulty, json.dumps(tags), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_exercises(topic: Optional[str] = None, grade: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = "SELECT * FROM exercise_bank WHERE 1=1"
    params = []
    if topic:
        query += " AND topic = ?"
        params.append(topic)
    if grade:
        query += " AND grade = ?"
        params.append(grade)
    query += " ORDER BY timestamp DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

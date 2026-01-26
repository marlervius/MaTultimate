import os
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models.config import MaterialConfig

DB_PATH = "data/matultimate.db"

def init_db():
    """Initialiserer databasen og oppretter tabeller hvis de ikke finnes."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Historikk-tabell for genererte dokumenter
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  klassetrinn TEXT,
                  emne TEXT,
                  config_json TEXT,
                  worksheet_pdf_b64 TEXT,
                  answer_key_pdf_b64 TEXT,
                  source_code TEXT,
                  timestamp TEXT)''')
    
    # Oppgavebank for individuelle oppgaver (fremtidig bruk)
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

def save_to_history(config: MaterialConfig, worksheet_pdf: str, answer_key_pdf: Optional[str], source_code: str):
    """Lagrer en genereringsøkt til historikken."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    title = f"{config.emne} - {config.klassetrinn}"
    config_dict = config.model_dump()
    
    c.execute('''INSERT INTO history 
                 (title, klassetrinn, emne, config_json, worksheet_pdf_b64, answer_key_pdf_b64, source_code, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (title, config.klassetrinn, config.emne, json.dumps(config_dict), 
               worksheet_pdf, answer_key_pdf, source_code, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Henter de siste genereringene fra historikken."""
    if not os.path.exists(DB_PATH):
        return []
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM history ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

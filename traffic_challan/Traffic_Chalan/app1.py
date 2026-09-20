import os
import urllib.parse
import sqlite3

import streamlit as st

from violation_detection import (
    detect_violation,
    detect_number_plate,
    get_fine,
    get_user
)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_chalan_database():

    conn = sqlite3.connect("Chalan.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        violation_name TEXT NOT NULL UNIQUE,
        fine INTEGER NOT NULL
    )
    """)

    violations = [
        ("Triple Ride", 1000),
        ("No Parking", 100),
        ("No Helmet", 200),
        ("Overspeed", 1000)
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO violations
    (
        violation_name,
        fine
    )
    VALUES (?, ?)
    """, violations)

    conn.commit()
    conn.close()


def initialize_user_database():

    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        vehicle_reg TEXT NOT NULL UNIQUE,
        vehicle_type TEXT,
        vehnum TEXT,
        mobile TEXT,
        driver_photo TEXT
    )
    """)

    # -----------------------------------------------------
    # DEMO USER
    # -----------------------------------------------------
    users = [
        (
            "Maicharla Raju",
            "TS10ED8176",
            "Scooty",
            "1662",
            "7729083565",
            "drivers/driver1.jpg"
        )
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO users
    (
        name,
        vehicle_reg,
        vehicle_type,
        vehnum,
        mobile,
        driver_photo
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, users)

    conn.commit()
    conn.close()


# Run database initialization
initialize_chalan_database()
initialize_user_database()


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

TEMP_DIR = os.path.join(
    BASE_DIR,
    "temp"
)

os.makedirs(
    TEMP_DIR,
    exist_ok=True
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Traffic Challan System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)
import os
import base64
import sqlite3

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# BASE PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHALAN_DB = os.path.join(BASE_DIR, "Chalan.db")
USER_DB = os.path.join(BASE_DIR, "user.db")


# ============================================================
# GROQ CONFIGURATION
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. "
        "Add it to .env or Streamlit Secrets."
    )

client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# IMAGE TO BASE64
# ============================================================

def image_to_base64(image_path):

    with open(image_path, "rb") as image_file:

        return base64.b64encode(
            image_file.read()
        ).decode("utf-8")


# ============================================================
# DETECT TRAFFIC VIOLATION
# ============================================================

def detect_violation(image_path):

    image_base64 = image_to_base64(image_path)

    response = client.chat.completions.create(

        model="qwen/qwen3.8-27b",

        messages=[
            {
                "role": "user",

                "content": [

                    {
                        "type": "text",

                        "text": """
Analyze this traffic image.

Identify the main traffic violation visible in the image.

Possible violations are:

1. Triple Ride
2. No Parking
3. No Helmet
4. Overspeed

Return ONLY ONE exact name:

Triple Ride
No Parking
No Helmet
Overspeed

Do not provide explanation.
"""
                    },

                    {
                        "type": "image_url",

                        "image_url": {
                            "url":
                            "data:image/jpeg;base64,"
                            + image_base64
                        }
                    }
                ]
            }
        ],

        max_tokens=100
    )


    result = response.choices[0].message.content.strip()

    result_lower = result.lower()


    # Normalize model response

    if "triple" in result_lower:

        return "Triple Ride"

    elif "parking" in result_lower:

        return "No Parking"

    elif "helmet" in result_lower:

        return "No Helmet"

    elif "overspeed" in result_lower:

        return "Overspeed"


    return result


# ============================================================
# DETECT NUMBER PLATE
# ============================================================

def detect_number_plate(image_path):

    image_base64 = image_to_base64(image_path)


    response = client.chat.completions.create(

        model="qwen/qwen3.8-27b",

        messages=[
            {
                "role": "user",

                "content": [

                    {
                        "type": "text",

                        "text": """
Look carefully at this traffic image.

Find the vehicle registration number plate.

Return ONLY the registration number.

Examples:

TS09PA3330
TS10EX2850
TS10ED8176

Do not return:

- explanation
- spaces
- hyphens
- quotation marks
- other text

If no number plate is visible, return:

NOT DETECTED
"""
                    },

                    {
                        "type": "image_url",

                        "image_url": {
                            "url":
                            "data:image/jpeg;base64,"
                            + image_base64
                        }
                    }
                ]
            }
        ],

        max_tokens=100
    )


    result = response.choices[0].message.content.strip()


    # Clean OCR result

    result = (
        result
        .upper()
        .replace(" ", "")
        .replace("-", "")
        .replace("\n", "")
        .replace("\r", "")
        .replace("`", "")
        .replace('"', "")
        .replace("'", "")
        .replace(".", "")
    )


    return result


# ============================================================
# GET FINE
# ============================================================

def get_fine(violation):

    conn = sqlite3.connect(CHALAN_DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT fine
        FROM violations
        WHERE LOWER(violation_type) = LOWER(?)
        """,
        (violation.strip(),)
    )


    row = cursor.fetchone()

    conn.close()


    if row:

        return row[0]

    return 0


# ============================================================
# GET DRIVER / OWNER DETAILS
# ============================================================

def get_user(number_plate):

    user_db_path = os.path.join(
        BASE_DIR,
        "user.db"
    )


    # Normalize number plate

    number_plate = (
        str(number_plate)
        .upper()
        .replace(" ", "")
        .replace("-", "")
        .replace("\n", "")
        .replace("\r", "")
        .strip()
    )


    if not number_plate:

        return None


    conn = sqlite3.connect(
        user_db_path
    )

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    # Make sure users table exists

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            vehicle_reg TEXT UNIQUE NOT NULL,

            vehicle_type TEXT,

            vehnum TEXT,

            mobile TEXT,

            driver_photo TEXT
        )
        """
    )


    conn.commit()


    # Search normalized registration number

    cursor.execute(
        """
        SELECT
            id,
            name,
            vehicle_reg,
            vehicle_type,
            vehnum,
            mobile,
            driver_photo

        FROM users

        WHERE
            REPLACE(
                REPLACE(
                    UPPER(vehicle_reg),
                    ' ',
                    ''
                ),
                '-',
                ''
            ) = ?
        """,
        (number_plate,)
    )


    row = cursor.fetchone()

    conn.close()


    if row:

        return dict(row)


    return None
import os
import base64
import sqlite3

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


# =========================================================
# GROQ API
# =========================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set."
    )

client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================================
# NORMALIZE NUMBER PLATE
# =========================================================

def normalize_plate(plate):

    if not plate:
        return ""

    return "".join(
        ch
        for ch in str(plate).upper()
        if ch.isalnum()
    )


# =========================================================
# DETECT TRAFFIC VIOLATION
# =========================================================

def detect_violation(image_path):

    with open(image_path, "rb") as f:

        image_base64 = base64.b64encode(
            f.read()
        ).decode("utf-8")


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

Identify ONLY ONE violation.

Allowed violations:

1. Triple Ride
2. No Parking
3. No Helmet
4. Overspeed

Return ONLY one of these exact names:

Triple Ride
No Parking
No Helmet
Overspeed

Do not provide:
- reasoning
- explanation
- markdown
- <think> tags
- additional text
"""
                    },

                    {
                        "type": "image_url",

                        "image_url": {
                            "url":
                            f"data:image/jpeg;base64,{image_base64}"
                        }
                    }

                ]
            }

        ]
    )


    result = response.choices[0].message.content.strip()


    # =====================================================
    # REMOVE THINK TAGS
    # =====================================================

    if "<think>" in result:

        if "</think>" in result:

            result = result.split(
                "</think>"
            )[-1]

        else:

            result = result.split(
                "<think>"
            )[-1]


    result = result.strip()


    # =====================================================
    # IDENTIFY VIOLATION
    # =====================================================

    result_lower = result.lower()


    if "triple ride" in result_lower:

        return "Triple Ride"


    if "no parking" in result_lower:

        return "No Parking"


    if "no helmet" in result_lower:

        return "No Helmet"


    if "overspeed" in result_lower:

        return "Overspeed"


    # Handle slight model variations

    if "triple" in result_lower:

        return "Triple Ride"


    if "parking" in result_lower:

        return "No Parking"


    if "helmet" in result_lower:

        return "No Helmet"


    if "overspeed" in result_lower:

        return "Overspeed"


    return result


# =========================================================
# DETECT NUMBER PLATE
# =========================================================

def detect_number_plate(image_path):

    with open(image_path, "rb") as f:

        image_base64 = base64.b64encode(
            f.read()
        ).decode("utf-8")


    response = client.chat.completions.create(

        model="qwen/qwen3.8-27b",

        messages=[

            {
                "role": "user",

                "content": [

                    {
                        "type": "text",

                        "text": """
Read the vehicle registration number plate
from this image.

Return ONLY the registration number.

VERY IMPORTANT:

- Do NOT provide reasoning.
- Do NOT provide <think>.
- Do NOT provide </think>.
- Do NOT provide explanations.
- Do NOT provide markdown.
- Do NOT write "Number Plate:".
- Do NOT write "Registration:".
- Do NOT write any other words.
- Return only letters and numbers.

Examples:

TS10ED8176

TS09PA3330

MH43BA2518

TS10EX2850
"""
                    },

                    {
                        "type": "image_url",

                        "image_url": {
                            "url":
                            f"data:image/jpeg;base64,{image_base64}"
                        }
                    }

                ]
            }

        ]
    )


    result = response.choices[0].message.content.strip()


    # =====================================================
    # REMOVE THINKING BLOCK
    # =====================================================

    if "<think>" in result:

        if "</think>" in result:

            result = result.split(
                "</think>"
            )[-1]

        else:

            result = result.split(
                "<think>"
            )[-1]


    # =====================================================
    # REMOVE COMMON LABELS
    # =====================================================

    result = result.replace(
        "Number Plate:",
        ""
    )

    result = result.replace(
        "NUMBER PLATE:",
        ""
    )

    result = result.replace(
        "number plate:",
        ""
    )

    result = result.replace(
        "Registration:",
        ""
    )

    result = result.replace(
        "REGISTRATION:",
        ""
    )

    result = result.replace(
        "registration:",
        ""
    )


    # =====================================================
    # REMOVE THINK TAGS IF STILL PRESENT
    # =====================================================

    result = result.replace(
        "<think>",
        ""
    )

    result = result.replace(
        "</think>",
        ""
    )


    # =====================================================
    # CLEAN MARKDOWN
    # =====================================================

    result = result.replace(
        "`",
        ""
    )

    result = result.replace(
        "*",
        ""
    )

    result = result.replace(
        "#",
        ""
    )


    # =====================================================
    # TAKE LAST NON-EMPTY LINE
    #
    # This protects against responses such as:
    #
    # The plate appears to be...
    # TS10EX2850
    # =====================================================

    lines = [
        line.strip()
        for line in result.splitlines()
        if line.strip()
    ]


    if lines:

        result = lines[-1]


    # =====================================================
    # KEEP ONLY LETTERS AND NUMBERS
    # =====================================================

    result = "".join(
        ch
        for ch in result.upper()
        if ch.isalnum()
    )


    return result


# =========================================================
# GET FINE
# =========================================================

def get_fine(violation):

    conn = sqlite3.connect(
        "Chalan.db"
    )

    cursor = conn.cursor()


    cursor.execute("""
        SELECT fine
        FROM violations
        WHERE LOWER(violation_name)
        = LOWER(?)
    """, (violation,))


    row = cursor.fetchone()

    conn.close()


    if row:

        return row[0]


    return 0


# =========================================================
# GET USER
# =========================================================

def get_user(number_plate):

    conn = sqlite3.connect(
        "user.db"
    )

    cursor = conn.cursor()


    detected_plate = normalize_plate(
        number_plate
    )


    # =====================================================
    # GET ALL USER DETAILS
    # =====================================================

    cursor.execute("""
        SELECT
            name,
            vehicle_reg,
            vehicle_type,
            vehnum,
            mobile,
            driver_photo
        FROM users
    """)


    rows = cursor.fetchall()

    conn.close()


    # =====================================================
    # FIND MATCH
    # =====================================================

    for row in rows:

        database_plate = normalize_plate(
            row[1]
        )


        if database_plate == detected_plate:

            return row


    return None


# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":

    print()
    print("--------------------------------")
    print("TRAFFIC VIOLATION DETECTION")
    print("--------------------------------")


    test_image = (
        r"images\no_helmet.jpg"
    )


    if not os.path.exists(
        test_image
    ):

        print(
            "Image not found:",
            test_image
        )

        exit()


    # =====================================================
    # VIOLATION
    # =====================================================

    print(
        "Detecting violation..."
    )


    violation = detect_violation(
        test_image
    )


    print(
        "Violation:",
        violation
    )


    # =====================================================
    # FINE
    # =====================================================

    fine = get_fine(
        violation
    )


    print(
        "Fine: ₹",
        fine
    )


    # =====================================================
    # NUMBER PLATE
    # =====================================================

    print(
        "Detecting number plate..."
    )


    number_plate = detect_number_plate(
        test_image
    )


    print(
        "Number Plate:",
        number_plate
    )


    # =====================================================
    # USER
    # =====================================================

    user = get_user(
        number_plate
    )


    if user:

        print()
        print(
            "--------------------------------"
        )

        print(
            "USER FOUND"
        )

        print(
            "--------------------------------"
        )


        print(
            "Name:",
            user[0]
        )

        print(
            "Vehicle:",
            user[1]
        )

        print(
            "Vehicle Type:",
            user[2]
        )

        print(
            "Vehicle Number:",
            user[3]
        )

        print(
            "Mobile:",
            user[4]
        )

        print(
            "Driver Photo:",
            user[5]
        )


    else:

        print()
        print(
            "--------------------------------"
        )

        print(
            "USER NOT FOUND"
        )

        print(
            "Number Plate:",
            number_plate
        )

        print(
            "--------------------------------"
        )
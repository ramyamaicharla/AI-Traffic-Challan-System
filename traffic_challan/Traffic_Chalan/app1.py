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


initialize_chalan_database()



# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")

os.makedirs(TEMP_DIR, exist_ok=True)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Traffic Challan System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- MAIN PAGE ---------- */

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .stButton > button, .stLinkButton > a {
        border-radius: 10px;
        font-weight: 700;
        min-height: 46px;
    }

    [data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.22);
        border-radius: 14px;
        padding: 12px 16px;
    }

    [data-testid="stFileUploader"] {
        border-radius: 14px;
    }


    /* ---------- TITLE ---------- */

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .main-subtitle {
        text-align: center;
        font-size: 17px;
        margin-bottom: 25px;
    }


    /* ---------- SECTION TITLE ---------- */

    .section-title {
        font-size: 27px;
        font-weight: 750;
        margin-top: 15px;
        margin-bottom: 15px;
    }


    /* ---------- OWNER CARD ---------- */

    .owner-card {
        padding: 25px;
        border-radius: 18px;
        border: 1px solid rgba(120,120,120,0.25);
        background: rgba(128,128,128,0.06);
        min-height: 330px;
    }

    .owner-name {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 20px;
    }

    .detail {
        font-size: 18px;
        margin-bottom: 13px;
    }


    /* ---------- PLATE CARD ---------- */

    .plate-card {
        padding: 22px;
        border-radius: 16px;
        border: 2px solid rgba(80,80,80,0.25);
        text-align: center;
        margin-top: 10px;
    }

    .plate-label {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .plate-number {
        font-size: 32px;
        font-weight: 900;
        letter-spacing: 3px;
    }


    /* ---------- CHALLAN CARD ---------- */

    .challan-card {
        padding: 25px;
        border-radius: 18px;
        border: 1px solid rgba(120,120,120,0.25);
        background: rgba(128,128,128,0.05);
    }


    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        font-size: 14px;
        margin-top: 30px;
        opacity: 0.65;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🚦 Traffic Challan")

    st.write(
        "AI-powered traffic violation "
        "detection and challan generation."
    )

    st.divider()

    st.markdown("### ⚙️ System Features")

    st.write("🚨 Violation Detection")
    st.write("🔢 Number Plate Detection")
    st.write("👤 Vehicle Owner Identification")
    st.write("💰 Automatic Fine Calculation")
    st.write("📷 Driver Photo")
    st.write("📱 WhatsApp Challan")

    st.divider()

    st.caption(
        "AI + SQL + Streamlit + WhatsApp"
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🚦 AI TRAFFIC CHALLAN SYSTEM</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'AI-Based Traffic Violation Detection and E-Challan Generation'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# UPLOAD SECTION
# =========================================================

st.markdown(
    '<div class="section-title">📷 Upload Violation Image</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Choose a traffic violation image",
    type=["jpg", "jpeg", "png"],
    help="Upload an image containing a traffic violation."
)


# =========================================================
# PROCESS IMAGE
# =========================================================

if uploaded_file is not None:

    # -----------------------------------------------------
    # SAVE IMAGE
    # -----------------------------------------------------

    image_path = os.path.join(
        TEMP_DIR,
        uploaded_file.name
    )

    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())


    # -----------------------------------------------------
    # IMAGE PREVIEW
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">🚨 Uploaded Violation</div>',
        unsafe_allow_html=True
    )

    preview_col1, preview_col2, preview_col3 = st.columns(
        [1, 2, 1]
    )

    with preview_col2:

        st.image(
            uploaded_file,
            caption="Violation Image",
            use_container_width=True
        )


    st.divider()


    # =====================================================
    # GENERATE BUTTON
    # =====================================================

    generate = st.button(
        "🚨 GENERATE CHALLAN",
        type="primary",
        use_container_width=True
    )


    # =====================================================
    # GENERATE CHALLAN
    # =====================================================

    if generate:

        # -------------------------------------------------
        # STEP 1: VIOLATION
        # -------------------------------------------------

        with st.spinner(
            "🔍 Detecting traffic violation..."
        ):

            try:

                violation = detect_violation(
                    image_path
                )

            except Exception as e:

                st.error(
                    f"Violation detection error: {e}"
                )

                st.stop()

        if not violation:

            st.error(
                "❌ Could not detect a traffic violation."
            )

            st.stop()


        # -------------------------------------------------
        # STEP 2: FINE
        # -------------------------------------------------

        with st.spinner(
            "💰 Checking applicable fine..."
        ):

            try:

                fine = get_fine(
                    violation
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )

                st.stop()
        # -------------------------------------------------
        # STEP 3: NUMBER PLATE
        # -------------------------------------------------

        with st.spinner(
            "🔢 Detecting vehicle number plate..."
        ):

            try:

                number_plate = detect_number_plate(
                    image_path
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )

                st.stop()
        if not number_plate:

            number_plate = "Not Detected"


        # =================================================
        # VIOLATION RESULT
        # =================================================

        st.markdown(
            '<div class="section-title">'
            '🚨 Violation Detection Result'
            '</div>',
            unsafe_allow_html=True
        )

        result1, result2, result3 = st.columns(3)


        with result1:

            st.metric(
                "🚨 Violation",
                violation
            )


        with result2:

            st.metric(
                "💰 Fine Amount",
                f"₹ {fine}"
            )


        with result3:

            st.metric(
                "🔢 Number Plate",
                number_plate
            )


        st.divider()


        # =================================================
        # FIND OWNER
        # =================================================

        with st.spinner(
            "👤 Searching registered vehicle owner..."
        ):

            try:

                user = get_user(
                    number_plate
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )

                st.stop()
        # =================================================
        # USER FOUND
        # =================================================

        if user:

            # -------------------------------------------------
            # DATABASE VALUES
            # -------------------------------------------------

            name = user[0]
            vehicle_reg = user[1]
            vehicle_type = user[2]
            vehnum = user[3]
            mobile = user[4]
            driver_photo = user[5]


            st.success(
                "✅ Registered vehicle owner found."
            )


            # =================================================
            # OWNER SECTION
            # =================================================

            st.markdown(
                '<div class="section-title">'
                '👤 Vehicle Owner Details'
                '</div>',
                unsafe_allow_html=True
            )


            photo_col, details_col = st.columns(
                [1, 2],
                gap="large"
            )


            # -------------------------------------------------
            # PHOTO
            # -------------------------------------------------

            with photo_col:

                st.markdown(
                    "### 📷 Driver Photo"
                )

                if driver_photo:

                    # Convert database path
                    clean_photo = driver_photo.replace(
                        "/",
                        os.sep
                    )

                    photo_path = os.path.join(
                        BASE_DIR,
                        clean_photo
                    )

                    if os.path.isfile(photo_path):

                        st.image(
                            photo_path,
                            caption=name,
                            use_container_width=True
                        )

                    else:

                        st.warning(
                            "Driver photo not found."
                        )

                        st.caption(
                            photo_path
                        )

                else:

                    st.warning(
                        "No driver photo registered."
                    )


            # -------------------------------------------------
            # DETAILS
            # -------------------------------------------------

            with details_col:

                st.markdown(
                    f"""
                    <div class="owner-card">

                    <div class="owner-name">
                    👤 {name}
                    </div>

                    <div class="detail">
                    🚗 <b>Vehicle Registration:</b>
                    {vehicle_reg}
                    </div>

                    <div class="detail">
                    🏍️ <b>Vehicle Type:</b>
                    {vehicle_type}
                    </div>

                    <div class="detail">
                    🆔 <b>Vehicle ID:</b>
                    {vehnum}
                    </div>

                    <div class="detail">
                    📱 <b>Mobile:</b>
                    {mobile}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            st.divider()


            # =================================================
            # DETECTED PLATE
            # =================================================

            plate_col1, plate_col2, plate_col3 = st.columns(
                [1, 2, 1]
            )

            with plate_col2:

                st.markdown(
                    f"""
                    <div class="plate-card">

                    <div class="plate-label">
                    🔢 DETECTED NUMBER PLATE
                    </div>

                    <div class="plate-number">
                    {number_plate}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            st.divider()


            # =================================================
            # CHALLAN SUMMARY
            # =================================================

            st.markdown(
                '<div class="section-title">'
                '📄 Challan Summary'
                '</div>',
                unsafe_allow_html=True
            )


            summary1, summary2 = st.columns(
                2,
                gap="large"
            )


            with summary1:

                st.markdown(
                    f"""
                    <div class="challan-card">

                    <h3>👤 Owner Information</h3>

                    <p>👤 <b>Name:</b> {name}</p>

                    <p>🚗 <b>Vehicle:</b> {vehicle_reg}</p>

                    <p>🏍️ <b>Vehicle Type:</b> {vehicle_type}</p>

                    <p>🆔 <b>Vehicle ID:</b> {vehnum}</p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with summary2:

                st.markdown(
                    f"""
                    <div class="challan-card">

                    <h3>🚨 Violation Information</h3>

                    <p>🚨 <b>Violation:</b> {violation}</p>

                    <p>💰 <b>Fine:</b> ₹ {fine}</p>

                    <p>🔢 <b>Number Plate:</b> {number_plate}</p>

                    <p>📱 <b>Mobile:</b> {mobile}</p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            st.divider()


            # =================================================
            # WHATSAPP
            # =================================================

            st.markdown(
                '<div class="section-title">'
                '📱 Send Challan to Vehicle Owner'
                '</div>',
                unsafe_allow_html=True
            )


            # -------------------------------------------------
            # PHONE NUMBER
            # -------------------------------------------------

            phone = "".join(
                ch
                for ch in str(mobile)
                if ch.isdigit()
            )


            if len(phone) == 10:

                whatsapp_number = "91" + phone

            else:

                whatsapp_number = phone


            # -------------------------------------------------
            # MESSAGE
            # -------------------------------------------------

            whatsapp_message = f"""
🚦 TRAFFIC CHALLAN ALERT

Dear {name},

A traffic violation has been detected for your vehicle.

━━━━━━━━━━━━━━━━━━

👤 Owner: {name}

🚗 Vehicle Number: {vehicle_reg}

🏍️ Vehicle Type: {vehicle_type}

🔢 Detected Number Plate: {number_plate}

🚨 Violation: {violation}

💰 Fine Amount: ₹{fine}

━━━━━━━━━━━━━━━━━━

Please pay the challan according to the applicable traffic rules.

Thank you.

🚦 AI Traffic Challan System
"""


            encoded_message = urllib.parse.quote(
                whatsapp_message
            )


            whatsapp_url = (
                "https://wa.me/"
                + whatsapp_number
                + "?text="
                + encoded_message
            )


            # -------------------------------------------------
            # WHATSAPP BUTTON
            # -------------------------------------------------

            wa_col1, wa_col2, wa_col3 = st.columns(
                [1, 2, 1]
            )

            with wa_col2:

                st.link_button(
                    "📱 SEND CHALLAN ON WHATSAPP",
                    whatsapp_url,
                    use_container_width=True
                )


                st.info(
                    f"WhatsApp number: +91 {phone}"
                )


        # =================================================
        # USER NOT FOUND
        # =================================================

        else:

            st.warning(
                "⚠️ Vehicle number was detected, "
                "but no matching owner was found."
            )


            st.markdown(
                f"""
                <div class="plate-card">

                <div class="plate-label">
                🔢 DETECTED NUMBER PLATE
                </div>

                <div class="plate-number">
                {number_plate}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )


            st.info(
                "Please register this vehicle in "
                "the User Database before generating "
                "the owner notification."
            )


# =========================================================
# NO IMAGE
# =========================================================

else:

    st.info(
        "👆 Upload a traffic violation image "
        "to begin the AI detection process."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div class="footer">
    🚦 AI Traffic Challan Automation System
    &nbsp; | &nbsp;
    YOLO / AI + SQL + Streamlit + WhatsApp
    </div>
    """,
    unsafe_allow_html=True
)



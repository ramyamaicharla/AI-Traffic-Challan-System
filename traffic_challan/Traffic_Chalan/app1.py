import os
import sqlite3
import urllib.parse
import streamlit as st

from violation_detection import (
    detect_violation,
    detect_number_plate,
    get_fine,
    get_user
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Traffic Challan System",
    page_icon="🚦",
    layout="wide"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHALAN_DB = os.path.join(BASE_DIR, "Chalan.db")
USER_DB = os.path.join(BASE_DIR, "user.db")
DRIVERS_DIR = os.path.join(BASE_DIR, "drivers")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

os.makedirs(DRIVERS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


# ============================================================
# CHALAN DATABASE
# ============================================================

def initialize_chalan_database():

    conn = sqlite3.connect(CHALAN_DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            violation_type TEXT UNIQUE,
            fine INTEGER
        )
    """)

    violations = [
        ("Triple Ride", 1000),
        ("No Parking", 100),
        ("No Helmet", 200),
        ("Overspeed", 1000)
    ]

    for violation, fine in violations:

        cursor.execute("""
            INSERT OR IGNORE INTO violations
            (violation_type, fine)
            VALUES (?, ?)
        """, (violation, fine))

    conn.commit()
    conn.close()


# ============================================================
# USER DATABASE
# ============================================================

def initialize_user_database():

    conn = sqlite3.connect(USER_DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            vehicle_reg TEXT UNIQUE NOT NULL,
            vehicle_type TEXT,
            vehnum TEXT,
            mobile TEXT,
            driver_photo TEXT
        )
    """)

    # --------------------------------------------------------
    # DEMO DRIVER DATA
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # Change vehicle numbers according to your real/demo data.
    #
    # driver1.jpg -> TS09PA3330
    # driver2.jpg -> TS10EX2850
    # driver3.jpg -> TS10ED8176
    # driver4.jpg -> TS09AB1234
    #
    # --------------------------------------------------------

    drivers = [
        (
            "Demo Driver 1",
            "TS09PA3330",
            "Scooty",
            "1662",
            "8688072565",
            "drivers/driver1.jpg"
        ),

        (
            "Demo Driver 2",
            "TS10EX2850",
            "Bike",
            "2850",
            "8688072565",
            "drivers/driver2.jpg"
        ),

        (
            "Demo Driver 3",
            "TS10ED8176",
            "Bike",
            "8176",
            "8688072565",
            "drivers/driver3.jpg"
        ),

        (
            "Demo Driver 4",
            "TS09AB1234",
            "Car",
            "1234",
            "8688072565",
            "drivers/driver4.jpg"
        )
    ]

    # --------------------------------------------------------
    # UPSERT
    # --------------------------------------------------------
    # Existing vehicle -> UPDATE
    # New vehicle -> INSERT
    # --------------------------------------------------------

    for driver in drivers:

        cursor.execute("""
            INSERT INTO users
            (
                name,
                vehicle_reg,
                vehicle_type,
                vehnum,
                mobile,
                driver_photo
            )
            VALUES (?, ?, ?, ?, ?, ?)

            ON CONFLICT(vehicle_reg)
            DO UPDATE SET
                name = excluded.name,
                vehicle_type = excluded.vehicle_type,
                vehnum = excluded.vehnum,
                mobile = excluded.mobile,
                driver_photo = excluded.driver_photo
        """, driver)

    conn.commit()
    conn.close()


# ============================================================
# INITIALIZE DATABASES
# ============================================================

initialize_chalan_database()
initialize_user_database()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 40px;
    font-weight: 700;
    margin-bottom: 5px;
}

.sub-title {
    font-size: 18px;
    color: #666;
    margin-bottom: 25px;
}

.owner-card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #ddd;
    background-color: #f8f9fa;
}

.plate-box {
    padding: 25px;
    border-radius: 15px;
    border: 2px solid #ddd;
    text-align: center;
    background-color: white;
}

.plate-text {
    font-size: 32px;
    font-weight: bold;
    letter-spacing: 4px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🚦 Traffic Challan")

    st.write(
        "AI-powered traffic violation "
        "detection and challan generation."
    )

    st.divider()

    st.subheader("⚙️ System Features")

    st.write("🚨 Violation Detection")
    st.write("🔢 Number Plate Detection")
    st.write("👤 Vehicle Owner Identification")
    st.write("💰 Automatic Fine Calculation")
    st.write("📷 Driver Photo")
    st.write("📱 WhatsApp Challan")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🚦 AI Traffic Challan System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'AI-powered traffic violation detection, '
    'number plate recognition and automated challan generation.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# IMAGE UPLOAD
# ============================================================

st.subheader("📷 Upload Traffic Image")

uploaded_file = st.file_uploader(
    "Upload a traffic image",
    type=["jpg", "jpeg", "png"]
)


# ============================================================
# PROCESS IMAGE
# ============================================================

if uploaded_file is not None:

    # Save uploaded image
    image_path = os.path.join(
        TEMP_DIR,
        uploaded_file.name
    )

    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Image uploaded successfully.")

    # Preview
    st.image(
        uploaded_file,
        caption="Uploaded Traffic Image",
        use_container_width=True
    )

    st.divider()

    # ========================================================
    # GENERATE CHALLAN BUTTON
    # ========================================================

    if st.button(
        "🚨 Generate Challan",
        type="primary",
        use_container_width=True
    ):

        # ====================================================
        # VIOLATION DETECTION
        # ====================================================

        with st.spinner("Detecting traffic violation..."):

            try:

                violation = detect_violation(image_path)

            except Exception as e:

                st.error(
                    f"Violation detection failed: {str(e)}"
                )

                st.stop()

        # ====================================================
        # FINE CALCULATION
        # ====================================================

        try:

            fine = get_fine(violation)

        except Exception:

            fine = 0

        # ====================================================
        # NUMBER PLATE DETECTION
        # ====================================================

        with st.spinner("Detecting vehicle number plate..."):

            try:

                number_plate = detect_number_plate(image_path)

            except Exception as e:

                st.error(
                    f"Number plate detection failed: {str(e)}"
                )

                st.stop()

        # ====================================================
        # CLEAN NUMBER PLATE
        # ====================================================

        if number_plate:

            number_plate = (
                str(number_plate)
                .upper()
                .replace(" ", "")
                .replace("-", "")
                .replace("\n", "")
                .strip()
            )

        else:

            number_plate = "NOT DETECTED"

        # ====================================================
        # RESULT HEADER
        # ====================================================

        st.markdown("---")

        st.header("🚨 Violation Detection Result")

        # ====================================================
        # METRICS
        # ====================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🚨 Violation",
                violation
            )

        with col2:

            st.metric(
                "💰 Fine Amount",
                f"₹ {fine}"
            )

        with col3:

            st.metric(
                "🔢 Number Plate",
                number_plate
            )

        st.divider()

        # ====================================================
        # FIND OWNER
        # ====================================================

        owner = None

        if number_plate != "NOT DETECTED":

            try:

                owner = get_user(number_plate)

            except Exception as e:

                st.error(
                    f"Owner database error: {str(e)}"
                )

        # ====================================================
        # OWNER FOUND
        # ====================================================

        if owner:

            st.success(
                "✅ Vehicle owner found successfully."
            )

            # ------------------------------------------------
            # OWNER DETAILS
            # ------------------------------------------------

            st.subheader("👤 Vehicle Owner Details")

            owner_col1, owner_col2 = st.columns([1, 2])

            # ------------------------------------------------
            # DRIVER PHOTO
            # ------------------------------------------------

            with owner_col1:

                driver_photo = owner.get(
                    "driver_photo"
                )

                if driver_photo:

                    # Convert relative path to absolute path
                    if not os.path.isabs(driver_photo):

                        photo_path = os.path.join(
                            BASE_DIR,
                            driver_photo
                        )

                    else:

                        photo_path = driver_photo

                    if os.path.exists(photo_path):

                        st.image(
                            photo_path,
                            caption="Driver Photo",
                            use_container_width=True
                        )

                    else:

                        st.warning(
                            "Driver photo not found."
                        )

                else:

                    st.warning(
                        "No driver photo registered."
                    )

            # ------------------------------------------------
            # OWNER INFORMATION
            # ------------------------------------------------

            with owner_col2:

                st.markdown(
                    '<div class="owner-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    f"**👤 Name:** "
                    f"{owner.get('name', 'N/A')}"
                )

                st.write(
                    f"**🚗 Vehicle Number:** "
                    f"{owner.get('vehicle_reg', 'N/A')}"
                )

                st.write(
                    f"**🚘 Vehicle Type:** "
                    f"{owner.get('vehicle_type', 'N/A')}"
                )

                st.write(
                    f"**🔢 Vehicle ID:** "
                    f"{owner.get('vehnum', 'N/A')}"
                )

                st.write(
                    f"**📱 Mobile:** "
                    f"{owner.get('mobile', 'N/A')}"
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            st.divider()

            # =================================================
            # DETECTED PLATE
            # =================================================

            st.subheader("🔢 Detected Number Plate")

            st.markdown(
                f"""
                <div class="plate-box">
                    <div>🔢 DETECTED NUMBER PLATE</div>
                    <div class="plate-text">
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

            st.subheader("🧾 Challan Summary")

            summary_col1, summary_col2 = st.columns(2)

            with summary_col1:

                st.write(
                    f"**Vehicle:** {number_plate}"
                )

                st.write(
                    f"**Owner:** "
                    f"{owner.get('name', 'N/A')}"
                )

                st.write(
                    f"**Violation:** {violation}"
                )

            with summary_col2:

                st.write(
                    f"**Fine Amount:** ₹{fine}"
                )

                st.write(
                    f"**Vehicle Type:** "
                    f"{owner.get('vehicle_type', 'N/A')}"
                )

                st.write(
                    "**Status:** ⚠️ Violation Recorded"
                )

            st.divider()

            # =================================================
            # WHATSAPP CHALLAN
            # =================================================

            st.subheader("📱 WhatsApp Challan")

            mobile = owner.get(
                "mobile",
                ""
            )

            if mobile:

                # Remove spaces/symbols
                mobile = (
                    str(mobile)
                    .replace("+", "")
                    .replace(" ", "")
                    .replace("-", "")
                )

                # Indian 10 digit number
                if len(mobile) == 10:

                    whatsapp_number = "91" + mobile

                else:

                    whatsapp_number = mobile

                # ------------------------------------------------
                # MESSAGE
                # ------------------------------------------------

                message = f"""
🚦 TRAFFIC CHALLAN NOTIFICATION

Dear {owner.get('name', 'Vehicle Owner')},

Your vehicle has been detected with a traffic violation.

Vehicle Number: {number_plate}
Violation: {violation}
Fine Amount: ₹{fine}

Please pay the applicable traffic fine.

Thank you.
AI Traffic Challan System
"""

                encoded_message = urllib.parse.quote(
                    message.strip()
                )

                whatsapp_url = (
                    f"https://wa.me/"
                    f"{whatsapp_number}"
                    f"?text={encoded_message}"
                )

                st.link_button(
                    "📱 Send Challan on WhatsApp",
                    whatsapp_url,
                    use_container_width=True
                )

                st.info(
                    "Click the button to open WhatsApp "
                    "with the challan message."
                )

            else:

                st.warning(
                    "No mobile number registered "
                    "for this vehicle."
                )

        # ====================================================
        # OWNER NOT FOUND
        # ====================================================

        else:

            st.warning(
                "⚠️ Vehicle number was detected, "
                "but no matching owner was found."
            )

            st.markdown(
                f"""
                <div class="plate-box">
                    <div>🔢 DETECTED NUMBER PLATE</div>
                    <div class="plate-text">
                        {number_plate}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.info(
                "Please register this vehicle in the "
                "User Database before generating the "
                "owner notification."
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🚦 AI Traffic Challan System | "
    "Violation Detection • Number Plate Recognition • "
    "Owner Identification • Automatic Fine • WhatsApp Notification"
)
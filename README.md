# 🚦 AI Traffic Challan System

An AI-powered Traffic Challan System that detects traffic violations from images, identifies vehicle number plates, retrieves registered vehicle-owner details, calculates applicable fines, and generates a digital challan notification.

## ✨ Features

- 🚨 Traffic violation detection
- 🔢 Vehicle number plate detection
- 👤 Vehicle owner identification
- 💰 Automatic fine calculation
- 📷 Driver photo retrieval
- 📄 Digital challan summary
- 📱 WhatsApp challan notification
- 🗄️ Database-based vehicle and owner management
- 🌐 Streamlit web dashboard

## 🛠️ Technologies Used

- Python
- Streamlit
- Groq AI
- SQL / SQLite
- OpenCV
- Pillow
- Requests
- WhatsApp Web API

## 🔄 Project Workflow


Upload Traffic Image
        ↓
AI Violation Detection
        ↓
Number Plate Detection
        ↓
Vehicle Owner Search
        ↓
Fine Calculation
        ↓
Challan Generation
        ↓
WhatsApp Notification

### 📂 Project Structure

traffic_challan/
│
├── traffic_challan/
│   ├── Traffic_Chalan/
│   │   ├── app1.py
│   │   ├── violation_detection.py
│   │   ├── Chalan.database.py
│   │   ├── create_database.py
│   │   ├── requirements.txt
│   │   │
│   │   ├── drivers/
│   │   ├── images/
│   │   ├── pages/
│   │
│   └── app.py
│
├── .gitignore
└── README.md

### ▶️ Run the Application

Go to the application folder:

cd traffic_challan/Traffic_Chalan

### Run Streamlit:

streamlit run app1.py

The application will open in your browser.

### 🖥️ Dashboard

The dashboard allows users to:

Upload a traffic violation image.
Detect the violation using AI.
Detect the vehicle number plate.
Find registered owner information.
Calculate the fine.
Display challan information.
Send the challan information through WhatsApp.

### 🎯 Supported Violations

The system is designed to detect traffic violations such as:

No Helmet
No Parking
Triple Riding
Overspeed

### 👩‍💻 Author

#### Ramya Maicharla

B.Tech – Artificial Intelligence & Data Science

GitHub: https://github.com/ramyamaicharla

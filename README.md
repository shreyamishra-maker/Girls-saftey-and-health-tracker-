# 💗 Girls Safety & Health Assistant

A **Python desktop application** focused on women's safety, health tracking, and emergency support.  
Built with **Tkinter + SQLite** — no internet required. All data is stored locally.

---

## 📁 Project Structure

```
girls_safety_app/
├── main_app.py       ← Main application + all UI screens
├── database.py       ← SQLite database layer (all CRUD operations)
├── safety_logic.py   ← SOS, location, self-defense tips, helplines
├── health_logic.py   ← Cycle prediction, symptom analysis, health tips
└── README.md         ← This file
```

---

## 🚀 Quick Start

### 1. Requirements

Python 3.8 or higher is required. All libraries used are **part of Python's standard library**:

| Library   | Purpose                     |
|-----------|-----------------------------|
| `tkinter` | GUI framework               |
| `sqlite3` | Local database              |
| `hashlib` | Password hashing (SHA-256)  |
| `threading` | Background reminder check |
| `datetime` | Date calculations           |
| `random`  | Location simulation         |

> ✅ **No pip install needed** for basic functionality.

### 2. Run the App

```bash
# Navigate to the project folder
cd girls_safety_app

# Run the app
python main_app.py
```

### 3. First Time Use

1. Click **"Create Account"** on the login screen
2. Fill in your name, age, email, and password
3. Log in with your credentials
4. Add **emergency contacts** under the Safety tab
5. Start logging your health data!

---

## 🌟 Features Overview

### 🏠 Home Dashboard
- Personalized greeting with time-of-day awareness
- Current menstrual cycle phase display (Menstrual / Follicular / Ovulation / Luteal)
- Next period prediction based on your logged history
- Daily rotating health tip

### 🚨 Safety Tab
- **SOS Alert Button** — Shows alert message with simulated GPS location
- **Emergency Contacts** — Add/delete contacts (name, phone, relation)
- **Fake Call** — Simulate an incoming call to escape uncomfortable situations
- **Call Contacts** — Displays contact info for quick dialing

### 🩺 Health Tracking
- **Period Logger** — Log start/end dates and cycle length
- **Symptom Tracker** — Track headache, cramps, fatigue, bloating, mood daily
- **Symptom Analysis** — Auto-generated summary with wellness tips
- **Medical History Notes** — Add/view/delete personal health notes

### 📍 Location Tab
- Simulated GPS location display with coordinates and Google Maps link
- Location sharing message composer for emergency contacts

### ⏰ Reminders
- Set reminders for: Period, Medication, Health Checkup, Vitamins, Exercise
- Background checker alerts you when reminders are due
- Mark reminders as done

### 🛡️ Tips & Helplines
- 10 self-defense tips with practical instructions
- Quick safety guidelines
- Emergency helpline numbers (India + Global)

### 👤 Profile
- View and edit your name, age, blood group
- All data stored locally in SQLite

---

## 🔧 Optional Enhancements (Advanced)

### Real GPS Location
Install `geopy` for real IP-based location:
```bash
pip install geopy
```
Then replace `get_current_location()` in `safety_logic.py`:
```python
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="safeher")
location = geolocator.geocode("your city")
```

### SMS Alerts via Twilio
```bash
pip install twilio
```
Use Twilio's API to send real SMS to emergency contacts on SOS.

### Voice SOS Command
```bash
pip install SpeechRecognition pyaudio
```
Listen for a keyword like "help" and trigger SOS automatically.

---

## 🔒 Privacy & Security

- All data is stored in **`safety_app.db`** (SQLite) on your local machine
- Passwords are hashed with **SHA-256** before storage
- No data is ever transmitted to any server
- Delete `safety_app.db` to completely wipe all data

---

## 📞 Emergency Numbers (India)

| Service                    | Number     |
|----------------------------|------------|
| Police Emergency           | 100        |
| National Emergency         | 112        |
| Women Helpline             | 1091       |
| Domestic Violence Helpline | 181        |
| Ambulance                  | 108        |
| Child Helpline             | 1098       |
| Cyber Crime                | 1930       |
| Mental Health (iCall)      | 9152987821 |

---

## 💡 Tips for Beginners

- The code is split into **4 separate files** for clarity:
  - `database.py` handles all data — you can modify this without touching the UI
  - `safety_logic.py` handles safety features — add your own tips here
  - `health_logic.py` handles health calculations — customize cycle logic here
  - `main_app.py` handles everything you see — customize colors and layout here

- Look for the `C = { ... }` dictionary in `main_app.py` to change the color theme
- The `FONT_*` variables control all text styles throughout the app

---

*Made with 💗 for women's safety and wellness*

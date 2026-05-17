"""
safety_logic.py - Safety features, location simulation, SOS, and self-defense tips
"""

import random
import math
from datetime import datetime

# ─────────────────────────────────────────────
#  LOCATION SIMULATION
#  (Replace get_current_location() with a real
#   GPS library like gpsd or geopy if available)
# ─────────────────────────────────────────────

# Simulated base coordinates (New Delhi, India as default)
_BASE_LAT = 28.6139
_BASE_LON = 77.2090


def get_current_location() -> dict:
    """
    Simulate GPS location with slight random drift.
    In a real deployment, replace this with actual GPS/IP geolocation.
    Returns dict with latitude, longitude, and address string.
    """
    lat = _BASE_LAT + random.uniform(-0.005, 0.005)
    lon = _BASE_LON + random.uniform(-0.005, 0.005)

    # Simulated address – replace with reverse geocoding API call
    address = f"Near Connaught Place, New Delhi ({lat:.4f}°N, {lon:.4f}°E)"
    return {
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "address": address,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "maps_link": f"https://maps.google.com/?q={lat},{lon}"
    }


# ─────────────────────────────────────────────
#  SOS MESSAGE COMPOSER
# ─────────────────────────────────────────────

def compose_sos_message(user_name: str, location: dict) -> str:
    """Build the SOS alert text that would be sent to emergency contacts."""
    return (
        f"🚨 EMERGENCY SOS ALERT 🚨\n\n"
        f"I NEED HELP! My name is {user_name}.\n"
        f"📍 My current location:\n"
        f"   {location['address']}\n"
        f"   Coordinates: {location['latitude']}, {location['longitude']}\n"
        f"   Google Maps: {location['maps_link']}\n\n"
        f"⏰ Alert sent at: {location['timestamp']}\n\n"
        f"Please contact me or call the police immediately!\n"
        f"India Emergency: 112 | Women Helpline: 1091"
    )


def compose_share_location_message(user_name: str, location: dict) -> str:
    """Compose a location-sharing message (non-emergency)."""
    return (
        f"📍 Location Update from {user_name}\n\n"
        f"I'm currently at:\n"
        f"   {location['address']}\n"
        f"   View on Maps: {location['maps_link']}\n\n"
        f"Time: {location['timestamp']}"
    )


# ─────────────────────────────────────────────
#  SELF-DEFENSE TIPS
# ─────────────────────────────────────────────

SELF_DEFENSE_TIPS = [
    {
        "title": "Stay Aware of Your Surroundings",
        "tip": "Always be conscious of what's happening around you. Avoid using headphones "
               "in both ears or looking at your phone while walking in unfamiliar areas.",
        "icon": "👁️"
    },
    {
        "title": "Trust Your Instincts",
        "tip": "If something feels wrong, it probably is. Don't second-guess your gut feeling. "
               "Move away from situations that make you uncomfortable immediately.",
        "icon": "💭"
    },
    {
        "title": "Use Your Voice",
        "tip": "Shout 'FIRE!' or 'HELP!' loudly in public – it draws more attention than 'Stop!'. "
               "Make noise to attract bystanders and create confusion for the attacker.",
        "icon": "📣"
    },
    {
        "title": "Eyes, Nose, Throat, Groin",
        "tip": "If physically attacked, target vulnerable spots: jab fingers at eyes, strike the "
               "nose with the heel of your palm, elbow the throat, or knee the groin to escape.",
        "icon": "🥊"
    },
    {
        "title": "Walk Confidently",
        "tip": "Walk with purpose, keep your head up, and make brief eye contact. "
               "Attackers often target people who seem distracted or uncertain.",
        "icon": "🚶‍♀️"
    },
    {
        "title": "Share Your Location",
        "tip": "Always tell someone where you're going and when you'll be back. "
               "Use location-sharing apps with trusted contacts when traveling alone.",
        "icon": "📍"
    },
    {
        "title": "Carry Permitted Safety Items",
        "tip": "Consider carrying a whistle, personal alarm, or pepper spray (where legally permitted). "
               "A loud alarm can disorient attackers and attract help quickly.",
        "icon": "🔔"
    },
    {
        "title": "Safe Transport Choices",
        "tip": "Use trusted cab services, share ride details with family, sit behind the driver, "
               "never share personal info with drivers, and keep your phone charged.",
        "icon": "🚗"
    },
    {
        "title": "Plan Your Route",
        "tip": "Know your route before you travel, prefer well-lit and populated paths, "
               "have backup routes in mind, and identify safe places (shops, police booths) along the way.",
        "icon": "🗺️"
    },
    {
        "title": "Digital Safety",
        "tip": "Be cautious about sharing your live location on social media. "
               "Don't announce when your house will be empty. Use strong passwords and 2FA.",
        "icon": "💻"
    },
]


# ─────────────────────────────────────────────
#  HELPLINE NUMBERS (India + International)
# ─────────────────────────────────────────────

HELPLINES = [
    {"name": "Police Emergency",           "number": "100",  "country": "India"},
    {"name": "National Emergency",          "number": "112",  "country": "India"},
    {"name": "Women Helpline",              "number": "1091", "country": "India"},
    {"name": "Women Helpline (Domestic Violence)", "number": "181", "country": "India"},
    {"name": "Child Helpline",              "number": "1098", "country": "India"},
    {"name": "Ambulance",                   "number": "108",  "country": "India"},
    {"name": "Cyber Crime Helpline",        "number": "1930", "country": "India"},
    {"name": "Anti-Stalking / Harassment",  "number": "100",  "country": "India"},
    {"name": "Mental Health Helpline (iCall)", "number": "9152987821", "country": "India"},
    {"name": "International SOS",           "number": "112",  "country": "Global"},
]


# ─────────────────────────────────────────────
#  SAFETY GUIDELINES
# ─────────────────────────────────────────────

SAFETY_GUIDELINES = [
    "📱 Save emergency numbers on speed dial.",
    "🔋 Always keep your phone charged above 30%.",
    "📸 Screenshot and save cab/auto details before riding.",
    "👥 Inform a trusted person before late-night outings.",
    "💡 Prefer well-lit, public routes over shortcuts at night.",
    "🚨 Do not hesitate to call 112 – false alarm is better than danger.",
    "🏠 Do not open your door to strangers without verification.",
    "📷 If you feel followed, enter a public place and call for help.",
    "🤝 Connect with neighbors and community safety groups.",
    "📰 Stay updated on local safety advisories in your area.",
]

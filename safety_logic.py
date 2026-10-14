"""
safety_logic.py - Safety features, location simulation, SOS, and self-defense tips
"""

import json
import urllib.error
import urllib.request
from datetime import datetime

# ─────────────────────────────────────────────
#  APPROXIMATE LOCATION VIA PUBLIC IP
# ─────────────────────────────────────────────

def get_current_location() -> dict:
    """
    Return approximate IP-based location from ipapi.co.

    This is NOT device GPS and may be inaccurate (especially with VPNs,
    mobile networks, or corporate networks). The provider receives the
    requester's public IP address. If the service/network is unavailable,
    return an explicit unavailable result rather than inventing coordinates.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "latitude": None,
        "longitude": None,
        "address": "Location unavailable. Check internet access and try again.",
        "timestamp": timestamp,
        "maps_link": None,
        "source": "unavailable",
        "accuracy": "unknown",
    }
    request = urllib.request.Request(
        "https://ipapi.co/json/",
        headers={"User-Agent": "GirlsSafetyHealthAssistant/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        lat = data.get("latitude")
        lon = data.get("longitude")
        if lat is None or lon is None:
            return result

        lat, lon = float(lat), float(lon)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return result

        parts = [data.get("city"), data.get("region"), data.get("country_name")]
        address = ", ".join(str(part) for part in parts if part)
        if not address:
            address = "Approximate area from public IP"

        return {
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "address": address + " (approximate IP location, not GPS)",
            "timestamp": timestamp,
            "maps_link": f"https://maps.google.com/?q={lat},{lon}",
            "source": "ip",
            "accuracy": "approximate; may be city-level",
        }
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return result


# ─────────────────────────────────────────────
#  SOS MESSAGE COMPOSER
# ─────────────────────────────────────────────

def compose_sos_message(user_name: str, location: dict) -> str:
    """Build the SOS alert text that would be sent to emergency contacts."""
    return (
        f"🚨 EMERGENCY SOS ALERT 🚨\n\n"
        f"I NEED HELP! My name is {user_name}.\n"
        f"📍 Location:\n"
        f"   {location['address']}\n"
        + (f"   Coordinates: {location['latitude']}, {location['longitude']}\n"
           f"   Google Maps: {location['maps_link']}\n" if location.get("latitude") is not None
           else "   Coordinates unavailable; no location link was generated.\n")
        + "\n"
        f"⏰ Message prepared at: {location['timestamp']}\n\n"
        f"⚠️ This app currently prepares an SOS message; it does NOT send SMS/calls automatically.\n\n"
        f"Please contact me or call the police immediately!\n"
        f"India Emergency: 112 | Women Helpline: 1091"
    )


def compose_share_location_message(user_name: str, location: dict) -> str:
    """Compose a location-sharing message (non-emergency)."""
    return (
        f"📍 Location Update from {user_name}\n\n"
        f"⚠️ This is approximate IP-based location, not live GPS.\n\n"
        f"Reported area:\n"
        f"   {location['address']}\n"
        + (f"   View on Maps: {location['maps_link']}\n\n" if location.get("maps_link")
           else "   Map link unavailable.\n\n")
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

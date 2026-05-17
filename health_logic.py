"""
health_logic.py - Menstrual cycle prediction, symptom analysis, and health insights
"""

from datetime import datetime, timedelta
from database import get_cycles, predict_next_cycle, get_symptom_logs


# ─────────────────────────────────────────────
#  CYCLE PREDICTION & INSIGHTS
# ─────────────────────────────────────────────

def get_cycle_phase(user_id: int) -> dict:
    """
    Determine the current phase of the menstrual cycle.
    Returns phase name, description, and cycle day number.
    """
    cycles = get_cycles(user_id, limit=1)
    if not cycles:
        return {"phase": "Unknown", "day": 0, "description": "Log your first period to see insights."}

    last_start = datetime.strptime(cycles[0]["start_date"], "%Y-%m-%d")
    cycle_length = cycles[0]["cycle_length"] or 28
    today = datetime.today()
    day_in_cycle = (today - last_start).days % cycle_length + 1

    if day_in_cycle <= 5:
        phase = "Menstrual"
        desc = "Your period is active. Rest, stay hydrated, and use a heating pad for cramps."
    elif day_in_cycle <= 13:
        phase = "Follicular"
        desc = "Energy levels rise. Great time for new projects, social activities, and exercise."
    elif day_in_cycle <= 16:
        phase = "Ovulation"
        desc = "Peak energy and confidence. You may feel more social and communicative today."
    else:
        phase = "Luteal"
        desc = "PMS symptoms may appear. Practice self-care, reduce sugar, and get enough sleep."

    return {
        "phase": phase,
        "day": day_in_cycle,
        "description": desc,
        "cycle_length": cycle_length
    }


def get_fertility_window(user_id: int) -> dict:
    """Estimate the fertile window based on last period and average cycle."""
    cycles = get_cycles(user_id, limit=3)
    if not cycles:
        return {"fertile_start": "N/A", "fertile_end": "N/A", "ovulation_day": "N/A"}

    avg_length = sum(c["cycle_length"] for c in cycles) / len(cycles)
    last_start = datetime.strptime(cycles[0]["start_date"], "%Y-%m-%d")

    ovulation = last_start + timedelta(days=int(avg_length) - 14)
    fertile_start = ovulation - timedelta(days=5)
    fertile_end = ovulation + timedelta(days=1)

    return {
        "fertile_start": fertile_start.strftime("%b %d"),
        "fertile_end": fertile_end.strftime("%b %d"),
        "ovulation_day": ovulation.strftime("%b %d")
    }


# ─────────────────────────────────────────────
#  SYMPTOM ANALYSIS
# ─────────────────────────────────────────────

def analyze_symptoms(user_id: int) -> str:
    """
    Return a plain-text summary of the user's recent symptoms
    and simple wellness recommendations.
    """
    logs = get_symptom_logs(user_id, limit=5)
    if not logs:
        return "No symptom data yet. Start logging daily to get insights!"

    total = len(logs)
    headache_count = sum(1 for l in logs if l["headache"])
    cramps_count = sum(1 for l in logs if l["cramps"])
    fatigue_count = sum(1 for l in logs if l["fatigue"])
    bloating_count = sum(1 for l in logs if l["bloating"])

    moods = [l["mood"] for l in logs if l["mood"]]
    most_common_mood = max(set(moods), key=moods.count) if moods else "Not recorded"

    lines = [f"📊 Symptom Summary (last {total} logs)\n"]
    lines.append(f"  🤕 Headache:  {headache_count}/{total} days")
    lines.append(f"  😣 Cramps:    {cramps_count}/{total} days")
    lines.append(f"  😴 Fatigue:   {fatigue_count}/{total} days")
    lines.append(f"  😮 Bloating:  {bloating_count}/{total} days")
    lines.append(f"  💭 Mood:      {most_common_mood} (most frequent)\n")

    # Simple wellness tips based on dominant symptom
    if headache_count >= total // 2:
        lines.append("💡 Tip: Frequent headaches detected. Drink more water and reduce screen time.")
    if cramps_count >= total // 2:
        lines.append("💡 Tip: Cramps are common. Try gentle yoga and magnesium-rich foods.")
    if fatigue_count >= total // 2:
        lines.append("💡 Tip: Fatigue noted. Aim for 7–8 hours of sleep and check iron levels.")

    return "\n".join(lines)


# ─────────────────────────────────────────────
#  MOOD OPTIONS
# ─────────────────────────────────────────────

MOOD_OPTIONS = ["😊 Happy", "😐 Neutral", "😢 Sad", "😠 Irritable", "😰 Anxious", "😴 Tired", "😍 Energetic"]


# ─────────────────────────────────────────────
#  HEALTH TIPS (rotated daily)
# ─────────────────────────────────────────────

HEALTH_TIPS = [
    "💧 Drink at least 8 glasses of water daily to reduce bloating and cramps.",
    "🥗 Include iron-rich foods (spinach, lentils) during your period to fight fatigue.",
    "🧘 10 minutes of meditation daily can significantly reduce PMS anxiety.",
    "🏃 Regular exercise helps regulate hormones and boosts mood naturally.",
    "🌙 Quality sleep is crucial – aim for consistent sleep and wake times.",
    "☀️ Vitamin D (from sunlight or supplements) supports hormonal balance.",
    "🍫 Dark chocolate (70%+) contains magnesium that helps with cramps.",
    "🚫 Limit caffeine and alcohol during your period – they worsen dehydration.",
    "📅 Track your cycle for 3+ months to notice patterns and prepare better.",
    "🩺 Schedule an annual gynecological check-up for preventive care.",
    "🌿 Ginger tea is a natural remedy for nausea and menstrual discomfort.",
    "💊 If cramps severely disrupt your life, consult a doctor – it may be endometriosis.",
]


def get_daily_tip() -> str:
    """Return a tip based on the day of the year."""
    day_of_year = datetime.today().timetuple().tm_yday
    return HEALTH_TIPS[day_of_year % len(HEALTH_TIPS)]


import json
from pathlib import Path
from datetime import datetime, timezone
from xml.sax.saxutils import escape

# File locations
DATA_FILE = Path("data/neopat.json")
OUTPUT_FILE = Path("assets/neopat-score.svg")


def safe(value):
    return escape(str(value))


def percentage(value):
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def generate_card():

    # Check JSON file
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "data/neopat.json not found. Run fetch_neopat.py first."
        )

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Read NeoPAT metrics
    metrics = data.get("overview") or data.get("patMetrics")

    if not metrics:
        raise ValueError("NeoPAT overview metrics not found.")

    coding = metrics.get("c_score", 0)
    mcq = metrics.get("m_score", 0)
    total = metrics.get("neo_score", coding + mcq)

    level = metrics.get("level", "Beginner")

    attended = metrics.get("total_questions_attended", 0)

    solved = (
        int(metrics.get("easy_correct", 0))
        + int(metrics.get("medium_correct", 0))
        + int(metrics.get("hard_correct", 0))
    )

    coding_accuracy = percentage(metrics.get("c_accuracy"))
    mcq_accuracy = percentage(metrics.get("m_accuracy"))

    # Last synchronization time
    synced = data.get("_synced_at")

    if synced:
        try:
            date = datetime.fromisoformat(
                synced.replace("Z", "+00:00")
            )
            last_updated = date.strftime("%d %b %Y, %H:%M UTC")
        except ValueError:
            last_updated = "Recently"
    else:
        last_updated = "Not available"

    # SVG card design
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="900" height="340" viewBox="0 0 900 340">

    <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#0d1117"/>
        <stop offset="100%" stop-color="#0d1117"/>
    </linearGradient>

    <linearGradient id="blue" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#58a6ff"/>
        <stop offset="100%" stop-color="#58a6ff"/>
    </linearGradient>
</defs>

    <!-- Background -->
    <rect x="1" y="1" width="898" height="338"
          rx="22" fill="url(#background)"
          stroke="#30363d" stroke-width="2"/>

    <!-- Header -->
    <text x="35" y="48" fill="#c9d1d9"
          font-family="Arial" font-size="23"
          font-weight="bold">
        NEOPAT PERFORMANCE
    </text>

    <rect x="740" y="22" width="125" height="31"
          rx="15" fill="#238636"/>

    <text x="802" y="43" fill="#ffffff"
          font-family="Arial" font-size="12"
          text-anchor="middle" font-weight="bold">
        AUTO SYNC
    </text>

    <!-- Overall Score -->
    <text x="36" y="95" fill="#8b949e"
          font-family="Arial" font-size="13">
        OVERALL SCORE
    </text>

    <text x="34" y="165" fill="#c9d1d9"
          font-family="Arial" font-size="65"
          font-weight="bold">
        {safe(total)}
    </text>

    <text x="36" y="197" fill="#58a6ff"
          font-family="Arial" font-size="17">
        Level {safe(level)}
    </text>

    <!-- Divider -->
    <line x1="330" y1="78" x2="330" y2="235"
          stroke="#30363d"/>

    <!-- Coding -->
    <text x="370" y="105" fill="#8b949e"
          font-family="Arial" font-size="13">
        CODING SCORE
    </text>

    <text x="370" y="150" fill="#58a6ff"
          font-family="Arial" font-size="38"
          font-weight="bold">
        {safe(coding)}
    </text>

    <text x="370" y="180" fill="#c9d1d9"
          font-family="Arial" font-size="14">
        Accuracy: {safe(coding_accuracy)}
    </text>

    <!-- MCQ -->
    <text x="620" y="105" fill="#8b949e"
          font-family="Arial" font-size="13">
        MCQ SCORE
    </text>

    <text x="620" y="150" fill="#3fb950"
          font-family="Arial" font-size="38"
          font-weight="bold">
        {safe(mcq)}
    </text>

    <text x="620" y="180" fill="#c9d1d9"
          font-family="Arial" font-size="14">
        Accuracy: {safe(mcq_accuracy)}
    </text>

    <!-- Bottom section -->
    <line x1="35" y1="235" x2="865" y2="235"
          stroke="#30363d"/>

    <text x="36" y="270" fill="#8b949e"
          font-family="Arial" font-size="13">
        QUESTIONS SOLVED
    </text>

    <text x="36" y="307" fill="#c9d1d9"
          font-family="Arial" font-size="25"
          font-weight="bold">
        {solved} / {attended}
    </text>

    <text x="865" y="270" fill="#8b949e"
          font-family="Arial" font-size="12"
          text-anchor="end">
        LAST SYNCHRONIZED
    </text>

    <text x="865" y="307" fill="#3fb950"
          font-family="Arial" font-size="14"
          text-anchor="end">
        {safe(last_updated)}
    </text>

    </svg>
    """

    # Create assets folder if missing
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save SVG
    OUTPUT_FILE.write_text(svg, encoding="utf-8")

    print("NeoPAT card generated successfully!")
    print("Overall Score:", total)
    print("Coding:", coding)
    print("MCQ:", mcq)
    print("Questions Solved:", solved)
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_card()

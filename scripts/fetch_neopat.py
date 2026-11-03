
import os
import json
import requests
from pathlib import Path
from datetime import datetime, timezone

API_URL = "https://api.examly.io/api/sps_metrics/getOverView"

def fetch_neopat():
    authorization = os.getenv("NEOPAT_AUTHORIZATION")

    if not authorization:
        raise RuntimeError("Missing NEOPAT_AUTHORIZATION secret")

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Authorization": authorization,
        "Referer": "https://rrgi364.examly.io/dashboard",
        "User-Agent": "NeoPAT-GitHub-Card/1.0"
    }

    payload = {
        "metrics_type": "overview_metrics",
        "contribution_year": str(datetime.now(timezone.utc).year),
        "contribution_type": "coding"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code in (401, 403):
        raise RuntimeError(
            "Authentication failed. The NeoPAT credential may have expired."
        )

    response.raise_for_status()

    result = response.json()

    if not result.get("success"):
        raise RuntimeError("NeoPAT API returned unsuccessful response")

    data = result["data"]

    overview = data.get("overview") or data.get("patMetrics")

    if not overview or "neo_score" not in overview:
        raise RuntimeError("NeoPAT score missing from API response")

    data["_synced_at"] = datetime.now(timezone.utc).isoformat()

    output = Path("data/neopat.json")
    output.parent.mkdir(exist_ok=True)

    temp = output.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2))
    temp.replace(output)

    print("NeoPAT score updated:", overview["neo_score"])


if __name__ == "__main__":
    fetch_neopat()

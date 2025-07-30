import json
import csv
from pathlib import Path

# === Load your saved JSON file ===
json_file = Path("predictions_20250730.json")
csv_file = Path("clean_predictions_20250730.csv")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# === Prepare CSV headers ===
headers = [
    "time", "home_team", "away_team",
    "odds_home_win", "odds_draw", "odds_away_win",
    "odds_1X", "odds_X2", "odds_12",
    "under_odds", "over_odds", "score"
]

# === Utility function to extract parts ===
def parse_text(text):
    import re

    # Extract time (e.g., 13:30)
    time_match = re.match(r"^(\d{2}:\d{2})", text)
    time = time_match.group(1) if time_match else ""

    # Remove time from text
    remaining = text[len(time):]

    # Try to extract odds using regular expressions
    odds_pattern = r"(1)(\d+\.\d+)(X)(\d+\.\d+)(2)(\d+\.\d+)(1X)(\d+\.\d+)(X2)(\d+\.\d+)(12)(\d+\.\d+)(Under )(\d+\.\d+)(Over )(\d+\.\d+)"
    odds_match = re.search(odds_pattern, remaining)

    if not odds_match:
        return [""] * 11

    odds_values = odds_match.groups()

    # Extract team names before odds section
    odds_start = odds_match.start()
    team_segment = remaining[:odds_start]
    teams = re.findall(r'[A-Z][a-z]+(?: [A-Z][a-z]+)*', team_segment)
    home_team = " ".join(teams[:len(teams)//2])
    away_team = " ".join(teams[len(teams)//2:])

    return [
        time,
        home_team.strip(),
        away_team.strip(),
        odds_values[1],
        odds_values[3],
        odds_values[5],
        odds_values[7],
        odds_values[9],
        odds_values[11],
        odds_values[13],
        odds_values[15],
    ]

# === Convert and Save to CSV ===
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)

    for item in data:
        row = parse_text(item["text"])
        row.append(item.get("score", ""))
        writer.writerow(row)

print(f"✅ Clean CSV created: {csv_file}")

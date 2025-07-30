import json
import csv
import re
from pathlib import Path

# === Locate latest JSON file in /data ===
data_dir = Path("data")
json_files = sorted(data_dir.glob("predictions_*.json"), reverse=True)
if not json_files:
    raise FileNotFoundError("❌ No JSON files found in 'data/' directory.")

json_file = json_files[0]
csv_dir = Path("clean_data")
csv_dir.mkdir(exist_ok=True)
csv_file = csv_dir / json_file.with_suffix(".csv").name.replace("predictions_", "clean_")

# === CSV Headers ===
headers = [
    "time", "home_team", "away_team",
    "odds_home_win", "odds_draw", "odds_away_win",
    "odds_1X", "odds_X2", "odds_12",
    "under_odds", "over_odds", "score"
]

def parse_text(text):
    try:
        # Extract time
        time_match = re.match(r"^(\d{2}:\d{2})", text)
        time = time_match.group(1) if time_match else ""
        remaining = text[len(time):]

        # Extract odds
        odds_pattern = r"(1)(\d+\.\d+)(X)(\d+\.\d+)(2)(\d+\.\d+)(1X)(\d+\.\d+)(X2)(\d+\.\d+)(12)(\d+\.\d+)(Under )(\d+\.\d+)(Over )(\d+\.\d+)"
        odds_match = re.search(odds_pattern, remaining)
        if not odds_match:
            raise ValueError("Odds pattern not found.")

        odds = odds_match.groups()
        odds_start = odds_match.start()
        team_segment = remaining[:odds_start]
        teams = re.findall(r'[A-Z][a-z]+(?: [A-Z][a-z]+)*', team_segment)

        home_team = " ".join(teams[:len(teams)//2])
        away_team = " ".join(teams[len(teams)//2:])

        return [
            time,
            home_team.strip(),
            away_team.strip(),
            odds[1], odds[3], odds[5],  # 1, X, 2
            odds[7], odds[9], odds[11],  # 1X, X2, 12
            odds[13], odds[15],  # Under, Over
        ]
    except Exception as e:
        print(f"⚠️ Skipped entry due to error: {e}")
        return [""] * 11

# === Load, Parse, Write CSV ===
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)

    for item in data:
        row = parse_text(item["text"])
        row.append(item.get("score", ""))
        writer.writerow(row)

print(f"✅ Clean CSV created: {csv_file}")

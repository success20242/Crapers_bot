import json
import csv
from pathlib import Path
import re

json_file = Path("data/predictions_20250730.json")
csv_file = Path("clean_data/clean_20250730.csv")
csv_file.parent.mkdir(exist_ok=True)  # ensure folder exists

headers = [
    "time", "home_team", "away_team",
    "odds_home_win", "odds_draw", "odds_away_win",
    "odds_1X", "odds_X2", "odds_12",
    "under_odds", "over_odds", "score"
]

def parse_text(text):
    # 1. Extract time (e.g. 13:30)
    time_match = re.match(r"(\d{2}:\d{2})", text)
    time = time_match.group(1) if time_match else ""

    # 2. Find where odds start - look for the first digit with decimals after time
    odds_start_idx = None
    for m in re.finditer(r"\d+\.\d+", text):
        if time and m.start() > len(time):
            odds_start_idx = m.start()
            break
        elif not time:
            odds_start_idx = m.start()
            break
    if odds_start_idx is None:
        return None  # no odds found

    # 3. Extract teams: text between time and odds start
    team_str = text[len(time):odds_start_idx].strip()
    # Split teams by uppercase letters followed by lowercase letters (approximation)
    teams = re.findall(r"[A-Z][a-z]+(?: [A-Z][a-z]+)*", team_str)
    if len(teams) < 2:
        # fallback: try splitting by uppercase letters but joined names
        teams = re.findall(r"[A-Z][a-z]+", team_str)

    if len(teams) < 2:
        return None  # can't extract teams properly

    home_team = " ".join(teams[:len(teams)//2])
    away_team = " ".join(teams[len(teams)//2:])

    # 4. Extract odds: all decimal numbers in the remaining text after odds_start_idx
    odds_text = text[odds_start_idx:]
    odds = re.findall(r"\d+\.\d+", odds_text)
    if len(odds) < 9:
        # Not enough odds found, skip entry
        return None

    # Map odds to respective fields
    odds_home_win = odds[0]
    odds_draw = odds[1]
    odds_away_win = odds[2]
    odds_1X = odds[3]
    odds_X2 = odds[4]
    odds_12 = odds[5]
    under_odds = odds[6]
    over_odds = odds[7]
    # Some texts might have extra odds, ignore

    return [
        time,
        home_team.strip(),
        away_team.strip(),
        odds_home_win,
        odds_draw,
        odds_away_win,
        odds_1X,
        odds_X2,
        odds_12,
        under_odds,
        over_odds,
    ]

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)

    skipped = 0
    for item in data:
        parsed = parse_text(item["text"])
        if parsed:
            parsed.append(item.get("score", ""))
            writer.writerow(parsed)
        else:
            skipped += 1

print(f"✅ Clean CSV created: {csv_file}")
print(f"⚠️ Skipped {skipped} entries due to parsing errors.")

import json
from pathlib import Path


LEADERBOARD_PATH = Path("leaderboard.json")


def load_leaderboard():
    if not LEADERBOARD_PATH.exists():
        return []

    with open(LEADERBOARD_PATH, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def save_score(username, score, level):
    if not username:
        username = "guest"

    leaderboard = load_leaderboard()

    leaderboard.append({
        "username": username,
        "score": score,
        "level": level
    })

    leaderboard.sort(key=lambda item: item["score"], reverse=True)
    leaderboard = leaderboard[:10]

    with open(LEADERBOARD_PATH, "w") as file:
        json.dump(leaderboard, file, indent=4)


def get_top_scores():
    return load_leaderboard()
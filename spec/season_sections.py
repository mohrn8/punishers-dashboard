"""
Season-cycle data helpers for The Punishers dashboard.

Feeds: injury_radar, trade_radar, trend_tracker, lineup_lock
Drop this alongside whatever script already writes pre_draft / camp_watch —
same league, same data.json, just picks up once Week 1 starts.

League: 1325388108564291584 (12-team, full PPR, 0.1/rush attempt, no DEF)
My roster_id: 3

-------------------------------------------------------------------------
NOTE (2026-08-30): This module is retained as an ENDPOINT CONTRACT, not as a
runnable script. The Claude sandbox proxy returns 403 for api.sleeper.app, so
these requests calls fail there; the scheduled tasks hit the same URLs through
the web_fetch tool instead. Each function below documents which endpoint feeds
which dashboard section.

Not covered by the original spec, and worth knowing: resolving Sleeper player
IDs to names via /v1/players/nfl does NOT work — the response is ~5MB and gets
truncated. Use /v1/draft/{draft_id}/picks instead, where each pick's `metadata`
carries first_name, last_name, position, and team for all 192 drafted players.
-------------------------------------------------------------------------
"""

import requests
from datetime import datetime, timezone

LEAGUE_ID = "1325388108564291584"
MY_ROSTER_ID = 3
DRAFT_ID = "1325388108576849920"   # for player-ID -> name resolution
BASE = "https://api.sleeper.app/v1"


def get_my_roster():
    """My current roster: starters, bench, taxi/IR."""
    rosters = requests.get(f"{BASE}/league/{LEAGUE_ID}/rosters").json()
    return next(r for r in rosters if r["roster_id"] == MY_ROSTER_ID)


def get_all_rosters_with_owners():
    """All 12 rosters mapped to owner display names — needed for trade_radar."""
    rosters = requests.get(f"{BASE}/league/{LEAGUE_ID}/rosters").json()
    users = requests.get(f"{BASE}/league/{LEAGUE_ID}/users").json()
    user_map = {u["user_id"]: u.get("display_name", u["user_id"]) for u in users}
    for r in rosters:
        r["owner_name"] = user_map.get(r.get("owner_id"), "unknown")
    return rosters


def get_week_transactions(week: int):
    """Trades, waiver claims, free-agent moves for one week — trade_radar source."""
    return requests.get(f"{BASE}/league/{LEAGUE_ID}/transactions/{week}").json()


def get_trending_adds(hours: int = 48, limit: int = 40):
    """League-wide trending adds across Sleeper — trend_tracker source."""
    return requests.get(
        f"{BASE}/players/nfl/trending/add",
        params={"lookback_hours": hours, "limit": limit},
    ).json()


def get_week_matchups(week: int):
    """This week's matchups/starters for everyone — lineup_lock source."""
    return requests.get(f"{BASE}/league/{LEAGUE_ID}/matchups/{week}").json()


def current_nfl_week():
    """Sleeper's own notion of the current week — avoids hardcoding it."""
    state = requests.get(f"{BASE}/state/nfl").json()
    return state.get("week", 1)


def player_name_map():
    """
    ID -> {name, position, team} for every drafted player.
    Use this INSTEAD of /v1/players/nfl, which is ~5MB and truncates.
    """
    picks = requests.get(f"{BASE}/draft/{DRAFT_ID}/picks").json()
    out = {}
    for p in picks:
        m = p.get("metadata") or {}
        out[p.get("player_id")] = {
            "name": f"{m.get('first_name', '')} {m.get('last_name', '')}".strip(),
            "position": m.get("position"),
            "team": m.get("team"),
        }
    return out


if __name__ == "__main__":
    wk = current_nfl_week()
    print(f"Current NFL week per Sleeper: {wk}")
    mine = get_my_roster()
    print(f"My roster ({len(mine.get('players') or [])} players): {mine.get('players')}")

# Season Sections — Build Spec

For the Claude Code task that already writes `pre_draft` / `draft_strategy` /
`camp_watch` / `colts_watch` into `data.json`. Extend it to also run weekly
once Week 1 starts, writing these four currently-empty sections in the same
style and schema.

## Output schema (matches existing sections exactly)

```json
"section_key": {
  "updated": "2026-09-09T14:00:00Z",
  "items": [
    { "text": "<b>Player Name</b> did the thing — why it matters for THIS league (Source, date)", "flag": true }
  ]
}
```

- `flag: true` = actionable/urgent, renders with the red left border
- `flag: false` = context, no action needed yet
- Bold player/team names with `<b>`, inline `<code>` for setting names
- Every claim needs a source + date in parens, same as `pre_draft` does
- 5-8 items per section is the right density (matches existing sections)

## Cadence

Run once per week, Tue/Wed morning (after MNF, before waiver processing) —
timed so `trade_radar` and `trend_tracker` reflect the prior week's activity
and `lineup_lock` has a full week of runway before Sunday.

## Section-by-section

### `lineup_lock`
Pull `get_my_roster()` + `get_week_matchups(current_week)`. For each start/sit
question on my roster: matchup quality, recent target/touch share, and —
specific to this league — remember rush attempts alone are worth 0.1 each,
so a volume back with a bad matchup can still outscore an efficient one.
Flag any close calls or players I might be sleeping on.

### `trade_radar`
Pull `get_week_transactions()` for the last 1-2 weeks across all 12 rosters
via `get_all_rosters_with_owners()`. Surface trades that reveal a team
selling/buying at a position — that's a signal for who to call about a deal,
and who might overpay for what I don't need.

### `trend_tracker`
Pull `get_trending_adds()`, cross-reference against `get_my_roster()`'s bench
and my likely waiver budget. Only surface adds relevant to my actual roster
gaps — not the full trending list. Note snap-share/target-share trends over
raw hype where possible.

### `injury_radar`
Same pattern as `camp_watch`, continued into the season — status changes for
players on my roster or rostered by direct opponents (upcoming matchups),
prioritized over league-wide injury news.

## One rule carried over from `draft_strategy`

No DEF is ever draftable or streamable in this league — don't suggest DEF
streaming as a `lineup_lock` idea. K is the only non-DEF flex-adjacent
consideration, and even that's usually a non-issue after the roster's set.

---

## Implementation notes (added during integration, 2026-08-30)

**Folded into the four existing scheduled tasks rather than built as a new
weekly task.** Each of these sections already had an owner, and two tasks
writing the same JSON key means the later run silently overwrites the earlier
one. Cadences kept as-is because they beat a single weekly run:

| Section | Task | Cadence | Why not weekly Tue/Wed |
|---|---|---|---|
| `injury_radar` | `punishers-injury-monitor` | Daily 7:00 AM | Injuries break on Wed practice reports and Fri designations |
| `trade_radar` | `punishers-league-intel` | Wed 8:00 AM | Already matches the spec's Tue/Wed window |
| `trend_tracker` | `punishers-efficiency-trends` | Mon 8:00 AM | Must land before Tuesday waiver processing |
| `lineup_lock` | `punishers-lineup-lock` | Sun 11:30 AM | Official inactives drop 90 min before kickoff |

**`season_sections.py` does not execute in this environment.** The sandbox
proxy returns 403 for `api.sleeper.app`; only the `web_fetch` tool reaches it.
The file is retained as an endpoint contract — it documents exactly which
Sleeper endpoint feeds which section, and the tasks call those same endpoints
via `web_fetch`.

**Player-ID resolution** is not covered by the spec and is a real trap: the
full player map at `/v1/players/nfl` is ~5MB and gets truncated. The tasks
build an ID→name map from `/v1/draft/{draft_id}/picks` instead, whose per-pick
`metadata` carries `first_name`, `last_name`, `position`, and `team`.

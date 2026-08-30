# Best-Available Board — Addendum to SEASON_SECTIONS_SPEC.md

Adds live "who's still good for THIS league" to the draft-day tab. Two parts:
a one-time data addition (your existing task) and a client-side panel (below).

## Part 1 — `big_board` in data.json

Have the same task that writes `pre_draft` also write a top-level `big_board`
array, refreshed the morning of Sept 5 (ADP moves fast in the last 48 hours —
this should NOT be the same static run as the rest of pre_draft).

```json
"big_board": [
  { "name": "Bucky Irving", "pos": "RB", "team": "TB", "tier": 2,
    "note": "Lead-back volume in a 0.1/att league — priced like RB20, plays like a top-12" },
  { "name": "Stefon Diggs", "pos": "WR", "team": "WAS", "tier": 4,
    "note": "Market hasn't repriced the role yet" }
]
```

- ~150-200 players, ranked/tiered for THIS league's scoring specifically —
  not generic ADP. Same adjustments already used in `pre_draft`/`draft_strategy`:
  rush attempts worth 0.1, no DEF drafted (board plays ~14 picks deeper than
  public ADP), QB devalued (wait to 83-110), PPR.
- `tier` groups players of similar value (tier 1 = top overall, etc.) — ties
  break better than forced 1-200 ranks when picks are close.
- `note` is optional, one line, only for players where the league-specific
  scoring meaningfully changes their value (most players don't need one).
- Name format must match Sleeper's pick metadata exactly (`first_name` +
  `last_name`) so the client-side matching in Part 2 works without a lookup.

## Part 2 — client-side panel (paste into index.html)

Drops into the existing `pollDraft()` flow in the `draft-day` live board.
Fetches `big_board` once, then on every 15s poll filters out anyone already
picked (matched by name against live picks) and shows the top remaining
player per position.

See `draft_board_bpa.js` for the exact code — it's written as a drop-in
addition to the existing `pollDraft()` function, not a replacement.

---

## Implementation notes (added during integration, 2026-08-30)

**Part 2 is wired into `index.html`.** All three edits from `draft_board_bpa.js`
were applied: `bigBoard` state declared alongside the other draft-board
variables, populated in `load()` from `data.json`, and `bestAvailableHTML(picks)`
spliced into the `pollDraft()` template after the "Most recent picks" section.
The panel is self-hiding — with an empty `big_board` it renders nothing, so it
sits dormant until the board is populated.

**Part 1 is assigned to `punishers-draft-prep`,** which already owns `pre_draft`
and `draft_strategy`. Per the spec it refreshes `big_board` separately from the
static sections, on the day of the draft.

**Name-matching is the fragile part.** Matching is done on lowercased
`first_name + ' ' + last_name` from Sleeper's pick metadata. Suffixes are the
known failure mode — Sleeper carries "Anthony Richardson Sr." and
"James Cook III", so a board entry reading "Anthony Richardson" will never match
the pick and the player will show as available after he is gone. The task is
instructed to use Sleeper's exact string, and the draft picks endpoint is the
authoritative source for it.

**Tiers, not ranks**, per the spec — with picks at 11/14 and 35/38 arriving in
quick succession, tier boundaries answer "is there a meaningful drop if I wait?"
better than an ordinal list.

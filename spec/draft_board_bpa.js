/* ===== BEST AVAILABLE — drop-in addition to the existing draft-day board =====
   Add this to index.html's <script> block, near the other draft-board code.
   Requires: BEST_AVAILABLE_ADDENDUM.md's "big_board" array in data.json.

   Wiring (3 small edits to existing code):
   1. Add `let bigBoard = [];` near the top with the other draft-board state.
   2. In `load()`, after `currentData = data;`, add: `bigBoard = data.big_board || [];`
   3. Inside `pollDraft()`, right after `if (!Array.isArray(picks)) picks = [];`,
      insert the block below, then splice `bestAvailableHTML(picks)` into the
      `box.innerHTML` template (right after the "Most recent picks" section,
      before the closing backtick).
*/

function draftedNameSet(picks) {
  const s = new Set();
  picks.forEach(p => {
    const m = p.metadata || {};
    const name = `${m.first_name || ''} ${m.last_name || ''}`.trim().toLowerCase();
    if (name) s.add(name);
  });
  return s;
}

function bestAvailableHTML(picks) {
  if (!bigBoard.length) return '';
  const drafted = draftedNameSet(picks);
  const available = bigBoard.filter(p => !drafted.has(p.name.trim().toLowerCase()));

  const positions = ['QB', 'RB', 'WR', 'TE'];
  const topByPos = positions.map(pos => {
    const best = available.filter(p => p.pos === pos).slice(0, 3);
    return { pos, best };
  });

  return `
    <div class="live-section">
      <h4>Best available — adjusted for this league's scoring</h4>
      <div class="panel-grid single-col" style="gap:10px;">
        ${topByPos.map(({ pos, best }) => `
          <div>
            <div class="run" style="display:inline-block;margin-bottom:6px;">${pos}</div>
            <ul class="picks">
              ${best.length ? best.map(p => `
                <li class="pick">
                  <span class="pick-name">${p.name}</span>
                  <span class="pick-pos">T${p.tier} &middot; ${p.team}</span>
                  ${p.note ? `<span class="pick-team" style="text-align:left;flex:1;">${p.note}</span>` : ''}
                </li>
              `).join('') : '<li class="empty">Tier exhausted</li>'}
            </ul>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

/* ===== END BEST AVAILABLE ===== */

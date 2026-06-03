---
name: super-start
description: Use when starting a new full cowork session — arms all channels, reads all inboxes, sets goal, activates superpowers and team tools. Replaces session-bootstrap-vnext.
---

# super-start — Kompletní cowork bootstrap

Spouštěj při: novém okně, po /clear, po /compact, po restartu, z launcheru.

## FÁZE A — Kanály (vždy, jako první)

**A1 — i-can-hear-u** (aggregator daemon + Monitor watcher — POVINNÉ)
```bash
python L:/LG13/app/agent/listen_aggregator.py --instance <inst> --status
# daemon_running: false → spusť s run_in_background: true
```
Pak arm Monitor:
```bash
tail -n 0 -F L:/LG13/runtime/ops/wake_signal/<inst>.jsonl 2>&1 | grep --line-buffered -E '"source"'
```

**A2 — load-from-store** (načti předchozí plán z MySQL)
```bash
python -c "import sys; sys.path.insert(0,'L:/GitHub/lg13-coder/agent/skills'); from db_query import db; ..."
```
→ `/lg13-skills:load-from-store`

**A3 — deep-read** (nové kanály od cursoru)
```bash
python L:/GitHub/lg13-coder/agent/skills/deep_read.py --instance <inst> --limit 200
```

**A4 — issue-sync** (GitHub delta digest)
```bash
python L:/LG13/app/agent/skills/issue_sync.py --repo LG13-21/legal-ship-2026
python L:/LG13/app/agent/skills/issue_read.py --instance <inst> --format markdown --update-anchor
```

**A5 — Queue check + claim**
```bash
python L:/LG13/app/agent/instance_queue.py --check --name <inst>
python L:/LG13/app/agent/instance_queue.py --claim-next --name <inst>
```

---

## FÁZE B — Self-awareness

**B1 — self-goal** (napiš SESSION GOAL do STAV_NOW.md)
```
## SESSION GOAL — <inst> <TS>
<1-3 věty: co chceš dodat v této session>
```

**B2 — edge-check** (token zone)
```bash
python L:/LG13/app/agent/skills/edge_calc.py --ctx-now <N>
```

**B3 — token-budget** (weekly/session stav)
```bash
python L:/LG13/app/agent/skills/claude_usage_read.py --json
```

---

## FÁZE C — Team coordination

**C1 — ping-pong heartbeat** (i bez příchozího pingu)
- Subject: `[HEARTBEAT] <inst> HH:MM — <co dělám>`
- Pošli stratu + cíli

**C2 — Arm ping-pong Monitor** (persistent)
```bash
# watch for *_to_<inst>_*.json changes every 15s
```

**C3 — avengers-meeting** (pokud tým mode)
→ `/lg13-skills:avengers-meeting` — spusť jen pokud Tom aktivoval tým

---

## FÁZE D — Superpowers (on-demand, podle tasku)

| Task | Skill |
|------|-------|
| Nová funkce / nápad | `/superpowers:brainstorming` |
| Mám spec, plánuji | `/superpowers:writing-plans` |
| Mám plán, implementuji | `/superpowers:executing-plans` |
| Bug / neočekávané chování | `/superpowers:systematic-debugging` |
| PR review | `/superpowers:requesting-code-review` |
| Commit + merge | `/superpowers:finishing-a-development-branch` |
| Právní dokumenty | `/lg13-skills:diamond-sentry` |

---

## FÁZE E — Datové nástroje (on-demand)

| Nástroj | Skill / příkaz |
|---------|---------------|
| MySQL dotaz | `/lg13-skills:mysql` |
| Supabase cloud DB | `/superpowers` + mcp__plugin_supabase |
| Plan do GitHub issue | `/lg13-skills:plan-to-git` |
| FTP operace | `/lg13-skills:ftp` |
| Skill dokumentace | `/lg13-skills:skills-list` / `skills-manual` |
| Email | `/lg13-skills:email-read` |

---

## FÁZE F — Persistence (každých ~15 min nebo při důležité změně)

```bash
# Save + heartbeat
/lg13-skills:save-min
# obsahuje: queue --done + STAV append + save_checkpoint
```

Pak pong stratu: `[HEARTBEAT] <inst> <HH:MM> — <stav>`

---

## Rychlý start (minimal — pokud se spěchá)

1. A1 (i-can-hear-u) — vždy
2. A3 (deep-read) — vždy
3. B1 (self-goal) — vždy
4. C1 (heartbeat pong stratu) — vždy
5. → work

---

## Red Flags — STOP pokud:

- Spustíš práci bez A1 → instance je hluchá
- Nenapíšeš B1 self-goal → Tom neví co děláš
- Nepošleš C1 heartbeat → město spí
- Ignoruješ deep-read výsledky → přijdeš o direktivy

---

## Related

- `session-bootstrap-vnext` → deprecated alias (viz níže)
- `L:/GitHub/lg13-coder/agent/listen_aggregator.py` — aggregator daemon
- `L:/LG13/runtime/ops/ping_pong/` — ping-pong protokol
- `L:/LG13/runtime/ops/wake_signal/` — wake signály
- Issue #90: Skills Registry
- Issue #91: work-mode (self-paced heartbeat loop)

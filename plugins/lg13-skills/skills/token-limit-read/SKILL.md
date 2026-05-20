---
name: token-limit-read
description: "Read current Claude usage (session % / week % / plan tier) z TM script ingested data. Token-free read, žádný API call."
user-invocable: true
---

# Token-Limit-Read — Live usage awareness

> **⚠️ KNOWN BUG (2026-05-12, Lik R197):** JSON pole `weekly_all` / `weekly_sonnet` / `weekly_design` jsou **PROHOZENÁ** vs. UI claude.ai/settings/usage. Konkrétní mapping inverze ověřena Tom screenshotem: UI All 76% ↔ JSON 11; UI Sonnet 11% ↔ JSON 80; UI Design 80% ↔ JSON 27. **Před major budget decisions (>80% threshold, P0 spawn, /compact gate) VŽDY ověř UI screenshot.** session_pct se zdá OK (close-ish), ale weekly_* nedůvěřuj dokud coder #3148 nefixne `lg13_claude_usage.user.js` DOM selector mapping. Memory: `bug_tm_usage_field_mapping_inverted.md`.

## PURPOSE

Přečíst aktuální Claude usage state (session pct, week pct, plan tier, last-sync) bez API call. Data ingestnutá Tampermonkey skriptem `lg13_claude_usage.user.js`.

---

## EXECUTION

### Step 0: Refresh browser tab (cowork instances s Chrome MCP)

TM userscript POSTuje data jen když claude.ai/settings/usage je live + page-render trigger. Bez refreshe = stale snapshot z minulé session.

**Instance s `mcp__claude-in-chrome__*` tools** (main, strat, coder, web, t005, atd. — cowork) MUSÍ before reading:

1. `mcp__claude-in-chrome__tabs_context_mcp` → find tab URL contains `claude.ai/settings/usage`
2. Pokud tab existuje → `mcp__claude-in-chrome__navigate` na stejnou URL (force reload) NEBO klávesovou zkratku F5 přes shortcuts_execute
3. Pokud tab neexistuje → `mcp__claude-in-chrome__tabs_create_mcp(url='https://claude.ai/settings/usage')`
4. Wait ~3-5s (TM script potřebuje render + POST na pl_server)

**CMD instance** (t001/t002/t005/media) bez Chrome MCP → skip Step 0 → read může být stale → warn user pokud `ingested_at` >5min stale.

### Step 1: Read state

Single-shot:

```
python L:/LG13/app/agent/skills/claude_usage_read.py
```

JSON mode (auto-parse):

```
python L:/LG13/app/agent/skills/claude_usage_read.py --json
```

Single field:

```
python L:/LG13/app/agent/skills/claude_usage_read.py --field session_pct
```

Watch mode:

```
python L:/LG13/app/agent/skills/claude_usage_read.py --watch 30
```

---

## CO SE STANE

- Step 0: refresh / open claude.ai/settings/usage v Chrome → TM `lg13_claude_usage.user.js` POSTne fresh snapshot na pl_server
- Step 1: read JSON snapshot z `/pl/usage/current`
- vrátí: session_pct, week_pct, plan_tier, last_sync, raw values
- pokud diff `now - ingested_at` >5min → warn (refresh nefungoval / TM script chybí v Chrome)

---

## OUTPUT

Default human-readable. --json pro auto-parse. --field pro single value.

---

## RULES

- pre-req: TM skript `lg13_claude_usage.user.js` nainstalovaný **v Chrome** (raw URL `https://raw.githubusercontent.com/LG13-21/lg13-tampermonkey/main/lg13_claude_usage.user.js`)
- cowork instance VŽDY dělá Step 0 (browser refresh) před Step 1 read
- pokud `ingested_at` >5min stale → TM offline / Chrome zavřený / script nenainstalovaný v Chrome — warn user
- token-free pro main read (Step 1); Step 0 stojí ~1-2 chrome MCP calls
- Firefox-only install NESTAČÍ — Claude Code instance používá Chrome MCP (Firefox MCP neexistuje)

---

## USE CASES

- před start velkého tasku → check session_pct (jsi v okně?)
- před /clear → confirm session_pct >80% (justified reset?)
- watch mode pro long-running operations

---

## FINAL

→ instance má awareness pro budget decisions

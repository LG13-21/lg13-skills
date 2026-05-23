---
name: issue-sync
description: This skill should be used when the user asks to "sync issues", "read issues", "issue digest", "co je nového na issues", "issue-sync", or wants a delta digest of GitHub issues + comments since last read with optional keyword filtering. Maintains local SQLite cache of all issues in `LG13-21/legal-ship-2026` and returns per-instance anchored JSON/markdown.
version: 0.1.0
---

# Issue-Sync — GitHub issues → SQLite → anchor/keyword JSON

## PURPOSE

Místo opakovaného `gh issue view 14 --comments` (drahé, jen jedna issue, propásne #34/#40/#41/#42/#43/#19) sync všech issues + comments do lokální SQLite a čti delta od posledního volání s keyword filtrem.

---

## PARAMETRY

| Parametr | Default | Popis |
|----------|---------|-------|
| `repo` | `LG13-21/legal-ship-2026` | Cílový GitHub repo |
| `instance` | auto-detect (legal/strat/coder) | Per-instance anchor + keyword preset |
| `anchor` | DB last_read_at | ISO UTC timestamp — od kdy číst |
| `keywords` | preset dle instance | Comma-list klíčových slov (substring, OR) |
| `limit` | 50 | Max počet issues v outputu |
| `format` | `json` | `json` nebo `markdown` |
| `full` | false | Plný re-sync místo incremental |
| `skip-sync` | false | Jen čti DB, nesyncuj |
| `force-read` | false | **FORCE MUST READ** — dump ALL open issues + ALL comments, bypass anchor+keywords |

---

## FORCE-READ MODE (Tom directive 2026-05-23)

Default delta+keyword mód mine drift („agents read sampled comments, miss critical directives like #46"). Force-read = mandatorní úplné čtení před tím než instance prohlásí readiness.

```bash
# All open issues, all comments, full bodies — JSON
python L:/LG13/app/agent/skills/issue_read.py --force-read --format json

# Markdown render
python L:/LG13/app/agent/skills/issue_read.py --force-read --format markdown
```

**Kdy použít force-read:**
- Před začátkem session na hot repo (legal-ship-2026 active filing)
- Po compactu, ztracený context
- Před tím než instance prohlásí readiness/LOCK gate transition
- Při escalation („nechtes issues" failure mode)

Force-read NEAKTUALIZUJE anchor (peek mode) — následný incremental `--update-anchor` read funguje normálně.

---

## EXECUTION

### 1. Sync (incremental delta z GitHub → SQLite)

```bash
python L:/LG13/app/agent/skills/issue_sync.py --repo LG13-21/legal-ship-2026
```

- První spuštění: full pull
- Další: jen issues s `updated_at > last_sync_at` (lacino — 1× gh api volání pro index)
- DB: `L:/LG13/runtime/state/issues_cache.db`

### 2. Read (filtr + JSON)

```bash
python L:/LG13/app/agent/skills/issue_read.py \
    --instance legal \
    --keywords "F19,AS,asistovany_styk,STOP ORDER,LOCK" \
    --format markdown \
    --update-anchor
```

`--update-anchor` posune `instance_anchors.legal.last_read_at` na NOW — další volání pak vrací jen co přibylo.

### 3. Default flow `/issue-sync`

1. Spusť sync
2. Spusť read s auto-detected instancí + presetem
3. Zobraz markdown (pro lidskou orientaci) nebo JSON (pro další zpracování)

---

## KEYWORD PRESETY

Per instance (override v `~/.lg13/issue_keywords_{instance}.json`):

- **legal**: `F19, AS, asistovany_styk, asistovaný styk, STOP ORDER, LOCK, filing, podání`
- **strat**: `orchestration, wave, ship, blocker, priority`
- **coder**: `corpus, build, FTP, pipeline, script`

Bez `--keywords` použije preset; explicitní `--keywords ""` = bez filtru.

---

## OUTPUT (JSON)

```json
{
  "instance": "legal",
  "anchor": "2026-05-22T20:00:00Z",
  "keywords": ["F19", "AS"],
  "total_new": 7,
  "issues": [
    {
      "number": 42,
      "title": "FAST-LANE AS-response structure",
      "state": "open",
      "url": "https://github.com/.../issues/42",
      "labels": ["legal", "fast-lane"],
      "new_comments": [
        {"id": ..., "author": "tom", "created_at": "...", "body": "..."}
      ]
    }
  ],
  "anchor_advanced_to": "2026-05-22T21:15:33Z"
}
```

---

## RULES

- **Read-only skill** — žádné write operations (comments/close)
- **`gh` CLI musí být auth'd** (`gh auth status`)
- **Anchor je per-instance** — legal/strat/coder mají vlastní timestamp
- **Substring match** — case-insensitive, OR napříč keywords; akceptuje false positives (např. „AS" v „class")
- **`--update-anchor` je opt-in flag** — bez něj anchor zůstává (peek mode); s ním se posune na NOW po čtení. V default `/issue-sync` flow předávat vždy `--update-anchor`

---

## RELATED

- `L:/LG13/app/agent/skills/issue_sync.py` — sync engine
- `L:/LG13/app/agent/skills/issue_read.py` — filter + output
- DB: `L:/LG13/runtime/state/issues_cache.db`
- Skill `ping-pong` — issue #14 byl primary, nyní doplněn celým issue prostorem
- Plan: `C:/Users/tom/.claude/plans/fancy-crafting-star.md`

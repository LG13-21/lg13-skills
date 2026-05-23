---
name: thread-harvest
description: This skill should be used when the user says "přečti vlákna", "co leží nevykonáno", "projdi exporty", "harvest instrukce", "co jsem říkal v jarvis", "thread-harvest", or when starting a session and suspecting unread directives in ChatGPT exports, issues, atoms or JSONs. Systematically reads all knowledge sources and extracts unexecuted directives, tasks, and instructions per instance.
version: 1.0.0
---

# thread-harvest — Systematické čtení vláken + extrakce nevykonaných instrukcí

## PURPOSE

Tom dává instrukce na mnoha místech — ChatGPT exporty, GitHub issues, atoms, LG13_META JSONs.
Instance to nečtou systematicky → instrukce leží nevykonané.

Tento skill to řeší: projde všechny zdroje, extrahuje nevykonané tasky/direktivy, rozdělí je per-instance.

---

## SPUŠTĚNÍ

```
/thread-harvest
/thread-harvest --source chatgpt        # jen ChatGPT exporty
/thread-harvest --source issues         # jen GitHub issues
/thread-harvest --source all            # vše (default)
/thread-harvest --since 2026-05-22      # jen od data
/thread-harvest --instance coder        # filtr jen pro coder tasky
```

---

## ZDROJE (v pořadí priority)

### 1. ChatGPT exporty — `L:\GitHub\legal-ship-2026\ChatGPT_export\*.json`

Nejbohatší zdroj nevykonaných instrukcí.

```python
import json, glob, os
from pathlib import Path

EXPORT_DIR = Path("L:/GitHub/legal-ship-2026/ChatGPT_export")
STATE_FILE = Path("L:/LG13/runtime/state/thread_harvest_state.json")

# Načti last-read timestamps
state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}

# Jen nové/změněné soubory
for fpath in sorted(EXPORT_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
    last = state.get(str(fpath), 0)
    if os.path.getmtime(fpath) <= last:
        continue   # nezměněno od minulého harvest
    
    data = json.load(open(fpath, encoding="utf-8"))
    extract_directives_from_export(data, source=fpath.name)
```

**Co hledat v exportech:**

```python
DIRECTIVE_PATTERNS = [
    # Explicitní tasky pro instance
    r"(udělej|vytvoř|implementuj|zkontroluj|oprav|nastav|přidej)\s+.{10,200}",
    r"(coder|legal|strat)\s*[:-]\s*.{10,200}",
    r"TODO[:\s].{10,200}",
    r"skill\s+(pro|na|který).{10,200}",
    # LG13_META JSONy — strukturované tasky
    r'"action"\s*:\s*"([^"]+)"',
    r'"fu"\s*:\s*"([^"]+)"',   # follow-up field
    r'"to"\s*:\s*\[([^\]]+)\]', # target instances
]
```

**LG13_META JSONy** (v každém ChatGPT exportu) obsahují:
- `"action"` — co bylo uděláno
- `"fu"` — follow-up (nevykonaný task)
- `"to"` — cílová instance
- `"st"` — status (`created`, `pending`, `done`)

```python
# Hledej LG13_META bloky
import re
meta_blocks = re.findall(r'\{[^{}]*"LG13_META"[^{}]*\{[^}]+\}[^{}]*\}', text, re.DOTALL)
for block in meta_blocks:
    meta = json.loads(block).get("LG13_META", {})
    if meta.get("st") not in ("done", "resolved", "closed"):
        yield DirectiveItem(
            source=fpath.name,
            action=meta.get("fu") or meta.get("action"),
            target=meta.get("to", ["any"]),
            priority=meta.get("li", "normal"),
            ts=meta.get("ts")
        )
```

---

### 2. GitHub Issues — `LG13-21/legal-ship-2026`

```bash
python L:/LG13/app/agent/skills/issue_read.py --force-read --format json
```

Z výstupu extrahuj:
- Issues s `awaiting-tom` labelem → Tom task
- Issues s `TODO`, `[ ]` checkboxy v body → nevykonaný task
- Komentáře od Toma s imperativními větami

```python
import re
TODO_PATTERN = re.compile(r'- \[ \] (.+)')
for issue in data["issues"]:
    todos = TODO_PATTERN.findall(issue["body"])
    for todo in todos:
        yield DirectiveItem(source=f"issue#{issue['number']}", action=todo,
                           target=classify_instance(todo), priority="normal")
    for comment in issue["comments"]:
        if comment["author"] == "LG13-21":  # Tom's account
            yield from extract_tom_directives(comment["body"], source=f"issue#{issue['number']}")
```

---

### 3. Atoms / JSONs — `L:\GitHub\legal-ship-2026\**\atoms*.json`

```python
ATOM_DIRS = [
    "L:/GitHub/legal-ship-2026/F19",
    "L:/GitHub/legal-ship-2026/DD",
    "L:/GitHub/legal-ship-2026/runtime",
]
for d in ATOM_DIRS:
    for fpath in Path(d).rglob("*.json"):
        data = json.load(open(fpath, encoding="utf-8"))
        # Hledej "pending", "todo", "required" fieldy
        extract_from_atom(data, source=str(fpath))
```

---

### 4. GDRV/IFTTT inbox — `L:\GitHub\G_drw\IFTTT\inbox\`

```python
INBOX = Path("L:/GitHub/G_drw/IFTTT/inbox")
for f in INBOX.glob("*.txt"):
    content = f.read_text(encoding="utf-8")
    if "[STATUS] OPEN" in content or "[STATUS] WAITING" in content:
        yield DirectiveItem(source=f"IFTTT:{f.name}", action=content[:300],
                           target=["coder"], priority="urgent" if "URGENT" in f.name else "normal")
```

---

## OUTPUT FORMAT

```
# THREAD HARVEST — 2026-05-23T22:00Z
Zdroje: 12 exportů, 25 issues, 3 atom JSONs, 1 IFTTT
Nových direktiv: 18 | Přiřazeno: coder=7, strat=4, legal=3, tom=4

---

## [CODER] — 7 nevykonaných direktiv

| # | Zdroj | Direktiva | Priorita |
|---|-------|-----------|----------|
| 1 | jarvis_2.3_(3).json | Implementovat skill pro thread digest | HIGH |
| 2 | issue#45 | [ ] Upgrade /analyze-vertical → atom diff | NORMAL |
| 3 | IFTTT:URGENT_... | LOCK2 visual check potřeba | URGENT |

## [STRAT] — 4 nevykonaných direktiv
...

## [TOM] — 4 položky čekají na Toma
...

## [ANY] — 3 obecné direktivy
...
```

---

## INSTANCE CLASSIFIER

```python
INSTANCE_KEYWORDS = {
    "coder":  ["coder", "implementuj", "kód", "script", "pipeline", "build", "deploy",
                "sqlite", "skill", "python", "fix bug", "commit"],
    "legal":  ["legal", "F19", "AS", "podání", "ISDS", "filing", "VDR", "PO", "PR",
                "soud", "vyjádření", "attachment"],
    "strat":  ["strat", "architect", "design", "decision", "governance", "wave",
                "orchestrat", "priority"],
    "tom":    ["tom musí", "awaiting-tom", "LOCK", "visual check", "potvrď", "schval",
                "rozhodnutí"],
}

def classify_instance(text: str) -> list[str]:
    text_lower = text.lower()
    matches = [inst for inst, kws in INSTANCE_KEYWORDS.items()
               if any(kw in text_lower for kw in kws)]
    return matches or ["any"]
```

---

## STATE (anti-duplicate)

Harvest si pamatuje co už bylo zpracováno:

```json
{
  "last_run": "2026-05-23T22:00:00Z",
  "files_seen": {
    "ChatGPT-JARVIS 2.3 Inicializace (1).json": 1716501600.0
  },
  "directives_dispatched": ["sha256_hash_1", "sha256_hash_2"]
}
```

State file: `L:/LG13/runtime/state/thread_harvest_state.json`

---

## DISPATCH (po harvestingu)

Po extrakci:

1. **Coder tasky** → přidat do ping-pong fronty nebo přímo zpracovat
2. **Strat tasky** → ping-pong pong stratu
3. **Legal tasky** → ping-pong legal instanci
4. **Tom tasky** → GDRV/IFTTT notification (skill `tom-notify`)
5. **ANY** → zalogovat do `L:/LG13/runtime/state/harvested_directives.jsonl`

```python
# Auto-dispatch
for item in directives:
    if "tom" in item.target:
        notify_tom_via_gdrv(item)
    elif "coder" in item.target:
        execute_or_queue(item)
    else:
        dispatch_via_pingpong(item)
```

---

## PRAVIDLA

- **Nečti soubory dvakrát** — state file zabrání re-harvest
- **Deduplikace** — SHA256 direktivy před dispatchem
- **Neposílej Tomovi víc než 3 GDRV notifications za harvest run**
- **Velké exporty** (>500KB) — jen LG13_META bloky + posledních 10 zpráv
- **Spouštěj na začátku každé session** (po force-read issues)

---

## KDY SPUSTIT

- Na začátku session (post force-read)
- Po přijetí nových ChatGPT exportů (listener event)
- Když Tom říká "co jsem říkal v jarvis" / "co leží nevykonáno"
- Periodicky každých ~4h (terminator loop)

---

## RELATED

- Skill `issue-sync` — GitHub issues sync + read
- Skill `tom-notify` — GDRV/IFTTT dispatch Tomovi
- Skill `ping-pong` — inter-instance dispatch
- `L:/LG13/app/agent/skills/issue_read.py` — force-read engine
- ChatGPT exporty: `L:/GitHub/legal-ship-2026/ChatGPT_export/*.json`

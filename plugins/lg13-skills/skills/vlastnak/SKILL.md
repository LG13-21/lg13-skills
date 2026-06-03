---
name: vlastnak
description: Use when an instance needs to define its own session goal — generates structured GOAL_PROMPT, saves to MySQL, copies to clipboard, displays in ASCII box. Alias for self-goal.
---

# vlastnak / self-goal

Vygeneruje vlastní session goal pro instanci. Uloží do MySQL, clipboard, ASCII box.

## EXECUTION

### Krok 1 — Promtuj si vlastní cíl

Zodpověz tyto otázky:
1. **MISE**: Co je tvůj hlavní úkol v této session? (1-2 věty)
2. **CÍLE**: Jaké konkrétní výstupy chceš dodat? (max 5 položek)
3. **BLOCKER**: Co tě blokuje nebo vyžaduje Tom GO? (nepovinné)
4. **DONE CRITERIA**: Jak poznáš, že session je hotová?

### Krok 2 — Sestavení GOAL_PROMPT

```python
import sys, json, time, subprocess
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

instance = 'coder'  # auto-detect z cwd
ts = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())

# --- vyplň interaktivně nebo jako literál ---
mise = "<MISE — co je hlavní úkol>"
goals = [
    ("P1", "<název>", "<soubor nebo N/A>", "<stav>", "<blocker nebo —>"),
]
done_criteria = ["<kritérium 1>", "<kritérium 2>"]

# --- compose ---
goals_table = "| # | Cíl | Výstup | Stav | Blocker |\n|---|-----|--------|------|---------|\n"
for g in goals:
    goals_table += f"| {g[0]} | {g[1]} | {g[2]} | {g[3]} | {g[4]} |\n"

done_list = "\n".join(f"- [ ] {c}" for c in done_criteria)

goal_text = f"""# {instance.upper()} INSTANCE — SESSION GOAL
# Generated: {ts}

## MISE
{mise}

## CÍLE

{goals_table}
## DONE CRITERIA

{done_list}

## BLOCKER
_(doplň nebo prázdné)_
"""
```

### Krok 3 — Uložení

```python
# A) Do STAV_NOW.md
stav = Path(f'L:/GitHub/lg13-coder/STAV_NOW.md')
with open(stav, 'a', encoding='utf-8') as f:
    f.write(f'\n## SESSION GOAL — {instance} {ts}\n\n{mise}\n\n')

# B) Do MySQL (instance_plans)
sys.path.insert(0, 'L:/GitHub/lg13-coder/agent/skills')
from db_query import db
db("INSERT INTO instance_plans (instance, plan_text, saved_at) VALUES (%s,%s,NOW()) "
   "ON DUPLICATE KEY UPDATE plan_text=%s, saved_at=NOW()",
   params=[instance, goal_text, goal_text])

# C) Do souboru (pro referenci)
out = Path(f'L:/GitHub/lg13-coder/GOAL_PROMPT_{instance.upper()}.md')
out.write_text(goal_text, encoding='utf-8')
print(f"[vlastnak] Uloženo: {out}")
```

### Krok 4 — Kopírovat do clipboardu

```powershell
Set-Clipboard -Value @"
<goal_text zde>
"@
Write-Output "[vlastnak] Zkopírováno do clipboardu."
```

Nebo přes Python:

```python
subprocess.run(['powershell', '-Command',
    f'Set-Clipboard -Value {json.dumps(goal_text)}'], check=False)
```

### Krok 5 — Zobrazit v ASCII boxu

```python
width = 60
border = '+' + '-' * (width + 2) + '+'
lines = [border, f'|  {instance.upper()} SESSION GOAL — {ts}  |', border]
for line in mise.splitlines():
    padded = line[:width].ljust(width)
    lines.append(f'| {padded} |')
lines.append(border)
print('\n'.join(lines))
```

## OUTPUT PŘÍKLAD

```
+--------------------------------------------------------------+
|  CODER SESSION GOAL — 2026-05-31 20:00 UTC  |
+--------------------------------------------------------------+
| Implementovat statusline right-side panel (brainstorming →  |
| design → writing-plans). Vedlejší: CGE potvrzeno.           |
+--------------------------------------------------------------+
```

## VARIANTA — Rychlá (jen STAV_NOW.md + ASCII box, bez MySQL)

Pokud chceš jen zapsat cíl bez persistování:

```
## SESSION GOAL — <inst> <TS>
<1-3 věty co chceš dodat>
```

## RELATED

- Vzorový GOAL_PROMPT: `L:/GitHub/legal-ship-2026/GOAL_PROMPT.md`
- MySQL save: `/lg13-skills:save-to-store`
- Super-start krok B1 (self-goal) → volá právě tuto funkci
- Alias: `self-goal` (stejný skill, jiné jméno)

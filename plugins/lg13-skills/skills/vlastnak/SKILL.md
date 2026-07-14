---
name: vlastnak
description: Use when an instance needs to write its own session goal prompt — a first-person startup prompt with clear done conditions, displayed on screen and copied to clipboard.
---

# vlastnak / self-goal

Napiš vlastní session prompt. Zobraz na screen. Dej do clipboardu.

**Výstup = text který by ses mohl paste-nout do nové session a okamžitě vědět co děláš.**

## EXECUTION

### Krok 1 — Napiš vlastní prompt (první osoba)

Formuluj jako by ses psal sám sobě. Odpověz:
- Kdo jsi a co je tvá role?
- Co konkrétně děláš v této session?
- Kdy je session hotová? (jasné, testovatelné podmínky)
- Co tě blokuje?

### Krok 2 — Sestavení a uložení do souboru

```python
import sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

instance = 'coder'  # auto-detect z cwd
ts = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())

# Piš vlastní prompt — první osoba, konkrétní
goal_prompt = f"""# {instance.upper()} SESSION GOAL -- {ts}

## KDO JSEM
<kdo jsi, tvá role v tomto projektu>

## CO DELAM TUTO SESSION
<co konkrétně děláš — 2-3 věty, ne obecnosti>

## DONE CONDITIONS
- [ ] <konkrétní, testovatelná podmínka 1>
- [ ] <konkrétní, testovatelná podmínka 2>
- [ ] <atd.>

## BLOCKER
- <co tě blokuje nebo vyžaduje GO>
"""

# Ulož do temp souboru pro clipboard
tmp = Path('C:/tmp/clipboard_goal.txt')
tmp.parent.mkdir(exist_ok=True)
tmp.write_text(goal_prompt, encoding='utf-8')
```

### Krok 3 — Zobraz na screen

```python
# Full text
print(goal_prompt)

# ASCII border
width = 66
border = '=' * (width + 4)
print(border)
for line in goal_prompt.splitlines():
    print(f'  {line[:width]}')
print(border)
```

### Krok 4 — Kopírovat do clipboardu (přes temp soubor)

```python
import subprocess
r = subprocess.run(
    ['powershell', '-Command', f'Get-Content -Path "{tmp}" -Raw | Set-Clipboard'],
    capture_output=True, text=True
)
if r.returncode == 0:
    print('[vlastnak] Zkopírováno do clipboardu.')
else:
    print(f'[vlastnak] Clipboard err: {r.stderr.strip()}')
```

**Proč temp soubor:** přímé předávání víceřádkového textu přes CLI args selže na quoting. Temp soubor je spolehlivý.

## DONE CONDITIONS formát

Každá podmínka musí být:
- **Konkrétní** — ne "feature hotová", ale "test_cmd_stack.py prochází"
- **Testovatelná** — dá se ověřit bez interpretace
- **Binary** — buď splněno, nebo ne

```
# ✅ Dobře
- [ ] chatgpt_ingest.py: CMD routing do coder_cmd_stack.jsonl funkční
- [ ] Test: Tom napíše [Ty:] → coder dostane atom do 30s

# ❌ Špatně  
- [ ] Zlepšit ingest
- [ ] Pracovat na reliability
```

## RELATED

- `/goal <text>` — nastav Stop hook na done conditions (paste z clipboardu)
- `/lg13-skills:save-to-store` — ulož stav do MySQL
- Super-start krok B1 (self-goal) → volá tuto funkci
- Alias: `self-goal`

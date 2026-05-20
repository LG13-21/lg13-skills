---
name: tmonkey-listen
description: "Persistentní příjem atomů — instance může normálně pracovat, každá nová zpráva ji probudí okamžitě. Jako mobil u hlavy: nic nedělej = spíš, ale zvonění uslyšíš vždy. Trigger: 'tmonkey listen', 'listen mode', 'arm listen', 'probudit při zprávě', 'neustálý příjem'."
user-invocable: true
---

# Tmonkey-Listen — Persistentní příjem, okamžité probuzení

## PURPOSE

Instance pracuje normálně (nebo čeká). Při každém novém atomu v jejím stacku → okamžité probuzení → zpracování → pokračuje v práci.

Žádné polling. Žádný sleep loop. Arm jednou, funguje dokud session žije.

---

## EXECUTION

### 1. Zjisti instanci

```python
import os
cwd = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
# T_Coder → coder, legal-ship-2026 → legal, T000_Strat → strat
```

### 2. Arm Monitor na tmonkey_arm.py

Spusť Monitor tool s tímto příkazem:

```
python L:/LG13/app/agent/tmonkey_arm.py --instance <inst> --interval 2 --timeout 86400
```

Monitor tool zachytí každý `[TMONKEY_NOTIFY]` nebo `[PINGPONG_NOTIFY]` řádek.

### 3. Na každý [TMONKEY_NOTIFY] event

```bash
python L:/LG13/app/agent/stack_reader.py --instance <inst> --new --mark-read --limit 50 --format markdown
```

Zpracuj nové atomy. Pak pokračuj v tom co jsi dělal.

### 4. Na každý [PINGPONG_NOTIFY] event

```bash
ls -t L:/LG13/runtime/ops/ping_pong/*_to_<inst>_*.json | head -3
```

Přečti nové zprávy, odpověz.

---

## CHOVÁNÍ

```
[instance pracuje na tasku A]
       ↓
[TMONKEY_NOTIFY přijde]
       ↓
[přeruš, spusť stack_reader, zpracuj atomy]
       ↓
[pokračuj v tasku A]
```

---

## RULES

- **Jedna instance, jeden arm** — nespouštěj arm vícekrát pro stejnou instanci
- **Monitor přežije práci** — je arm, nezastavuje se mezi eventy
- **Disarm při /clear nebo session end** — arm se zastaví sám, watchdog ho restartuje pro příště
- **Interval 2s** — optimum: rychlá reakce bez I/O flooduení
- **--timeout 86400** — arm žije 24h, watchdog ho restartuje

---

## RELATED

- `tmonkey-arm` skill — one-shot arm bez loop
- `tmonkey` skill — manuální jednorázový pickup
- `ping-pong` skill — stejný Monitor pattern pro ping-pong soubory
- `tmonkey_arm_watchdog.py` — drží arm procesy živé i mimo session

---

## FINAL

→ Monitor armed → instance pracuje nebo čeká → každá zpráva = okamžité probuzení → zpracování → pokračuj.

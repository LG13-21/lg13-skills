---
name: tmonkey-monitor
description: "Zapni zvonění — arm Monitor na tmonkey_arm.py, každý nový atom okamžitě probudí instanci. Normálně = zvonění vypnuto (tmonkey = manuální čtení). Monitor = zvonění zapnuto. Trigger: 'tmonkey monitor', 'zapni zvonění', 'arm monitor', 'chci být buzen', 'real-time atomy'."
user-invocable: true
---

# Tmonkey-Monitor — Zapni zvonění

## MODEL

Atomy jsou jako SMS. Každá instance dostává jen ty, co jí patří.

- **tmonkey** = přečti zprávy (manuálně, zvonění vypnuto)
- **tmonkey-monitor** = zapni zvonění → každý nový atom = okamžitá notifikace

---

## EXECUTION

### 1. Zjisti instanci

```python
import os
cwd = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
# T_Coder → coder | legal-ship-2026 → legal | T000_Strat → strat
```

### 2. Arm Monitor (zapni zvonění)

Spusť Monitor tool:

```
python L:/LG13/app/agent/tmonkey_arm.py --instance <inst> --interval 2 --timeout 86400
```

Monitor sleduje stdout. Na každý event:

**`[TMONKEY_NOTIFY]`** → nový atom → zpracuj okamžitě:
```bash
python L:/LG13/app/agent/stack_reader.py --instance <inst> --new --mark-read --limit 50 --format markdown
```

**`[PINGPONG_NOTIFY]`** → nová ping-pong zpráva → přečti:
```bash
ls -t L:/LG13/runtime/ops/ping_pong/*_to_<inst>_*.json | head -3
```

### 3. Timeout fallback (pokud žádná zpráva do 3 minut)

Pokud Monitor nepošle žádný event do **3 minut** od aktivace nebo posledního eventu:

```bash
# Manuální fallback check
python L:/LG13/app/agent/stack_reader.py --instance <inst> --new --mark-read --limit 50 --format markdown
```

**Vyhodnocení výsledku:**
- Atomy nalezeny → pipeline funguje, arm byl pomalý → zpracuj normálně → reset timer → pokračuj v monitorování
- Žádné atomy → OK, Tom ještě nepsal → reset timer → pokračuj v monitorování
- Atomy nalezeny ALE arm neposlal notify → **pipeline broken** → eskaluj a pokračuj:

```bash
python L:/LG13/app/agent/instance_queue.py --send --to strat --from-inst <inst> \
  --msg "PIPELINE ALERT: tmonkey_arm nenotifikoval ale stack má nové atomy — arm pravděpodobně mrtvý" \
  --priority P1

python L:/LG13/app/agent/instance_queue.py --send --to coder --from-inst <inst> \
  --msg "PIPELINE ALERT: tmonkey_arm dead — zkontroluj watchdog, restartuj arm" \
  --priority P1
```

Po eskalaci: reset timer, **pokračuj v monitorování** (neskončit).

### 4. Disarm (vypni zvonění)

```
TaskList → najdi running Monitor task → TaskStop <id>
```

---

## RULES

- Arm jen jednou per instance per session
- Timeout 3 min = od aktivace nebo posledního eventu — fallback check + případná eskalace
- Po eskalaci: pokračuj v monitorování, čekej na opravu
- **Auto-konec: 30–60 min od poslední zprávy** — pokud tak dlouho nic nepřišlo, konverzace skončila, Monitor disarm
- Eskaluj jen pokud stack má nové atomy ale arm nenotifikoval — ne při prázdném stacku
- tmonkey_arm_watchdog.py drží arm proces živý na pozadí — Monitor ho jen čte
- Při /clear nebo session end: Monitor se zastaví, watchdog restartuje arm pro příště

---

## RELATED

- `tmonkey` skill — manuální jednorázový pickup (zvonění vypnuto)
- `tmonkey-diag` skill — diagnostika atom flow health
- `tmonkey-arm` skill — implementation detail (arm samotný)

---

## FINAL

→ Monitor armed → zvonění zapnuto → každý atom = okamžité probuzení.
→ Po 3 min ticha: zkontroluj stack → pokud pipeline broken → eskaluj strat+coder → pokračuj v monitorování.
→ Po 30–60 min od poslední zprávy: konverzace skončila → Monitor disarm → konec.

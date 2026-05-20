---
name: team-launcher
description: >
  Spouští jednu nebo více LG13 instancí autonomně — headless nebo s oknem —
  bez Tomovy přítomnosti. Použij VŽDY když chceš: (a) spustit celý tým nebo
  konkrétní instance (coder, legal, strat, jcu…), (b) sequential start (strat
  první → broadcast → ostatní), (c) spustit instanci na pozadí bez okna, (d)
  spustit subagenta pro konkrétní task s custom promptem, (e) restartovat
  crashlou instanci s init promptem. Invoke when: "spusť tým", "launch coder",
  "start instances", "spusť strat a ostatní", "team start", "autonomous launch",
  "spusť subagenta", "start headless", "spusť na pozadí", "restart instance",
  "pusti legal jako subagenta", "spusť jcu s promptem", "sequential launch".
---

# Team Launcher Skill

## PURPOSE

Spouštět LG13 instance autonomně — bez Toma u klávesnice.

Každá instance dostane:
- `cowork_init.py` run před startem (tmonkey-arm + i14_watchdog + token check)
- Per-instance default prompt z `team_config.json`
- Headless spawn (t001/t002/t005/media = vždy hidden; ostatní = okno)

Config: `L:/LG13/runtime/ops/team_config.json` — edituj per-instance prompty tam.

---

## EXECUTION

### Spustit celý tým (parallel)
```bash
python L:/LG13/app/agent/team_launcher.py
```

### Sequential start (strat → wait → ostatní)
```bash
python L:/LG13/app/agent/team_launcher.py --seq
```

### Jen konkrétní instance
```bash
python L:/LG13/app/agent/team_launcher.py --instances coder,legal
python L:/LG13/app/agent/team_launcher.py --instances strat
```

### Subagent pro konkrétní úkol (přepíše default prompt)
```bash
python L:/LG13/app/agent/team_launcher.py --instances coder --prompt "zpracuj F19 atom batch; done ping strat"
```

### Dry-run (ukáže co by se stalo)
```bash
python L:/LG13/app/agent/team_launcher.py --dry-run
python L:/LG13/app/agent/team_launcher.py --instances coder --dry-run
```

### Bez cowork stacku (plain init min)
```bash
python L:/LG13/app/agent/team_launcher.py --no-cowork --instances t001
```

---

## TEAM_CONFIG.JSON

`L:/LG13/runtime/ops/team_config.json` — editovatelný config:

```json
{
  "default_instances": ["strat", "coder", "legal", ...],
  "cowork_issues": [14],
  "cowork_repo": "LG13-21/legal-ship-2026",
  "seq_wait_s": 15,
  "prompts": {
    "strat": "init min; spust cowork stack; broadcastuj INIT_COWORK...",
    "coder": "init min; spust cowork stack; zkontroluj queue...",
    "legal": "init min; spust cowork stack; zkontroluj F-cykl...",
    ...
  }
}
```

**Priority promptů:** `--prompt` CLI arg > `team_config.json` > built-in default.

---

## SEQUENTIAL MODE (--seq)

```
strat spustí → cowork_init --strat-broadcast → INIT_COWORK ping všem
  ↓ 15s čekání
coder/legal/web/... spustí → obdrží INIT_COWORK ping → armují stack
```

Strat tím ví kdo je online (každá instance pošle INIT_COWORK pong zpět).

---

## HEADLESS INSTANCES

Automaticky bez okna (CREATE_NO_WINDOW): `t001`, `t002`, `t005`, `media`, `openclaw`

Přidat okno pro headless: `+w` flag v `instance_launcher.py` (ne v team_launcher).

---

## COWORK STACK (co se armuje)

`cowork_init.py` spustí před každou Claude session:
1. `tmonkey-arm` — stack file watcher (30s poll, mtime change → wake)
2. `i14_watchdog` — GitHub issue monitor + ping-pong notifier (300s interval)
3. Token budget check — session_pct + weekly_all
4. INIT_COWORK ping → strat

---

## RELATED

- `L:/LG13/app/agent/team_launcher.py` — main script
- `L:/LG13/app/agent/cowork_init.py` — per-instance stack arm
- `L:/LG13/runtime/ops/team_config.json` — per-instance prompts
- `L:/LG13/app/agent/i14_watchdog.py` (alias → `L:/GitHub/lg13-coder/pipeline/i14_watchdog.py`)
- Skill `ping-pong` — pro ruční ping/pong výměny
- Skill `tmonkey-arm` — pro ruční arm watcheru

---

## NOTES

- Launcher se self-close po spawnu (neblokuje)
- Instance běží nezávisle po spuštění
- Výsledky přes ping-pong nebo issue #14 komentáře
- NIKDY: send ven, release bez 5 LOCKS — platí pro všechny spuštěné instance

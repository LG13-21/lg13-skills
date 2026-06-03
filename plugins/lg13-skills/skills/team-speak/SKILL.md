---
name: team-speak
description: Use when Tom types a message that should be forwarded to all active ping-pong instances simultaneously — broadcasts the message as if Tom wrote it to each instance's inbox.
---

# team-speak — Broadcast Tom's message to all instances

Pošle Tomovu zprávu do ping-pong inboxu všem aktivním instancem najednou.

## EXECUTION

```bash
python L:/GitHub/lg13-coder/agent/skills/team_speak.py \
  --msg "zprava od toma" \
  --targets legal,strat \
  --priority P1
```

Bez `--targets`: pošle všem kromě aktuální instance (auto-detect z CWD).

## USAGE

Tom napíše cokoliv, instance to zachytí a broadcastne:

```
Tom: "jdeme dnes na F30, soustredime se na FTP a archivaci"
/lg13-skills:team-speak
```

Coder vytvoří `tom_to_legal_<TS>.json` + `tom_to_strat_<TS>.json`.
Monitor watcher v každé instanci detekuje nový soubor a instanci vzbudí.

## PARAMETRY

| Parametr | Default | Popis |
|----------|---------|-------|
| `--msg` | (required) | Text zprávy |
| `--msg-file` | — | Cesta k souboru s textem |
| `--targets` | všichni kromě mě | Comma-list instancí |
| `--priority` | P1 | P0–P3 |

## FORMÁT ZPRÁVY

```json
{
  "from": "tom",
  "to": "legal",
  "type": "team-speak",
  "subject": "[TEAM-SPEAK] <preview>",
  "body": "<plny text>",
  "priority": "P1"
}
```

## RELATED

- Skill `ping-pong` — klasický inter-instance dialog
- `L:/GitHub/lg13-coder/agent/skills/team_speak.py` — implementace
- `L:/LG13/runtime/ops/ping_pong/` — adresář zpráv

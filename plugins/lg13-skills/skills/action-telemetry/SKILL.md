---
name: action-telemetry
description: "Log akci + report top actions + share přes ping_pong. Tom 2026-05-10 cost optimization pro coder/strat/legal."
user-invocable: true
---

# Action Telemetry — LG13 cost optimization tracking

## PURPOSE

Instance logují každou akci (Bash, Read, Agent, atd.) s odhadem tokenů do sdíleného JSONL souboru. Agregovaný report odkryje nejčastější a nejdražší akce. Cíl: identifikovat kandidáty na token-free náhradu (Glob/Grep/Python místo LLM).

---

## EXECUTION

Log jedné akce:

```bash
python L:/LG13/app/agent/skills/action_telemetry.py --log --action "Bash:gh_run_list" --instance coder --tokens 120
```

Report (last 24h, všechny instance):

```bash
python L:/LG13/app/agent/skills/action_telemetry.py --report --since 24h
```

Share přes ping_pong na strat:

```bash
python L:/LG13/app/agent/skills/action_telemetry.py --share-to strat --from-inst coder
```

---

## CO SE STANE

- `--log`: atomicky appenduje jeden JSON řádek do `actions.jsonl` (kategorie auto-derive z prefixu před `:`)
- `--report`: načte JSONL, filtruje dle `--since` a volitelně `--instance`, tiskne dvě markdown tabulky (top 10 count, top 10 tokens)
- `--share-to`: generuje ping_pong JSON soubor s top-10 statistikami za posledních 24h, atomic write (`.tmp` → replace)
- auto-create: parent adresáře se vytvoří pokud chybí

---

## OUTPUT

Datový soubor:
```
L:/LG13/runtime/telemetry/actions.jsonl
```

Schema řádku:
```json
{"ts": "2026-05-10T12:00:00Z", "instance": "coder", "action": "Read:CLAUDE.md", "category": "Read", "est_tokens": 80}
```

Report formát:
```
| action | count | total_tokens | avg_tokens |
```

Ping_pong výstup:
```
L:/LG13/runtime/ops/ping_pong/<from>_to_<to>_<YYYY-MM-DDTHHMMSSZ>.json
```

---

## RULES

- Žádné LLM API volání. Čistý Python stdlib.
- Append-only JSONL — nikdy nepřepisovat existující záznamy.
- Atomic write pro ping_pong (`.tmp` → `Path.replace()`).
- Minimální overhead: --log je < 5ms, žádné čtení dat při logování.
- UTF-8 všude.

---

## USE CASES

- Auto-logování přes wrapper: každá instance obalí klíčové tool cally do `--log` (Bash hook nebo manuální call po akci)
- Týdenní review: `--report --since 7d` odhalí systematické plýtvání tokeny
- Cross-instance srovnání: každá instance pošle `--share-to strat`, strat vidí kdo co volá nejčastěji

---

## FINAL

→ strat vidí telemetrii přes všechny instance, identifikuje optimization targets a zadává tasky na náhradu drahých akcí token-free alternativami.

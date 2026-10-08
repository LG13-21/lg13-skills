---
name: ctx-usage-report
description: "Use when a larger task has just finished (new F-document version, audit, render, commit) and its token cost must show up in Jarvis /jarvis/usage.php; also when a task used unusually many tokens. Triggers: 'ctx-usage-report', 'zapis spotrebu', 'spotreba po ukolu'"
status: experimental
user-invocable: true
---

# ctx-usage-report

## PURPOSE

Spáruje spotřebu tokenů s konkrétní dokončenou prací, aby v Jarvis (`usage.php`, sekce „Co instance udělaly") nebyla prázdná a bylo vidět, co kolik stálo. Vyčleněno z `low-food-slow-down`, který zůstává jen pro pacing a hodinovou kontrolu.

---

## EXECUTION

### 1. Snapshot spotřeby

```bash
python L:/GitHub/lg13-coder/agent/skills/usage_log.py snapshot --instance <inst>
```

### 2. Zapiš úkol

```bash
python L:/GitHub/lg13-coder/agent/skills/usage_log.py task --instance <inst> \
  --task-ref <např. F62.98> --summary "co se udělalo"
```

Pokud úkol stál nezvykle mnoho tokenů (zhruba >50 % nad mediánem posledních záznamů z `usage_log.py show --instance <inst> --limit 20`), připoj do `--summary` důvod: `| VYSOKA SPOTREBA (~N tok.): <důvod>`. Uveď ho i když šlo o chybu (plošné hledání na disku, opakované čtení velkých souborů, slepá větev). Nepřikrášluj.

### 3. Zkontroluj

```bash
python L:/GitHub/lg13-coder/agent/skills/usage_log.py show --instance <inst> --limit 5
```

---

## OUTPUT

- Řádek `task` v MySQL, viditelný na `luky.ai-domy.cz/jarvis/usage.php`.
- Jedna věta uživateli: kolik tokenů úkol stál (a proč, pokud vysoko).

---

## RULES

- Volat hned po dokončení, ne až v hodinové smyčce.
- Mimo frontu ručně; `instance_queue.py --done` zapisuje automaticky.
- Instance: coder, strat, legal, t002, jcu. Účtové % je sdílené, tokeny jsou per instance.
- Pacing a zóny řeší `low-food-slow-down`, ctx a compact `edge-check`.

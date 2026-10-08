---
name: edge-check
description: "Use when deciding whether to save or let compaction happen: context fills up, footer/statusline shows ctx usage, at the end of a task, or before any manual /compact. Single source of the ctx-usage policy (replaces compact-check)."
user-invocable: true
---

# Edge-Check — kdy uložit a nechat compactnout

## PROČ

Každá zpráva znovu načítá celý kontext z cache (u legal ≈ 160 k tokenů na zprávu). Menší kontext = levnější každá další zpráva. Proto se nečeká na 95 %.

## POLICY (Tom 2026-10-09)

Ctx % = **využito** (číslo ve footeru / `/statusline`). Autocompact je nastaven na ~25 % využití (`autoCompactWindow` v settings; legal: 250000).

| Využito | Zóna | Akce |
|---------|------|------|
| < 20 % | green | pracuj |
| 20–50 % | consider | na přirozeném konci úkolu (hotová verze, odeslaný ping, commit) `/lg13-skills:save-min`, pak nech autocompact, nebo požádej Toma o `/compact` |
| > 50 % | over | save-min HNED; autocompact už měl zasáhnout, upozorni Toma (špatné nastavení?) |

## CO INSTANCE SMÍ / NESMÍ

- **Nesmí:** spustit `/compact` sama (nástroj na to nemá). Nepředstírej, že ho spouštíš.
- **Smí a musí:** `save-min` (+ `/remember`) PŘED compactem; PreCompact hooky (`save_precompact.py`, git commit) udělají zbytek.
- Nikdy ruční `/compact` bez předchozího save-min.
- Po compactu: `/lg13-skills:load-from-store` + `.remember/remember.md`.

## VÝPOČET (volitelně, token-free)

```
python L:/LG13/app/agent/skills/edge_calc.py --ctx-now <tokeny> --window <okno> --threshold-pct 25
```
Bez toho stačí % z footeru; nepočítej z hlavy.

## HLÍDÁ TO

`low-food-slow-down` při každém hodinovém běhu (sekce „Hygiena ctx a compactu"). Nahrazuje `compact-check` (okno 200 k, smazáno 2026-10-09).

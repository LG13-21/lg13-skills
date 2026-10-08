---
name: autosave
description: "Use when context is filling up (edge-check says consider/over, 20+ % used) or Tom says 'autosave', 'ulož a compact', 'context se plní', 'dochází kontext' — state must be saved before compaction."
user-invocable: true
---

# Autosave — save + předání compactu

Save bez compactu kontext neuvolní, compact bez save ztratí stav. Instance umí jen první půlku; compact provede autocompact nebo Tom.

## POSTUP

1. **Zóna:** `/lg13-skills:edge-check` (využito 20–50 % = zvaž, > 50 % = hned).
2. **Dokonči** rozdělanou věc na přirozeném konci (hotová verze, odeslaný ping, commit). Neukládej uprostřed věty.
3. **Ulož:** `/lg13-skills:save-min` a `/remember:remember` (handoff do `.remember/remember.md`).
4. **Předej compact:**
   - autocompact je nastaven na ~25 % využití → nech ho zasáhnout;
   - jinak napiš Tomovi jednu větu: „Uloženo, můžeš dát /compact." (varianta C: čekáš na Tomův vstup, compact by ho přerušil, řekni to).
5. **Po compactu:** `/lg13-skills:load-from-store`.

## PRAVIDLA

- Nikdy neříkej, že jsi spustil `/compact`; nemůžeš.
- Rate v $/hod ani Playwright refresh usage se nepoužívá (zastaralé); sleduj využití ctx a účtové % přes `low-food-slow-down`.
- PreCompact hooky (`save_precompact.py`, git commit) běží automaticky při compactu.

## RELATED

`edge-check` (zóny), `save-min` (kroky save), `low-food-slow-down` (hlídání), `load-from-store` (obnova).

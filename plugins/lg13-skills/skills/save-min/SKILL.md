---
name: save-min
description: "Token-min save (3 kroky): queue --done + STAV append + save_checkpoint + edge calc. NIKDY /compact bez prior save min. Alias: volá save-to-store + remember."
user-invocable: true
---

# Save-Min — Alias pro save-to-store + remember

> **Alias skill.** Kombinuje původní session_manager checkpoint s novými skills.

## POŘADÍ

1. `python L:/LG13/app/agent/session_manager.py --mode save --instance <name> --ctx-now <N>`
   - queue --done aktivní task, STAV_NOW.md append (3 bullety), edge_calc
2. `/lg13-skills:save-to-store` — MySQL + git backup
3. `/remember:remember` — handoff note

## HARD RULE

NIKDY `/compact` bez prior save-min execution.

## ANTI-PATTERN (2026-05-10)

Strat dělal /compact bez save-min → ztrácel state. Fix: tato skill = prerekvizita pro compact.

## RELATED

→ `/lg13-skills:save-to-store` — plná dokumentace uložení
→ `/remember:remember` — handoff note

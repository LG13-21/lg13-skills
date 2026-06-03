---
name: restart
description: "Session transition: plan-to-store → remember → clear → (nové okno) remember from MySQL → plan-from-store. Přechod do nové session bez ztráty kontextu. Triggery: restart, session transition, new session, přechod do nové session, nová session."
user-invocable: true
---

# restart — Session Transition Skill

## PURPOSE

Bezpečný přechod do nové session. Pořadí:

1. `plan-to-store` — uloží plán do MySQL + git
2. `/remember:remember` — handoff note do `.remember/remember.md`
3. `/clear` — smaže kontext (Tom potvrdí), okno zůstane otevřené
4. *(Tom otevře nové Claude okno nebo novou session)*
5. `plan-from-mysql` — načte plán z MySQL (auto při session startu)
6. `/remember:remember` — načte handoff note

**Poznámka:** `/clear` vs `/compact` — clear smaže celý kontext, compact komprimuje. Pro čistý restart použij clear + nové okno.

---

## EXECUTION

### Fáze 1 — PŘED CLEAR (spusť v tomto pořadí)

#### Krok 1: Uloži plán

```
/lg13-skills:save-to-store
```

Uloží STAV_NOW.md (posledních 40 řádků) do MySQL + git.

#### Krok 2: Handoff note

```
/remember:remember
```

#### Krok 3: Clear NEBO nové okno

Vyber jeden z:
- `/clear` — smaže kontext v aktuálním okně, session pokračuje čistá
- Otevři nové okno Claude (nová session) — staré okno zůstane

Obě varianty fungují. `/clear` je rychlejší, nové okno zachová historii ve starém.

---

### Fáze 2 — PO RESTARTU (nová session)

#### Krok 4: Načti plán

```
/lg13-skills:load-from-store
```

Načte uložený plán z MySQL (nebo git jako fallback).

#### Krok 5: Načti handoff note

```
/remember:remember
```

---

## RYCHLÝ PŘEHLED

```
PŘED clear/close:             PO restartu (nová session):
──────────────────            ────────────────────────────
/lg13-skills:save-to-store    /lg13-skills:load-from-store
/remember:remember            /remember:remember
/clear  nebo  nové okno       pokračuj v práci
```

---

## RULES

- `save-to-store` je idempotentní — bezpečné volat vícekrát
- MySQL = primary, git = backup
- `/clear` navrhne Claude, Tom potvrdí — nikdy automaticky

---

## RELATED

- Skill `save-to-store` — uloží plán do MySQL + git
- Skill `load-from-store` — načte plán z MySQL nebo git
- Skill `save-min` — mini-checkpoint (STAV_NOW.md), volat PŘED restart
- Skill `remember` — handoff note
- MySQL tabulka `instance_plans` — centrální store pro všechny instance

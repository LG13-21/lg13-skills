---
name: plan-to-git
description: Generates commented multi-step plan as GitHub issue for ChatGPT guided session. Templates for research, review, filing. Triggers: 'plan-to-git', 'guided session', 'chatgpt plan', 'priprav plan', 'create plan issue', 'plan na git'
status: stable
user-invocable: true
---

# plan-to-git

## PURPOSE

Připraví strukturovaný multi-step plán jako GitHub issue. ChatGPT guided session pak čte issue krok po kroku, Tom validuje každý krok v issue comments, posun na další.

Výhoda: plan je veřejný, verzovaný, ChatGPT+Tom ho vidí synchronizovaně, každý krok má feedback slot.

---

## TEMPLATES

Vyber typ plánu:

| Template | Kdy použít |
|----------|-----------|
| `research` | Výzkumný plán — gather info, analyse, conclude |
| `review` | Guided review právního dokumentu (F-cycle) |
| `refactor` | Code/document refactoring plán |
| `filing-prep` | Příprava podání — VA check, LOCK workflow, ISDS |
| `blank` | Prázdný plán s jen strukturou |

---

## EXECUTION

### 1. Zjisti parametry

Pokud voláš `/plan-to-git` bez args — zeptej se:
- `template` — research | review | refactor | filing-prep | blank
- `subject` — o čem je plán (1 věta)
- `repo` — LG13-21/legal-ship-2026 nebo jiné
- `chatgpt_url` — volitelně: URL ChatGPT session (přidat do issue body)
- `steps_count` — počet kroků (default: 5)

### 2. Generuj body plánu

Každý krok má tuto strukturu:

```markdown
## Krok N: <action>

**Proč:** <rationale — proč je tento krok potřebný>
**Vstup:** <soubory / data / kontext>
**Očekávaný výstup:** <co by mělo vzniknout / co ověřit>
**Instrukce pro ChatGPT:** <konkrétní instrukce>

---
<!-- COMMENT SLOT: Tom doplní feedback po kroku N -->
```

### 3. Create issue

```bash
gh issue create \
  --repo <OWNER/REPO> \
  --title "[PLAN] <subject> — guided session" \
  --label "guided-session,plan" \
  --body "$(cat <<'EOF'
## Guided Session Plan: <subject>

**Template:** <template>
**ChatGPT session:** <url nebo TBD>
**Vytvořeno:** <date>

---

## Checklist
- [ ] Krok 1: <action>
- [ ] Krok 2: <action>
...

---

<krok 1 detail>
<krok 2 detail>
...

---

## Poznámky
<!-- Tom: sem přidávej globální feedback -->
EOF
)"
```

### 4. Výstup

```
✅ Issue vytvořen: https://github.com/<owner>/<repo>/issues/<N>

ChatGPT instrukce:
1. Otevři issue: <url>
2. Čti kroky sekvenčně
3. Po každém kroku napíše výsledek jako comment na issue
4. Tom validuje comment → pokračuj na další krok
```

---

## TEMPLATES DETAIL

### `review` template — guided review právního dokumentu

```markdown
## Krok 1: Přečti dokument

**Proč:** Základní orientace
**Vstup:** <file_path> (PDF nebo MD)
**Očekávaný výstup:** Shrnutí obsahu ve 3-5 bulletech
**Instrukce:** Přečti dokument, identifikuj: účel, strany, klíčové argumenty

## Krok 2: Vertikální analýza

**Proč:** Ověřit soulad s judikaturou
**Vstup:** Shrnutí z kroku 1 + zdroje v `analysis/sources/`
**Očekávaný výstup:** VA skóre 0-100 + doporučení
**Instrukce:** Proveď VA check dle `analysis/vertical/REGISTRY.md`

## Krok 3: Identifikuj rizika

...

## Krok 4: Navrhni úpravy

...

## Krok 5: Final GO/NO-GO

**Proč:** Tom rozhodnutí
**Instrukce:** Shrň vše, navrhni GO / NO-GO / PENDING
<!-- COMMENT SLOT: Tom → GO nebo HOLD -->
```

### `filing-prep` template

```markdown
## Krok 1: Phase 0 pipeline check
## Krok 2: Vertical Analysis
## Krok 3: LOCK checklist
## Krok 4: Tom visual check (PDF render)
## Krok 5: GO/KONEC STOP decision
```

---

## RULES

- Issue VŽDY s label `guided-session` — snadné filtrování
- Každý krok MUSÍ mít `<!-- COMMENT SLOT -->` — Tom ví kam psát
- Instrukce pro ChatGPT musí být konkrétní (ne "analyze" ale "identify top 3 risks")
- Pokud `filing-prep` → přidej STOP ORDER reminder do issue body
- Nikdy nevytvářej issue s citlivými daty (tokeny, hesla, osobní data)

## RELATED

- Skill `terminator` — executor pro plány vytvořené tímto skillem
- Skill `skill-creator` — meta-skill (tento skill byl vytvořen pomocí skill-creator)
- ChatGPT tampermonkey: `L:/GitHub/lg13-tampermonkey/lg13_chatgpt_ingest.user_JSON_v4.7.js`

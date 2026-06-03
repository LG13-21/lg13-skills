---
name: skills-manual
description: Use when you need detailed documentation for a specific skill (with skill name as argument) or a short manual for all skills (without argument, paginated 20 per page).
---

# skills-manual

## Usage

```
/lg13-skills:skills-manual                 # krátký manual pro všechny skills (20/strana)
/lg13-skills:skills-manual <skill-name>    # plný SKILL.md pro konkrétní skill
```

## EXECUTION

### Bez parametru — krátký manual všech skills (paginated)

```bash
python L:/LG13/app/agent/skills/skills_registry.py --format manual --page-size 20
```

### S parametrem — plný SKILL.md pro jeden skill

```bash
# Příklady
python L:/LG13/app/agent/skills/skills_registry.py --skill deep-read --format full
python L:/LG13/app/agent/skills/skills_registry.py --skill ping-pong --format full
python L:/LG13/app/agent/skills/skills_registry.py --skill brainstorming --format full
```

`--skill` akceptuje dirname (např. `deep-read`) nebo name z frontmatter.

## OUTPUT

### Bez parametru (manual mode)

```
--- Strana 1/5 ---

/deep-read [lg13-skills]
  Use when you need to read all channels since last cursor...

/ping-pong [lg13-skills]
  Use when instances need to communicate...

--- Strana 2/5 ---
...
```

### S parametrem (full mode)

Vypíše celý obsah SKILL.md — popis, parametry, příklady, execution kroky.

## RELATED

- `/lg13-skills:skills-list` — tabulkový přehled (rychlejší, bez detailů)
- `L:/LG13/app/agent/skills/skills_registry.py` — zdrojový skript
- Issue #90: `[REGISTRY] LG13 Skills Registry`

---
name: skills-list
description: Use when you need to see all available skills as a formatted text table. Shows skill name, namespace, and short description for every installed skill.
---

# skills-list

Zobrazí text tabulku všech dostupných skills z lg13-skills + superpowers.

## EXECUTION

```bash
python L:/LG13/app/agent/skills/skills_registry.py --format table
```

Volitelné filtry:
```bash
# Jen lg13-skills
python L:/LG13/app/agent/skills/skills_registry.py --format table --namespace lg13-skills

# Jen superpowers
python L:/LG13/app/agent/skills/skills_registry.py --format table --namespace superpowers
```

## OUTPUT

```
=== lg13-skills (N skills) ===
SKILL                 POPIS
------------------------------------------------------
/deep-read            Use when you need to read...
/ping-pong            Use when ...
...

=== superpowers (N skills) ===
...
```

## RELATED

- `/lg13-skills:skills-manual` — detailní info pro konkrétní skill nebo krátký manual pro všechny
- Issue #90: `[REGISTRY] LG13 Skills Registry` — živý seznam + návrhy

---
name: skill-catalog
description: Use when unsure which skill fits the current task, when a skill inventory or up-to-date catalog is needed, or after skills were added, removed or renamed. Trigger - "skill-catalog", "jaky skill", "ktery skill pouzit", "inventura skills", "katalog skills", "pick skill".
---

# skill-catalog

Inventura všech skills (lg13-skills, `~/.claude/skills`, plugin cache) + výběr skillu k úkolu. Doplňuje `skill-picker` (ručně psaný decision tree) automaticky generovaným katalogem.

## Použití

```bash
python L:/GitHub/lg13-skills/plugins/lg13-skills/skills/skill-catalog/skill_catalog.py pick "kontrola podani pred odeslanim" -n 5
python L:/GitHub/lg13-skills/plugins/lg13-skills/skills/skill-catalog/skill_catalog.py build   # po změně skills
```

- `pick` — BM25 přes name + description, česky i anglicky (bez diakritiky, prefixový stem, malý CZ→EN slovník). Vrací top-N: skore, `/skill`, kategorie/zdroj, popis.
- `build` — přegeneruje `catalog.json` + `SKILL_CATALOG.md` (tabulky po kategoriích, sekce „Problémy" = skills bez description nebo deprecated).

## Pravidla výběru

1. Běžná práce: `pick` s 3–6 slovy z úkolu, vezmi top 1–3. Skore pod ~8 = slabá shoda, ber jako tip, ne jistotu.
2. Při shodě procesního a implementačního skillu jdou první procesní (debugging, brainstorming), pak doménové.
3. Instance `coder`: nespouštět `brainstorming` ani `writing-plans` (CLAUDE.md), i když je `pick` navrhne.
4. Prázdný výsledek = přeformuluj, nebo `build` (katalog je zastaralý).

## Údržba

- Skill bez `description` ve frontmatteru dostane popis z prvního textového řádku; správně mu description doplnit (viz „Problémy" v `SKILL_CATALOG.md`).
- Deprecated skills (`replaced by ...` v textu) `pick` přeskakuje.
- Nepoužívat verze z `plugins/cache/lg13` (starý duplikát marketplace, skript ho ignoruje).

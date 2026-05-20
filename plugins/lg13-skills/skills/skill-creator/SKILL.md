---
name: skill-creator
description: Creates a new skill from template + git commit. Triggers: 'skill creator', 'new skill', 'create skill', '/skill-creator'
status: stable
user-invocable: true
---

# skill-creator

## PURPOSE

Meta-skill. Generuje nový `SKILL.md` z template, aktualizuje REGISTRY + CHANGELOG, commituje do `LG13-21/lg13-skills`.

Používej kdykoli chceš přidat nový skill do knihovny — místo ručního psaní SKILL.md.

---

## EXECUTION

### 0. Prerekvizity

```bash
# Repo musí existovat lokálně
ls L:/GitHub/lg13-skills/plugins/lg13-skills/skills/
```

### 1. Zjisti parametry

Pokud voláš `/skill-creator <name>` bez dalších args — zeptej se uživatele:
- `name` — slug (kebab-case, např. `my-skill`)
- `description` — 1 věta co skill dělá
- `trigger_words` — comma-separated (co uživatel napíše)
- `template` — basic | pingpong | monitor | meta (default: basic)
- `purpose` — 2-3 věty proč skill existuje

Pokud jsou args v příkazu → použij je, neptej se.

### 2. Vyber template

```
L:/GitHub/lg13-skills/TEMPLATES/basic.md       → obecný skill
L:/GitHub/lg13-skills/TEMPLATES/pingpong.md    → komunikační (ping-pong)
L:/GitHub/lg13-skills/TEMPLATES/monitor.md     → persistent Monitor arm
L:/GitHub/lg13-skills/TEMPLATES/meta.md        → skill operující na jiných skills
```

### 3. Substituuj placeholders + write

```python
from pathlib import Path

template = Path('L:/GitHub/lg13-skills/TEMPLATES/basic.md').read_text(encoding='utf-8')
# Nahraď {{name}}, {{description}}, {{trigger1}}, {{trigger2}}, {{purpose}}, atd.
content = template.replace('{{name}}', name).replace('{{description}}', description)
# ... ostatní substituty

skill_dir = Path(f'L:/GitHub/lg13-skills/plugins/lg13-skills/skills/{name}')
skill_dir.mkdir(exist_ok=True)
(skill_dir / 'SKILL.md').write_text(content, encoding='utf-8')
print(f'Written: {skill_dir}/SKILL.md')
```

Zkontroluj výsledný soubor — doplň prázdné sekce podle znalosti úkolu.

### 4. Update REGISTRY + CHANGELOG

```bash
cd L:/GitHub/lg13-skills && python scripts/gen_registry.py
```

CHANGELOG přidej řádek:
```
## [<date>] — add <name>
- New skill `<name>`: <description>
```

### 5. Git commit (+ optional push + optional PR)

```bash
cd L:/GitHub/lg13-skills
git add plugins/lg13-skills/skills/<name>/ REGISTRY.md CHANGELOG.md
git commit -m "feat(skills): add <name> — <description>"
git push origin main
# Optional PR:
# gh pr create --title "feat(skills): add <name>" --body "..."
```

---

## OUTPUT

```
Created: L:/GitHub/lg13-skills/plugins/lg13-skills/skills/<name>/SKILL.md
REGISTRY.md: updated (N+1 skills)
CHANGELOG.md: updated
Git: committed + pushed
```

---

## RULES

- Name musí být kebab-case, bez diakritiky, bez mezer
- Trigger words nesmí kolidovat s existujícími skills (zkontroluj REGISTRY.md)
- Vždy aktualizuj REGISTRY + CHANGELOG — ne jen SKILL.md
- Commituj jako `feat(skills): add <name>` nebo `fix(skills/<name>): <desc>`
- Pokud není local marketplace symlinked na repo — po commitu upozorni uživatele na `git pull` v marketplace dir

## RELATED

- Skill `plan-to-git` — přidej nový skill jako GitHub issue nejdřív
- TEMPLATES: `L:/GitHub/lg13-skills/TEMPLATES/`
- REGISTRY: `L:/GitHub/lg13-skills/REGISTRY.md`
- Repo: https://github.com/LG13-21/lg13-skills

#!/usr/bin/env python3
"""Generate REGISTRY.md from SKILL.md frontmatter."""
import re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / 'plugins' / 'lg13-skills' / 'skills'
REGISTRY = REPO_ROOT / 'REGISTRY.md'


def parse_frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip()
    return fm


def main():
    rows = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / 'SKILL.md'
        if not skill_md.exists():
            continue
        content = skill_md.read_text(encoding='utf-8', errors='ignore')
        fm = parse_frontmatter(content)
        desc = fm.get('description', '')[:90]
        status = fm.get('status', 'stable')
        user_inv = 'yes' if 'true' in fm.get('user-invocable', '').lower() else 'no'
        rows.append(f'| `{skill_dir.name}` | {desc} | {status} | {user_inv} |')

    output = '# REGISTRY.md — LG13 Skill Library\n\n'
    output += '> Auto-generated from SKILL.md frontmatter. Edit skills, not this table.\n'
    output += '> To regenerate: `python scripts/gen_registry.py`\n\n'
    output += f'**Total skills: {len(rows)}**\n\n'
    output += '| Skill | Description | Status | User-invocable |\n'
    output += '|-------|-------------|--------|----------------|\n'
    output += '\n'.join(rows) + '\n'

    REGISTRY.write_text(output, encoding='utf-8')
    print(f'REGISTRY.md updated — {len(rows)} skills')


if __name__ == '__main__':
    main()

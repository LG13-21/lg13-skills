# LG13 Skill Library

Claude Code skill library for the LG13 pipeline. Skills are versioned here and loaded via the Claude Code marketplace plugin.

## Install

```
Plugin path: C:\Users\tom\.claude\plugins\marketplaces\lg13\
(symlinked to this repo)
```

After cloning or pulling, restart Claude Code to reload skills.

## Structure

```
plugins/lg13-skills/skills/<skill-name>/SKILL.md   # skill definition
REGISTRY.md                                         # index of all skills
TEMPLATES/                                          # templates for skill-creator
.github/                                            # PR/issue templates
```

## Contribute

1. Fork → branch `feat/skill-<name>`
2. Add `plugins/lg13-skills/skills/<name>/SKILL.md`
3. Update `REGISTRY.md` (run `python scripts/gen_registry.py`)
4. Open PR — use the PR template

## Key skills

| Skill | Purpose |
|-------|---------|
| `heartbeat` | Keep-alive ping-pong loop, keep awake |
| `terminator` | Execute goal list from git issue |
| `avengers` | Team multi-instance goal execution |
| `skill-creator` | Create new skill from template + commit |
| `plan-to-git` | Generate structured plan as GitHub issue |
| `ping-pong` | Inter-instance JSON dialog protocol |
| `tmonkey-listen` | Persistent Monitor arm for tmonkey events |

See [REGISTRY.md](REGISTRY.md) for full list.

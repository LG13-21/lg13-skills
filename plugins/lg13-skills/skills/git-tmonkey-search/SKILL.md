---
name: git-tmonkey-search
description: "Search v L:/GitHub/lg13-tampermonkey/ repo (userscripts) přes gh CLI + Grep fallback. Trigger: 'git tmonkey', 'userscript search', 'najdi v TM repo'."
user-invocable: true
---

# Git-Tmonkey-Search — Userscript repo search

## PURPOSE

Hledat v `L:/GitHub/lg13-tampermonkey/` repo (Tampermonkey userscripts: ChatGPT ingest, Claude usage monitor, atd.). Primární gh CLI search code (indexed, fast); fallback local Grep když gh down/no auth.

---

## EXECUTION

### Helper (preferred — auto-fallback)

```bash
python L:/LG13/app/agent/skills/git_tmonkey_search.py --query "<term>"
```

Optional flags:
- `--repo <name>` (default: `lg13-tampermonkey`)
- `--owner <name>` (default: auto-detect from git remote)
- `--local-only` (skip gh, jen local Grep)
- `--limit <N>` (default: 20)

### Inline gh CLI (manual)

```bash
gh search code --repo <owner>/lg13-tampermonkey "<query>"
```

### Inline Grep fallback

```
Grep tool (NOT bash grep): pattern + path: "L:/GitHub/lg13-tampermonkey/"
```

---

## CO SE STANE

- helper try gh CLI search code first (indexed GitHub search)
- pokud gh fails (no auth / repo private / 404) → local Grep `L:/GitHub/lg13-tampermonkey/`
- vrátí list matches: file path + line number + context snippet

---

## OUTPUT

JSON nebo markdown table s: `{file, line, snippet, source: gh|local}`. `source` flag = transparency kde hit pochází.

---

## RULES

- **L:/GitHub/ canonical path** (per memory `reference_github_repos_path.md`) — NIKDY guess `C:\Users\tom\GitHub\` nebo `Documents\GitHub\`
- gh auth required pro search code (LG13-21 already authed per memory)
- Grep fallback NIKDY rekurzivní bash — vždy Grep tool
- Token-free (žádný Claude API call)

---

## USE CASES

- "kde scrapuje TM script Claude usage table?" → search "claude.ai/settings/usage"
- "co dělá adaptive_reload userscript?" → search filename "adaptive_reload"
- Před edit userscript: search related selectors

---

## RELATED

- `rag-search` skill — pro indexed local docs (komplementární)
- `tool-picker` skill — Grep vs gh search rozhodnutí
- Memory: `reference_gh_cli_available.md` (gh v2.92 + LG13-21 auth)
- Memory: `reference_github_repos_path.md` (L:/GitHub canonical)

---

## STATUS

Helper `git_tmonkey_search.py` — TBD (sonnet subagent buildí post-this skill write).

---

## FINAL

→ matches returned → instance Read přímo na file:line pro deep dive

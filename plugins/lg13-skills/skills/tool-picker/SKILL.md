---
name: tool-picker
description: "Decision tree: který tool kdy. Save-the-tokens hierarchie 1-7 + anti-patterns. Trigger: 'co použít', 'tool', 'Glob vs Grep', 'tool guide'."
user-invocable: true
---

# Tool-Picker — Save-the-tokens decision tree

## PURPOSE

Reference doc — žádný kód, žádné spuštění. Instance loaded on demand když si není jistá který tool zvolit.

---

## HIERARCHIE (od nejlevnějšího po nejdražší)

| # | Tool | Use when | Cost |
|---|------|----------|------|
| 1 | **MCP** (sqlite-comms, filesystem, imap, brave) | strukturovaná query, exact field | free / minimal |
| 2 | **DB / JSON** přes Python | známá schema, exact lookup | free (Python local) |
| 3 | **ctx_search / ctx_batch_execute** | output >20 řádků, repeat search | free (FTS5 indexed) |
| 4 | **Glob** | file patterns (`L:/Lukasek/**/CLAUDE.md`) | low (file metadata) |
| 5 | **Grep** | content match, file contains | low (ripgrep) |
| 6 | **Read** s `offset`+`limit` | známá pozice, malý kus | medium (file load) |
| 7 | **Bash** | git/mkdir/rm/mv/navigation, single targeted file op | last resort |

---

## ZAKÁZÁNO

- `Bash ls /složka` celé adresáře → **Glob `L:/path/**/*.ext`**
- `Bash find/dir` rekurzivní → **Glob pattern**
- `Bash cat/head/tail` velkých souborů → **Read s offset+limit, nebo ctx_execute_file**
- `Bash grep/rg` → **Grep tool**
- WebFetch URL → **mcp__plugin_context-mode_context-mode__ctx_fetch_and_index**

---

## DECISION TREE

```
Need data?
├── Z DB/JSON s known schema? → MCP nebo Python (1-2)
├── Z indexed knowledge? → ctx_search (3)
├── Najít soubor? → Glob (4)
├── Najít obsah? → Grep (5)
├── Číst známý soubor? → Read s offset+limit (6)
└── Git/mv/mkdir? → Bash (7)
```

---

## RULES (per CLAUDE.md SAVE-THE-TOKENS)

- Spawn worker: vždy `model: "haiku"` (file ops) nebo `"sonnet"` (reasoning), NIKDY default Opus
- Token-tip → poslat strat task `[TOKEN_SAVE_TIP P3]`
- Per memory `feedback_token_free_first_confirmed.md`: token-free FIRST, LLM call last

---

## ANTI-PATTERN — incident 2.5.2026 22:25

Strat hledal Likův CLAUDE.md přes `Bash ls L:/Lukasek/` + `ls Documents/` → session **9.2 USD/hr**. Jeden `Glob L:/Lukasek/**/CLAUDE.md` by stačil.

Memory: `feedback_no_bash_ls_for_search.md`.

---

## QUICK REFERENCE — common cases

| Task | Wrong | Right |
|------|-------|-------|
| najdi všechny CLAUDE.md | `Bash find / -name CLAUDE.md` | `Glob **/CLAUDE.md` |
| read 50MB log | `Bash cat big.log` | `ctx_execute_file path:big.log code:'...analysis...'` |
| search "TODO" v repo | `Bash grep -r TODO` | `Grep TODO` |
| fetch web page | `WebFetch url` | `ctx_fetch_and_index url` |
| list dir contents | `Bash ls dir/` | `Glob dir/*` (capped to relevant pattern) |

---

## FINAL

→ instance vybere correct tool podle hierarchie → minimum tokens spent

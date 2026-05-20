---
name: rag-search
description: "Search indexed knowledge base (FTS5 sandbox) přes ctx_search MCP. Token-efficient retrieval místo full-file Read. Trigger: 'rag', 'search docs', 'najdi v db'."
user-invocable: true
---

# RAG-Search — Indexed knowledge query

## PURPOSE

Hledat v context-mode FTS5 indexu (sandbox tool výstupy + manually indexed docs). Tokenově levnější než Glob/Grep + Read full file.

---

## EXECUTION

### Multi-query (preferováno — 1 call, N queries)

```
mcp__plugin_context-mode_context-mode__ctx_search(queries: ["q1", "q2", "q3"])
```

### Single query (default relevance mode)

```
mcp__plugin_context-mode_context-mode__ctx_search(queries: ["one query"])
```

### Timeline mode (memory-style ordered)

```
mcp__plugin_context-mode_context-mode__ctx_search(queries: ["q"], sort: "timeline")
```

### Filtered by source

```
mcp__plugin_context-mode_context-mode__ctx_search(queries: ["q"], source: "session-events")
```

---

## CO SE STANE

- query SQLite FTS5 index (auto-built z ctx_batch_execute / ctx_fetch_and_index)
- vrátí top hits s snippet + chunk metadata (label = section header)
- relevance mode = BM25 ranking; timeline = chronological
- **`source: "session-events"`** filtruje na compacted session data

---

## OUTPUT

JSON s arrays of {chunk_id, label, snippet, score, source, ts}. Use snippet pro decision, chunk_id pro deep-read přes ctx_execute.

---

## RULES

- **Nikdy NEČTI velké soubory full** — vždy Grep nebo ctx_search first
- Multi-query > single (parallel cheap, 1 call latency)
- `source: "session-events"` při post-compact recall
- Pokud no hits → check `ctx_stats` (index empty?) before fallback Grep

---

## USE CASES

- post-compact: "co jsem dělal v posledním turn?" → `ctx_search(queries: [...], source: "session-events")`
- code lookup: "kde je definice X?" → multi-query bias na variant naming
- doc retrieval: "jak funguje atom dispatcher?" → semantic snippet match
- vs. Grep: rag-search = indexed/semantic, Grep = exact regex; pro fuzzy/concept rag wins

---

## RELATED

- `tool-picker` skill — kdy rag vs Glob vs Grep vs Read
- ctx_batch_execute — primární gather tool (auto-indexes results)
- ctx_fetch_and_index — replace WebFetch (also auto-indexes)

---

## FINAL

→ relevant snippets returned → instance může pokračovat bez full file Read

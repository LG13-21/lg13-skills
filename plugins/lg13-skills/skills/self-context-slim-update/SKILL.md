---
name: self-context-slim-update
description: "Use when context usage >50%, memory files bloated or duplicated, index overhead growing, or preparing for major task requiring fresh context"
metadata: 
  node_type: memory
  originSessionId: 4fb56675-006e-478f-9a21-439bd2080ed4
---

# Self-Context Slim Update

Optimize session context by restructuring memory system without losing data. **Goal: Reduce token overhead 60-75% while preserving active memories.**

---

## When to Use

- **Context >50%** and session must continue without `/compact`
- **Memory files >100** or **index >10KB** (loaded every session)
- **Duplicate memories** (3 token-governance files, etc.)
- **Stale data** (>30 days old) mixed with active data
- **Before major task** requiring 10+ fresh turns

**NOT for:** Single-turn cleanups, session-end archival (use `/compact`), removing memories.

---

## Core Pattern

**Before:** Flat 68 files + 13KB index + 45 stale + 3 duplicates = 5k tokens overhead per load

**After:** 21 active files + 3.5KB index + 47 archived + consolidated = 1.8k tokens (64% savings)

```
memory/
├── SKILL.md / README.md          (guidance)
├── MEMORY.md                     (3.5KB index, TOP 5 per category only)
├── user/ feedback/ project/      (21 active files)
├── case_fact/ reference/         (organized by type)
└── _archive/                     (47 files >30d old, verify-before-use)
```

---

## Quick Reference: 5-Step Procedure

| Step | Action | Output |
|------|--------|--------|
| **1. Categorize** | Group all 68 files by prefix (feedback_, project_, etc.) | Category manifest |
| **2. Age filter** | Move files >30 days to `_archive/` | 45→47 archived |
| **3. Deduplicate** | Merge 3 token-files → 1 consolidated | 68→65 files |
| **4. Compress index** | Keep TOP 5 per category in MEMORY.md | 13KB→3.5KB |
| **5. Test + Commit** | Verify `/context` shows savings; git commit | GREEN ✓ |

---

## Implementation (5–10 min)

### Step 1: Categorize Files

```bash
# List all memory files by prefix
ls memory/*.md | sed 's/.*\///' | cut -d'_' -f1 | sort | uniq -c

# Expect: feedback(30+), case_fact(8), project(7), reference(5), user(1), other(N)
```

### Step 2: Archive Old Files (>30 days)

```bash
# Get today's date and file mtimes
today=$(date +%s)
threshold=$((30 * 86400))

for file in memory/*.md; do
    mtime=$(stat -c %Y "$file")
    age=$(( ($today - $mtime) / 86400 ))
    [ $age -gt 30 ] && mv "$file" memory/_archive/ && echo "→ $file ($age days)"
done
```

### Step 3: Consolidate Duplicates

Create `memory/feedback/feedback_<topic>_consolidated.md`:
- Merge 3 overlapping memories into 1
- Keep "Frontmatter" + main content from each
- Add "Consolidated from:" section listing originals
- Delete originals from `_archive/`

Example:
```markdown
---
name: topic_consolidated
description: [merged description]
---

# Topic — Consolidated

Consolidates: memory/_archive/topic_v1.md + topic_v2.md + topic_v3.md

[merged content]
```

### Step 4: Rewrite MEMORY.md

Keep **TOP 5 per category** (fresh + most-applied):

```markdown
# MEMORY INDEX

**Last updated:** [today] | **Tokens:** 1.8k | **Structure:** [diagram]

## TOP PRIORITIES (Fresh + Active)

### Feedback (5 most-applied rules)
- [title](feedback/file.md) — short context
- ...

### Project (3 active tasks)
- ...

### Archive
- 47 files in `_archive/` (>30d old)
```

**Target:** <150 words, <3.5KB

### Step 5: Verify + Commit

```bash
# Check context usage
/context
# Expected: tokens reduced 60-75%

# Commit
git add memory/
git commit -m "optimize: restructure memory for 64% context savings

- Categorized 68 files → user/feedback/project/reference/case_fact
- Archived 47 stale files (>30d) to _archive/
- Consolidated 3 token-governance → 1 (65% token save)
- Compressed MEMORY.md 13KB → 3.5KB (64% index savings)

Related: MEMORY.md updated with TOP-5 per category
"
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Delete instead of archive | Files go to `_archive/`, never rm |
| Keep stale data active | >30d → move, don't delete (may need later) |
| Over-compress index | Keep TOP 5 per cat actively used (not just newest) |
| Consolidate too aggressively | 3 files max per consolidation (preserve context) |
| Forget to update MEMORY.md | Index points to new structure, or agents read old refs |

---

## Red Flags — STOP If:

- Deleting files (RED FLAG: archive instead)
- Index <150 words per category (too aggressive)
- Active memories moved to archive (check dates)
- Consolidation creates >3KB merged file (too big)

---

## Result

**Before:** 68 files, 5k token load, 13KB index → **After:** 21 active + 47 archived, 1.8k token load, 3.5KB index

**Savings:** ~3.2k tokens per session (64% reduction) + 22 turns instead of 20 before `/compact`


---
name: github-actions-if-yaml
description: Use when writing GitHub Actions job or step `if:` conditions with multiple expressions joined by || or && — especially when the condition spans multiple lines. Symptoms of wrong approach: job is always skipped, condition evaluates to empty string, `##[debug]Evaluating condition` shows newlines.
---

# GitHub Actions `if:` YAML Multiline Conditions

## The Problem

YAML has two multiline block scalars. Only one works for GitHub Actions `if:` conditions.

| Scalar | Newlines | Result for `if:` |
|--------|----------|------------------|
| `\|` (literal) | **preserved** | ❌ Parser gets `expr\n\|\|\nexpr` → always skipped |
| `>-` (folded + strip) | collapsed to spaces | ✅ Parser gets `expr \|\| expr` on one line |

## Quick Fix

```yaml
# ❌ WRONG — job always skipped (newlines preserved)
if: |
  startsWith(github.event.comment.body, '/find') ||
  startsWith(github.event.comment.body, '/build')

# ✅ CORRECT — use >- (folded, strip trailing newline)
if: >-
  startsWith(github.event.comment.body, '/find') ||
  startsWith(github.event.comment.body, '/build')

# ✅ ALSO CORRECT — single line (no YAML scalar needed)
if: startsWith(github.event.comment.body, '/find') || startsWith(github.event.comment.body, '/build')
```

## Rule

**Whenever you write a multiline `if:` in GitHub Actions → use `>-`, never `|`.**

`>-` = fold newlines to spaces (`>`) + strip trailing newline (`-`). This produces a single-line expression that the GitHub Actions expression parser handles correctly.

## Symptoms of the Bug

- Job shows as `skipped` (not `false`, not an error)
- `##[debug]Evaluating condition for step` shows the condition
- The evaluated value is `''` (empty string) instead of `true`/`false`
- Removing the multiline format (putting it on one line) fixes it immediately

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `if: \|` multiline | Change `\|` to `>-` |
| `if: >` without `-` | Use `>-` (trailing newline causes issues) |
| Single `startsWith` on one line | OK — no scalar needed |
| `${{ }}` expression syntax in multiline | Use `>-`, still avoid `\|` |

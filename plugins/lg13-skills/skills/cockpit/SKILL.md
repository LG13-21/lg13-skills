---
name: cockpit
description: This skill should be used when the user asks to "show cockpit", "operation board", "status report", "/cockpit", "what's the state", "what do you need", "summary of work". Generates 1-page real-time operation board showing blockers, approvals needed, metrics, and quick links.
version: 0.1.0
---

# /cockpit — Operation Board (1-page status)

## PURPOSE

Generate real-time 1-page operation board for current instance. Shows:
- Active work (Filing #46, governance plan, etc.)
- Blockers + what's needed from others
- Metrics (RTG/RTS scores, token usage, 24h work)
- Quick links to relevant files/issues
- Decisions pending Tom/legal approval

Used for quick situational awareness without context bloat.

## EXECUTION

```bash
python L:/LG13/app/agent/skills/cockpit.py --instance coder --output L:/GitHub/legal-ship-2026/COCKPIT.md
```

Or inline (no file):

```bash
python L:/LG13/app/agent/skills/cockpit.py --instance coder --format markdown
```

## OUTPUT FORMAT

1-page Markdown (80-120 lines max):

```markdown
# COCKPIT — Coder Instance | 2026-05-23 01:15Z

## ACTIVE WORK
- Filing #46 (staging ready, awaiting Tom LOCK 2)
- Governance plan (Phase 1+2 ready, awaiting legal repo structure)
- Listener ChatGPT source (path confirmed: L:\GitHub\legal-ship-2026\ChatGPT_export)

## BLOCKERS & APPROVALS NEEDED
- [ ] Tom: LOCK 2 visual PDF review (Filing #46)
- [ ] Legal: Repo structure confirmation (listener daemon, signal files, DOCUMENT_MATRIX paths)
- [ ] Legal: Response to ping coder_to_legal_2026-05-23T010811Z.json

## METRICS
- RTG: 0.87 | RTS: 0.50 (LOCK 2 pending)
- Session: 38% | Weekly: (fetch from claude_usage_read)
- 24h work: 8 pings, 2 decisions, 3 reports

## CRITICAL FILES
- Plan: [cozy-kindling-castle.md](C:\Users\tom\.claude\plans\cozy-kindling-castle.md)
- Filing: [Issue #46](https://github.com/LG13-21/legal-ship-2026/issues/46)
- Staging: L:/GitHub/legal-ship-2026/runtime/ops/filing_16_4_output/
- Ping-pong: L:/GitHub/lg13-coder/runtime/ops/ping_pong/

## NEXT STEPS
1. Await Tom LOCK 2 (Filing #46)
2. Await legal response (repo paths)
3. Start Phase 1+2 governance impl (post-approval)
```

## AUTOMATION

Call weekly or on-demand:

```bash
# Via heartbeat skill (auto every 15 min)
/lg13-skills:heartbeat --with-cockpit

# Or manual
/cockpit
```

Generates fresh markdown to `L:/GitHub/legal-ship-2026/COCKPIT.md` (overwrites).

## RELATED

- Skill `heartbeat` — 15-min status keep-alive
- Skill `ping-pong` — inter-instance coordination
- Skill `rt` — RTG/RTS score fetch
- Governance plan: `cozy-kindling-castle.md`

---
name: terminator
description: Goal-list executor from git issue. Iterates goals, time-limited questions for blockers, continues without Tom. Triggers: 'terminator', 'execute goals', 'work the list', 'go through goals', 'splň goals'
status: stable
user-invocable: true
---

# terminator

## PURPOSE

Obdoba `/goal` ale pracuje s **listem goals z GitHub issue** (markdown checklist).

Iteruje goals jeden po druhém, používá team+advisor+tools, na blokery pošle time-limited otázku do issue a pokračuje dál pokud Tom neodpoví. Nezastaví se dokud nejsou všechny goals hotové nebo Tom neřekne STOP.

Tom nemusí být dostupný — Terminator pracuje autonomně.

---

## EXECUTION

### 1. Parse goal list z issue

```bash
# Výchozí: issue z aktuálního projektu (z CLAUDE.md nebo args)
# Args: /terminator #16  nebo /terminator LG13-21/legal-ship-2026#16
gh issue view <NUMBER> --repo <OWNER/REPO> --json body,title,number
```

Parsuj checkboxy z body:
```python
import re
goals = re.findall(r'- \[( |x|~)\] (.+)', issue_body)
# ' ' = pending, 'x' = done, '~' = in-progress
pending = [g[1] for g in goals if g[0] == ' ']
```

### 2. Pro každý pending goal — iteruj

```python
for goal_text in pending:
    # 2a. Mark in-progress
    mark_goal_inprogress(issue_number, goal_text)  # gh issue comment
    
    # 2b. Execute
    result = execute_goal(goal_text)  # subagent / tools / advisor
    
    # 2c. Na blocker → time-limited question
    if result.blocked:
        post_timelimited_question(issue_number, goal_text, result.blocker,
            deadline_h=4, default_action=result.proposed_default)
        # ⏰ format: "Goal X paused — replying in 4h locks default Y"
        mark_goal_deferred(issue_number, goal_text)
        continue  # přejdi na další goal
    
    # 2d. Done
    mark_goal_done(issue_number, goal_text)
    post_result_comment(issue_number, goal_text, result.summary)
```

### 3. Time-limited question format

```bash
gh issue comment <NUMBER> --repo <OWNER/REPO> --body "
## ⏰ [TERMINATOR] Goal paused — decision needed

**Goal:** <goal_text>
**Blocker:** <what's blocked>
**Proposed default:** <what will happen if no reply>

**Deadline: UTC+4h** — pokud Tom neodpoví, pokračuji s default.
"
```

### 4. Continue without answer (po deadline)

```python
import time
if time.time() > question_ts + 4*3600:
    apply_default(goal)
    mark_goal_done_with_default(issue_number, goal_text)
```

### 5. Final report

```bash
gh issue comment <NUMBER> --repo <OWNER/REPO> --body "
## ✅ [TERMINATOR] All goals complete

- Done: N
- Deferred (awaiting Tom): M
- Skipped: K

See individual comments for details.
"
```

---

## EXIT CONDITIONS

- Všechny goals done nebo deferred
- Tom napíše `STOP TERMINATOR` v issue (terminator čte issue každých ~5 minut)
- Token budget hit (`context_pct > 85`) → commit progress + compact

---

## RULES

- Vždy pracuj na **jednom goal najednou** — neparalelizuj bez instrukce
- Time-limited questions: deadline 4h default (konfigurovatelné v args)
- Nikdy neposílej mimo issue (email/ISDS) — to je STOP ORDER #1452 doména
- Pokud goal vyžaduje jiný instance (coder task v legal repo) → přepošli přes ping-pong

## RELATED

- Skill `avengers` — team verze terminator (více instancí)
- Skill `ping-pong` — inter-instance task dispatch
- Skill `heartbeat` — keep-alive během dlouhého terminator běhu
- Skill `plan-to-git` — příprava goal listu PŘED spuštěním terminator

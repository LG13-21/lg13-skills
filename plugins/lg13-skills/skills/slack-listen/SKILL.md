---
name: slack-listen
description: "Persistentní Slack listener — čte #lg13 (C0B3X5XC0JU), parsuje WAKE:<inst>:<msg> signály, routuje do ping-pong. Kombinuj s tmonkey-listen pro dual-channel wake. Trigger: 'slack listen', 'arm slack', 'slack wake', 'sleduj slack'."
user-invocable: true
---

# Slack-Listen — Slack #lg13 wake receiver

## PURPOSE

Instance sleduje Slack kanál `#lg13`. Každá zpráva ve formátu `WAKE:<inst>:<msg>` → okamžité probuzení instance → zpracování → pokračuje v práci.

Zdroj zpráv: CCR heartbeat routine (každé 2h) + manuální mention.

---

## CHANNEL

```
#lg13  ID: C0B3X5XC0JU
workspace: LG13 Slack
```

---

## EXECUTION

### 1. Zjisti instanci

```python
import os
cwd = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
# T_Coder → coder, legal-ship-2026 → legal, T000_Strat → strat
```

### 2. Arm Monitor na slack_listener_arm.py

```
python L:/LG13/app/agent/slack_listener_arm.py --instance <inst> --interval 30 --timeout 86400
```

Monitor zachytí každý `[SLACK_NOTIFY]` řádek.

### 3. Na každý [SLACK_NOTIFY] event

```python
# Přečti nové zprávy přes Slack MCP
# mcp__claude_ai_Slack__slack_read_channel(channel_id="C0B3X5XC0JU", limit=10)
# Parse: WAKE:<inst>:<msg> → zpracuj
# Ostatní zprávy → log nebo ping-pong
```

### 4. Alternativa — in-session MCP poll (bez daemona)

Pokud daemon není spuštěn, použij přímo v session:

```
Čti #lg13 přes Slack MCP:
  mcp__claude_ai_Slack__slack_read_channel  channel_id=C0B3X5XC0JU  limit=20

Parse zprávy novější než <last_check_ts>:
  - "WAKE:coder:<msg>" → zpracuj pokud inst=coder
  - "WAKE:all:<msg>"   → zpracuj vždy
  - ostatní            → log do ping_pong/_slack_log.jsonl
```

---

## WAKE MESSAGE FORMAT

```
WAKE:<instance>:<zpráva>
WAKE:coder:2h heartbeat — see #16
WAKE:all:EMERGENCY blocker nalezen
```

Instance: `coder` | `legal` | `strat` | `all`

---

## DAEMON SETUP (slack_listener.py)

Daemon polluje Slack API každých 30s bez Claude tokenů:

```bash
# Spustit daemon
python L:/LG13/app/agent/slack_listener.py --instance <inst>

# Watchdog (drží daemon živý)
python L:/LG13/app/agent/slack_listener_watchdog.py
```

Vyžaduje: `SLACK_BOT_TOKEN` v env nebo `L:/LG13/config/slack.env`

---

## KOMBINACE S TMONKEY-LISTEN

Oba listenery lze spustit současně — nezávislé kanály:

```
tmonkey-listen  →  filesystem tmonkey stack  →  wake
slack-listen    →  Slack #lg13               →  wake
ping-pong       →  filesystem ping_pong/     →  wake
```

Triple-channel coverage: žádná zpráva se neztrácí.

---

## RELATED

- Skill `tmonkey-listen` — filesystem atom listener
- Skill `ping-pong` — ping-pong filesystem protocol
- Daemon: `L:/LG13/app/agent/slack_listener.py`
- Watchdog: `L:/LG13/app/agent/slack_listener_watchdog.py`
- Channel: `#lg13` (C0B3X5XC0JU)
- Heartbeat routine: `trig_01UiDqkD1f4dJoQGcv5cSD1P`

---

## FINAL

→ Daemon arm nebo MCP poll → Monitor armed → každá WAKE zpráva = probuzení → zpracování → pokračuj.

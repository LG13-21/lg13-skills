---
name: chat-reply
description: Use when Tom asks for a reply via cockpit chat / Jarvis v2 chat, or when an instance should send a message back to Tom through the shared chat_messages channel visible in the browser cockpit.
---

# chat-reply — Odpověz Tomovi do cockpit chatu

Pošle zprávu z aktuální instance do MySQL `chat_messages` tabulky.
Zpráva se okamžitě zobrazí v cockpitu (browser poll každých 5s).

## EXECUTION

```bash
python L:/GitHub/lg13-coder/agent/skills/team_chat.py --to tom --msg "zprava"
```

Sender se detekuje automaticky z CWD (lg13-coder → coder, legal-ship-2026 → legal, atd.).

### Příklady

```bash
# Odpověď Tomovi
python L:/GitHub/lg13-coder/agent/skills/team_chat.py \
  --to tom --msg "ACK: task #155 hotovo — chat panel v cockpitu nasazen"

# Broadcast všem (Tom vidí v cockpitu)
python L:/GitHub/lg13-coder/agent/skills/team_chat.py \
  --to avengers --msg "BLOCKER: pl_server nereaguje na portu 8790"

# Přečíst příchozí zprávy od Toma
python L:/GitHub/lg13-coder/agent/skills/team_chat.py \
  --read [--since <last_id>]
```

## PARAMETRY

| Parametr | Default | Popis |
|----------|---------|-------|
| `--to` | (required) | Příjemce: tom / avengers / coder / strat / legal |
| `--msg` | (required) | Text zprávy (max 1000 znaků) |
| `--read` | — | Číst příchozí místo odesílat |
| `--for` | auto | Instance pro čtení (auto-detect z CWD) |
| `--since` | 0 | Čti od tohoto ID |

## KDY POUŽÍT

- Tom píše do cockpit chatu a čeká na odpověď instance
- Instance chce hlásit stav/blokery přímo Tomovi (ne jen přes ping-pong)
- Broadcast celému týmu o kritickém stavu (avengers channel)

## BACKEND

Chat jde přes MySQL `chat_messages` (stejná tabulka jako `lmt_chat` source).
Browser cockpit (`luky.ai-domy.cz/cockpit`) polluje každých 5s a přehraje beep
když přijde nová zpráva od instance (non-tom sender).

## RELATED

- `team-speak` — ping-pong broadcast (filesystem), chat-reply = MySQL/browser channel
- `lmt_chat` listen source — instance wake-up při nové Tom zprávě
- `cockpit` skill — otevře cockpit v browseru

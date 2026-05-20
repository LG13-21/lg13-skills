---
name: ping-pong
description: "LG13 cowork file-based komunikacni protokol pro inter-instance dialog (legal ↔ strat ↔ coder ↔ ...). Atomic JSON files v L:/LG13/runtime/ops/ping_pong/ + Monitor watcher + budget tracker. Low-cost (~100 tokenu/event) misto queue spamu. Trigger: 'ping pong', 'pong reply', 'odpovez Likovi pingponem', 'arm pingpong watcher', 'check ping pong'."
user-invocable: true
---

# Ping-Pong — LG13 cowork JSON protocol

## PURPOSE

Inter-instance dialog přes shared filesystem. Náhrada za queue spam (kde každý event ~100 tokenů a Tom musel polling). Monitor watcher detekuje nový soubor a budí instanci. Atomic write zaručí konzistenci. `_budget.json` tracker hlídá session limit.

**Source of truth:** `L:/LG13/runtime/ops/ping_pong/_README.md`

---

## EXECUTION

### 0. Issue #14 read (KAŽDÉ kolo — povinné)

Před každým pongem přečti nejnovější komentáře z issue #14 a zahrň stručný digest do těla pongu.
Pošli pong **oběma** — strat i legal — aby měli aktuální obraz bez nutnosti sami kontrolovat issue.

```bash
gh issue view 14 --repo LG13-21/legal-ship-2026 --comments 2>/dev/null | tail -40
```

Výstup shrň do 2–4 bullet pointů v sekci `### Issue #14 digest` v body pongu:
- Nové komentáře od posledního kola (author + 1 věta)
- Blocker nebo action item pokud existuje
- Pokud nic nového: `(žádné nové komentáře od R<předchozí>)`

Příklad sekce v body:
```markdown
### Issue #14 digest
- **strat** (16:42): STOP ORDER aktivní, Wave 1 zafreezeována
- **tom** (17:03): LOCK 2 čeká vizuální check PDF
- (žádné nové komentáře od R144)
```

### 1. Číst příchozí ping

```bash
# List nových souborů na me
ls -la L:/LG13/runtime/ops/ping_pong/*_to_<my-name>_*.json | sort -r | head -5

# Read jednu konkrétní zprávu
python -c "import json,sys; print(json.dumps(json.load(open(sys.argv[1])), ensure_ascii=False, indent=2))" L:/LG13/runtime/ops/ping_pong/<from>_to_<me>_<TS>.json
```

### 1b. Token read (periodický, ne každý pong)

Čte budget manager (viz skill `budget-manager`). Ostatní instance žádají alokaci, nečtou samy.
Pokud nemáš budget managera: čti sám každých ~5 kol nebo před velkým taskem.

```python
import subprocess, sys, json
r = subprocess.run([sys.executable, 'L:/LG13/app/agent/skills/claude_usage_read.py', '--json'],
    capture_output=True, text=True, timeout=5)
usage = json.loads(r.stdout)
# session_pct → context_pct v pongu; weekly_all → pro alokační rozhodnutí
```

### 2. Napsat odpověď (atomic)

```python
import json, time
from pathlib import Path

base = Path("L:/LG13/runtime/ops/ping_pong")
ts = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())
fname = f"{me}_to_{them}_{ts}.json"
msg = {
    "from": me, "to": them, "ts": ts,
    "round": "R145",                              # stejné round-id jako příchozí (nebo R<n+1> pro novou linii)
    "type": "pong",                               # ping | pong
    "in_reply_to": "<from>_to_<me>_<TS>.json",    # filename of msg you're replying to (jen pong)
    "subject": "<short>",
    "body": "<markdown>",                          # plný obsah, viz BODY STRUCTURE
    "decisions": {},                              # taken decisions; {} pokud none
    "questions_for_other": [],                    # nové Q pro receivera
    "refs": ["#NNN", "..."],                      # queue task IDs / file paths
    "tokens_spent_estimate": 800,
    "context_pct": 45,                            # POVINNÉ: z claude_usage_read.py --field session_pct
    "actual_consumption_rate_tok_per_h": 1200,    # skutečná spotřeba tok/h od session start
    "token_limit_5h": 200000,                     # limit pro aktuální 5h okno
    "token_used_5h": 45000,                       # spotřeba v tomto 5h okně
    "emergency_broadcast": False,                 # True = všechny instance vidí ⚠️
    "emergency_subject": "",                      # co hoří (jen při emergency_broadcast=True)
    "compact_signal": False,                      # True pokud context_pct > 70
    "priority": "P2"
}
tmp = base / f".{fname}.tmp"
tmp.write_text(json.dumps(msg, ensure_ascii=False, indent=2), encoding="utf-8")
tmp.replace(base / fname)
```

### 3. Update budget + log

```python
budget = json.load(open(base / "_budget.json"))
budget["total_tokens_session"] += msg["tokens_spent_estimate"]
budget[me]["context_pct"] = msg["context_pct"]
budget[me]["last_ping_ts"] = ts
budget["rounds_count"] += 1
if msg["context_pct"] > 70:
    budget[me]["should_compact"] = True
tmp = base / "_budget.json.tmp"
tmp.write_text(json.dumps(budget, ensure_ascii=False, indent=2), encoding="utf-8")
tmp.replace(base / "_budget.json")

with open(base / "_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps({"ts": ts, "from": me, "to": them, "round": msg["round"], "subject": msg["subject"], "tokens": msg["tokens_spent_estimate"]}) + "\n")
```

### 4. Arm Monitor (watcher pro příchozí)

```
Monitor tool tail watch L:/LG13/runtime/ops/ping_pong/ for new *_to_<me>_*.json files
→ on new file: notification → wake instance → goto step 1
```

---

## NAMING CONVENTION

- Lowercase `from_to_to` (legal_to_coder, NE Legal_to_Coder)
- ISO 8601 UTC bez milis: `2026-05-09T214332Z` (T před hodinou, Z na konci)
- Round-id: `R<n>` (R141 → R142 → R145), increment per topic chain — pokud reaguješ na R145, drž R145; pokud začínáš novou linii, R<latest+1>

---

## MESSAGE SCHEMA

**Povinná pole** (per strat #3073 canonical spec 2026-05-10):
- `from`, `to`, `ts` (ISO UTC Z bez milis), `round` ("R###"), `type` (`ping`/`pong`), `subject`, `body` (markdown)
- `in_reply_to` (filename — když type=pong)
- `decisions` (object — taken decisions; empty `{}` pokud none)
- `questions_for_other` (array — co chceš od receivera; empty `[]` pokud none)
- `tokens_spent_estimate` (int)
- `context_pct` (int 0-100) — **HARD RULE 11.5.2026:** volej `python L:/LG13/app/agent/skills/claude_usage_read.py --field session_pct` PŘED každým pong; fill skutečnou hodnotu, ne odhad. Pokud null → použij interní estimate + flag `compact_signal: true` pokud >70.
- `compact_signal` (bool)
- `priority` ("P0"/"P1"/"P2"/"P3")

**Doporučená:**
- `refs` (array — queue task IDs, paths, jiné pongy)
- `ack_round_other` (deprecated — use `in_reply_to` filename instead)
- `expected_response_eta` ("30 min", "tomorrow")
- `blocking` (string — co je blocked do response)

**Strukturované varianty (R145+):**
- `context` (paragraph s background)
- `request` (array of Q strings)
- `team_solve_proposals` (array akcí)
- `next_action_proposed` (chain: kdo → co → komu)

---

## BODY STRUCTURE

Markdown s povinným tail:

```markdown
## <Topic>

<obsah / odpovědi / questions>

### Budget state
- session: <session_pct>% | weekly: <weekly_all>% | plan: <plan>
- resets_in: <resets_in>
- ⚠️ weekly >90%: upozornit receivera, navrhnout odložení neurgentních tasků
- ⚠️ session >70%: compact_signal: true

## PLAN STATUS — <MY-NAME>

- [x] hotovo
- [~] běží
- [ ] pending
- [!] blocker / Tom decision needed
```

**`### Budget state` je povinná sekce v každém pongu** — obě strany vždy vidí aktuální stav tokenů. Receiver může okamžitě reagovat pokud limit blízko.

`## PLAN STATUS` na konci kazdeho pongu — Tom dozoruje, chce instant glance kdo kde stojí (memory `feedback_ping_pong_plan_checklist`).

---

## RULES

- **Budget state periodicky** — ne před každým pongem. Frekvence závisí na náročnosti: těžká práce (F-cyklus, subagenti) = každých ~3 kol; idle/FYI pony = každých ~10 kol. Budget manager (viz skill `budget-manager`) rozhoduje a alokuje — ostatní instance žádají.
- **Atomic write VŽDY** (`.tmp` → `Path.replace()`). Bez toho race condition s Monitor watcher.
- **Update `_budget.json` per round** — bez toho bleeding token budget.
- **Append `_log.jsonl`** — append-only audit, NIKDY rewrite.
- **`compact_signal: true`** když `context_pct > 70` — receiver ví že čekáš na compact. Nakopne k /compact dřív.
- **NEVYTVÁŘEJ duplicity** — pokud receiver už má pong se stejným round+ack, neposílej znovu.
- **NESEND z queue** věci které mají jít přes ping_pong (P0/P1 cowork dialog) — queue je pro one-shot tasking, ping_pong pro back-and-forth.
- **Ping_pong NEPŘENÁŠÍ data ven** (žádné odeslání Tomovi/legal/ISDS) — to je STOP ORDER #1452 + 5 LOCKS doména t002.

### Nová pole (2026-05-15) — POVINNÁ od R210+

- **`actual_consumption_rate_tok_per_h`** — spočítej: `(session_tokens_used / session_minutes) * 60`. Z `claude_usage_read.py --json` → `session_tokens / elapsed_h`. Receiver vidí tvoje tempo a může upozornit pokud hoříš.
- **`token_limit_5h` + `token_used_5h`** — strat alokuje per-instance. Žádej `BUDGET_REQUEST` v body pokud potřebuješ víc.
- **`emergency_broadcast: true`** — pokud víš o problému který se týká víc instancí (pl_server down, AVG blocker, TM broken). Šíří se dál dokud strat nepotvrdí resolved. Přidej `⚠️ EMERGENCY: <subject>` jako první řádek body.
- **`context_pct`** — VŽDY skutečná hodnota z `claude_usage_read.py --field session_pct`. Nikdy odhad. Toto je trigger pro /compact koordinaci přes instances.

---

## TOKEN-CHECK (periodický, ne před každým pongem)

Budget manager čte a alokuje — ostatní žádají přes `BUDGET_REQUEST` v ping-pongu.
Instance bez role budget managera: čti sám každých ~5 kol nebo před velkým taskem.

Frekvence dle náročnosti (viz skill `budget-manager`):
- těžká práce ~3 kola | normální ~7 kol | idle ~15 kol

Při check-inu pošli v body sekci `### Budget state`:
- session_pct, weekly_all, plan, resets_in

## 15-MIN HEARTBEAT (povinné)

Každých 15 minut — bez ohledu na ping — každá instance pošle heartbeat pong stratu:

```
strat_to_<me>_*.json nemusí přijít. Pošli stejně.
```

Formát subject: `[HEARTBEAT] <instance> <HH:MM> — <1 řádek co dělám>`

Body: jen PLAN STATUS + budget state. Žádný obsah navíc.

Účel: Tom vidí v cowork okně že město nespí. Strat vidí kde kdo stojí.

**Nikdy nečekej na ping aby ses ozval. 15 min = max ticho.**

---

## PERSISTENT TEAM PATTERN (2026-05-16, Tom)

**"Ping-pong je wake up call."** — sotva přijde míček, odehraj ho zpět.

### Pravidla
- Ping = wake up call. Po přečtení → pong (i kdyby jen "ACK, pracuji na X")
- Kdo má míč **pracuje**. Kdo nemá — taky může pracovat (vždy paralelní práce)
- **Palermo** — nikdy nespí celé městečko. Někdo je vždy vzhůru a pracuje
- Když je vše hotovo nebo jsme na limitech → **lazy tennis** (dlouhé výměny OK, bez práce)

### Kamos pattern — persistent team bez serveru

**Filesystem IS the orchestrator.** 2-3 instance mohou fungovat persistent bez pl_server, bez centrálního orchestrátoru:

```
Instance A                    Instance B
   │                              │
   ├── arm Monitor watcher ───────┤
   │   (watches *_to_A_*.json)    │   (watches *_to_B_*.json)
   │                              │
   │ -- writes strat_to_B.json ──▶│ Monitor notifies B → wake
   │                              │ B pracuje na vlastním tasku
   │◀── B_to_strat.json ──────── ─┤ B odesílá pong
   │ Monitor notifies A → wake    │
   │ A pracuje...                 │
```

**Kamos = buddy** — instance, která:
- Tě **hlídá** (Monitor watcher na tvé soubory) — když usneš, kamos tě budí
- Ti **pomůže** s prací (ping přijde s konkrétním taskem nebo otázkou)
- Vidí tvůj PLAN STATUS — ví kde jsi

### Arm kamos watcher (2 instance)
```bash
# Instance A armuje watcher na B soubory
# Instance B armuje watcher na A soubory
# Monitor tool — persistent, ~100 tok/event, žádný polling
cd L:/LG13/runtime/ops/ping_pong
while true; do
  latest=$(ls -t *_to_<me>_*.json 2>/dev/null | head -1)
  if [ -n "$latest" ] && [ "$latest" != "$last" ]; then
    echo "PINGPONG_NEW <me> file=$latest"
    last=$latest
  fi
  sleep 15
done
```

### Micro-server = filesystem + Monitor
- **Shared state:** JSON soubory v `ping_pong/` = message bus
- **Event notification:** Monitor watcher = push (ne polling)
- **Atomic writes:** `.tmp` → `replace()` = bez race condition
- **Schema:** `_budget.json`, `_log.jsonl`, `_README.md` = protokol
- **Zero infrastructure:** žádný port, žádný daemon, žádný server

---

## RELATED

- README: `L:/LG13/runtime/ops/ping_pong/_README.md` (canonical spec, evolution log)
- Skill `budget-manager` — kdo drží roli, jak žádat kapacitu, thresholdy
- Skill `deferred-plans` — odložit rozpracovanou věc do gitu místo nošení v kontextu
- Memory: `feedback_monitor_low_cost_pingpong`, `feedback_ping_pong_plan_checklist`
- Recipe: kernel `L:/Lukasek/CLAUDE.md` (queue vs ping_pong rozdělení)

---

## FINAL

→ pong sent / received → Monitor armed → čekej.

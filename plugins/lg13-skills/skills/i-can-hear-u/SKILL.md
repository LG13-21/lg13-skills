# I-Can-Hear-U — Alias pro listen-to-the-music

> **This skill should be used when** the user asks `/i-can-hear-u`, "spust listener", "poslouchej vsechny kanaly", "wake aggregator", "listen all".

## ALIAS

Tento skill je kratky alias pro `/lg13-skills:listen-to-the-music`. Stejna implementace, stejny daemon, stejne signal soubory.

---

## CO SKILL DELA (ne jen instrukce — POVINNE PROVED VSE)

Tento skill ma **dva kroky**, oba povinne. Nestaci spustit daemon a skoncit — bez Monitor watcher tato instance je hluchy odberatel (daemon pise, nikdo necte).

### Krok 1 — spust/over daemon (psani do coder.jsonl)

Auto-detect instance z cwd (lg13-coder → coder, legal-ship-2026 → legal, T000_Strat → strat) nebo z `.lg13_instance` souboru v repo root.

```bash
# Spust pokud uz nebezi (PID file v wake_signal/.daemon-<inst>.pid)
python L:/LG13/app/agent/listen_aggregator.py --instance <inst>
```

Pouzij `run_in_background: true`. Output bude: `[listen] start instance=<inst> sources=[pingpong, slack, tmonkey, github, plserver, queue, chatgpt]`.

Pokud uz bezi: `[listen] daemon already running pid=<N> for <inst>` — to je OK, pokracuj na Krok 2.

### Krok 2 — POVINNE arm Monitor watcher (cteni z coder.jsonl)

**Bez tohoto kroku jsem hluchy.** Daemon zapisuje do `wake_signal/<inst>.jsonl`, ale TATO Claude session se neprobudi, dokud Monitor neposle notification.

Pouzij `Monitor` tool s timto prikazem:

```bash
tail -n 0 -F L:/LG13/runtime/ops/wake_signal/<inst>.jsonl 2>&1 | grep --line-buffered -E '"source"'
```

Parametry Monitor toolu:
- `persistent: true` (drz az do session end)
- `timeout_ms: 3600000` (1h safety)
- `description: "<inst> wake_signal stream (chatgpt/github/pingpong/queue/slack/tmonkey/plserver)"`

`-n 0` = ignoruj historii, jen nove eventy od TEDka. `-F` = follow + retry pokud soubor rotuje. Grep `"source"` zachyti vsechny JSON eventy (kazdy ma `"source": ...` field).

---

## RUNTIME PATH WARNING

> **TODO 2026-05-23:** Tom prestehoval runtime z `L:/LG13/` do `L:/GitHub/legal-ship-2026/`. Tento skill stale spousti z deprecated `L:/LG13/app/agent/`. Az migrace dobehne (governance #49), uprav obe cesty v Krok 1 + Krok 2 na novy root. Zkontroluj pred spustenim: `ls L:/GitHub/legal-ship-2026/runtime/ops/wake_signal/` — pokud existuje, je to nove rooot a `L:/LG13/` je dead.

---

## VERIFIKACE PO STARTU

Po obou krocich over:

```bash
# Daemon alive?
cat L:/LG13/runtime/ops/wake_signal/.daemon-<inst>.pid
# Mela by byt platna PID a proces ma bezet

# Nove eventy za poslednich 5 min?
tail -10 L:/LG13/runtime/ops/wake_signal/<inst>.jsonl

# Monitor armed? — Monitor tool ti hned vrati "Monitor started (task ...)"
```

Pokud `coder.jsonl` neroste, nektery source plugin crashnul nebo ma spatnou cestu — viz `listen-to-the-music/SKILL.md` debug sekci.

---

## PLNA DOKUMENTACE

→ `skills/listen-to-the-music/SKILL.md` (architecture, source plugins, config, source plugin spec).

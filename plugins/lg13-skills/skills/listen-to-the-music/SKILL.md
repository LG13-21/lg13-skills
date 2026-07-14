# Listen-to-the-Music — Multi-channel wake aggregator

> `/i-can-hear-u` je širší startup skill (8 kroků: daemon+Monitor+CGE+CDC+issues+Jarvis+PRTSC+handoff sem) — jeho Krok 8 volá TUTO skill, pokud dorazí nový materiál. Tahle skill = (a) architektura daemon/Monitor kanálů níže + (b) sekce "PROCEDURE: New-Research Ingestion Pipeline" (čtení→extrakce→prioritizace→aplikace→polish).

## PURPOSE

Posloucha vsechny wake kanaly soucasne a stridi je do jedineho per-instance signal souboru. Instance Monitor-watcha ten signal a probudi se na jakykoliv event z libovolneho zdroje.

Aktualni source plugins:

| Source | Mechanism | Interval |
|---|---|---|
| `pingpong` | watch `L:/LG13/runtime/ops/ping_pong/*_to_<inst>_*.json` | 5 s |
| `slack` | Slack #lg13 poll, parse `WAKE:<inst>:msg` | 30 s |
| `tmonkey` | watch `L:/LG13/runtime/ops/tmonkey/*.json` | 10 s |
| `github` | `gh issue list` diff vs cache | 60 s |
| `plserver` | GET `/pl/atoms/feed` (fallback `/pl/open_questions`) | 45 s |
| `queue` | `instance_queue.py --check --name <inst>` | 30 s |
| `chatgpt` | watch `L:/LG13/runtime/ops/chatgpt_export/*.json` | 15 s |

Budouci sources: pridat modul do `L:/LG13/app/agent/listen_sources/` (viz `references/source_plugin_spec.md`).

## ARCHITECTURE

```
[7 sources, threads]            [aggregator daemon]            [Monitor watcher]
  pingpong  ─┐
  slack     ─┤
  tmonkey   ─┤
  github    ─┼──> listen_aggregator.py ──>  wake_signal/<inst>.jsonl  ──>  instance wake
  plserver  ─┤    (one per instance)         (append-only stream)
  queue     ─┤
  chatgpt   ─┘
```

- Daemon: `L:/LG13/app/agent/listen_aggregator.py` — bezi 1× per instance, pidfile lock
- Signal: `L:/LG13/runtime/ops/wake_signal/<inst>.jsonl` — append-only, JSON-per-line
- Stdout zaroven vypisuje `[WAKE_<SOURCE>] <id> pri=<P> <summary>` pro Monitor tool

## EXECUTION

### 1. Zjisti vlastni instanci

```python
import os
from pathlib import Path
cwd = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
# T_Coder → coder | legal-ship-2026 → legal | T000_Strat → strat | T002 → t002
```

### 2. Spust daemon (1× per instance)

```bash
python L:/LG13/app/agent/listen_aggregator.py --instance <inst>
```

Volitelne sources filter:

```bash
python L:/LG13/app/agent/listen_aggregator.py --instance coder --sources pingpong,slack,queue
```

Daemon je locked PID file `L:/LG13/runtime/ops/wake_signal/.daemon-<inst>.pid` — dvojspusteni faili.

### 3. Arm Monitor watcher na signal stream

```bash
# Monitor tool tail-follow on signal file
python L:/LG13/app/agent/listen_aggregator.py --instance <inst>
```

Nebo nezavisle (daemon uz bezi):

```
Monitor tool tail-watch L:/LG13/runtime/ops/wake_signal/<inst>.jsonl
keyword: WAKE_
```

Kazdy novy radek = wake. Stdout pattern `[WAKE_<SOURCE>]` chyti Monitor.

### 4. Status / stop / one-shot

```bash
# kdo bezi
python L:/LG13/app/agent/listen_aggregator.py --instance coder --status

# stop
python L:/LG13/app/agent/listen_aggregator.py --instance coder --stop

# jednorazovy poll vsech sources (bez daemon)
python L:/LG13/app/agent/listen_aggregator.py --instance coder --once
```

## SIGNAL FILE FORMAT

Append-only JSONL, jeden radek per event:

```json
{"source":"pingpong","event_id":"strat_to_coder_2026-05-22T210000Z.json","summary":"[R145] strat: ACK queue polling","payload_ref":"L:/LG13/runtime/ops/ping_pong/strat_to_coder_2026-05-22T210000Z.json","priority":"P1","target":"coder","ts":"2026-05-22T210105Z"}
```

Pole:
- `source` — plugin name
- `event_id` — stable unique ID v ramci source (filename, slack ts, issue#@updated, ...)
- `summary` — 1-line preview
- `payload_ref` — kde najit full data (path / URL / id)
- `priority` — P0/P1/P2/P3
- `target` — `<inst>` nebo `any`/`all`
- `ts` — UTC ISO8601 Z

## CONFIG (optional)

Per-source config v JSON souboru, predani `--config <path>`:

```json
{
  "github": {"repos": ["LG13-21/legal-ship-2026", "LG13-21/lg13-app"]},
  "slack": {"channel_id": "C0B3X5XC0JU"},
  "plserver": {"base_url": "http://localhost:8000"}
}
```

## CALLABLE FROM ANY INSTANCE

Daemon je standalone python skript bez plugin-specific deps. Kazda instance:

```bash
# coder
python L:/LG13/app/agent/listen_aggregator.py --instance coder &

# strat
python L:/LG13/app/agent/listen_aggregator.py --instance strat &

# legal
python L:/LG13/app/agent/listen_aggregator.py --instance legal &
```

Kazdy daemon ma vlastni PID + signal file → izolovany.

## PRIDANI NOVEHO SOURCE

Viz `references/source_plugin_spec.md`. Minimalni modul:

```python
# L:/LG13/app/agent/listen_sources/myfoo.py
from .base import Source, WakeEvent

class MyFooSource(Source):
    name = "myfoo"
    interval_sec = 60

    def poll(self):
        events = []
        # ... detect new things ...
        events.append(WakeEvent(
            source=self.name,
            event_id="unique-id",
            summary="1-line",
            payload_ref="path-or-url",
            priority="P3",
            target=self.instance,
        ))
        return self.dedupe(events)
```

A pridat `"myfoo"` do `DEFAULT_SOURCES` v `listen_aggregator.py`.

## RELATED

- `slack-listen` — Slack-only listener (legacy, supersedes by source `slack`)
- `tmonkey-arm` — TMonkey-only listener (legacy, supersedes by source `tmonkey`)
- `ping-pong` — protokol pro inter-instance dialog (source `pingpong` watcha)
- Daemon: `L:/LG13/app/agent/listen_aggregator.py`
- Sources: `L:/LG13/app/agent/listen_sources/*.py`
- Signal: `L:/LG13/runtime/ops/wake_signal/<inst>.jsonl`

## FINAL

→ Spust daemon → arm Monitor → vsechny kanaly hlidane → wake na cokoliv → pokracuj v praci.

---

## PROCEDURE: New-Research Ingestion Pipeline ("Final Read")

> Zdroj: Tom, 2026-07-12 — "je to rezim, ktery pouzivame casto". Spoustet pokazde, kdyz dorazi novy material (novy CGE/CDC soubor, nove ChatGPT vlakno, novy diktat) a je potreba ho dostat z "precteno" az po "zapracovano do podani".

Ctyri faze. Kazda faze ma jasny vstup/vystup, aby se nepreskakovalo (viz `lazy_boy`/`atom-read-all` — kazdy wake event/material se cte cely, ne "neni pro mne").

```
FAZE 0: CTENI  →  FAZE 1: EXTRAKCE  →  FAZE 2: PRIORITIZACE  →  FAZE 3: APLIKACE  →  FAZE 4: POLISH
(cely material)   (diamondy+judi)      (change-matrix rank)    (change-discipline)   (post-edit verify)
```

### FAZE 0 — Čtení (dokud není hotovo, nepokračuj)

- `cti-cele` — celý dlouhý soubor (ChatGPT export/JSON/TXT) po iteracích, ne jen výtažek
- `atom-read-all` (alias `lazy_boy`) — enforcement: každý atom/wake event se čte celý, žádné "není pro mě" bez přečtení
- Pro known-cursor zdroje (deep_read_config.json) místo cti-cele: `deep-read` / `deep-read-full`

### FAZE 1 — Extrakce (až je čtení hotové)

1. `diamond-pick` — vytáhni klíčové myšlenky/nálezy z přečteného
2. `deep-read` — re-run přes nově přečtený materiál, pokud FAZE 0 použila cti-cele (deep-read doplní diamond-scoring, které cti-cele samo nedělá)
3. `diamond-sentry` — sken na diamondy napříč konverzací/atomy, propojení s existujícím diamond indexem
4. `judi-sentry` — **jen pokud se v materiálu objevila nová judikatura nebo § odkaz** — ověř proti `judi_library/judi_index.json` dřív, než se citace dostane do change-matrixu

### FAZE 2 — Prioritizace na change-matrixu

1. `diamond-to-matrix` — pokud FAZE 1 vyprodukovala `diamonds.json`, převeď na prioritizovanou CHANGE_MATRIX (P0/P1/P2)
2. `lare` — argument ranking (CORE/SUPPORT/CONTEXT/EXCLUDED) na change-matrixu, pokud jde o argumentační obsah, ne jen mechanické doplnění
3. **Compliance check** — v repu není samostatný skill; použij `writing-doc` Zákon č. 1 (§ musí existovat přesně) na každou novou/změněnou § citaci v change-matrixu PŘED aplikací, ne až po ní

### FAZE 3 — Aplikace

- `change-discipline` — pokud přichází víc kousků postupně (Level 4: sbírej do `CHANGE_MATRIX_pending.md`, aplikuj najednou na konci kola)
- Verzování dle `writing-doc` (nová verze = přejmenuj soubor PŘED editací, CHANGE_MATRIX povinná)

### FAZE 4 — Post-edit polish/verify

Po aplikaci změn, PŘED renderem finálního PDF:

1. `slim-diet` — zeštíhlení, pokud dokument nabobtnal
2. `lex-atomic-render` — vizuální soulad s Lex Atomic designem (petit/evidence table/meta grid)
3. `VAM` — vizuální scan-readability, 3-second-scan test
4. `total-analysis-all-in-one` (nebo `legal-total-analysis` pro plný 14-lock CDC) — finální GO/NO-GO

**Zkratka:** pokud dokument už prošel `pipeline` Phase 1 (Build) dřív, `doc-polish` sám zavolá ekvivalent kroků 1–4 (attachments/dates/§/compliance/red-team/judge-sim) + lock release v jednom běhu — použij misto rucniho projeti FAZE 4, kdyz uz je dokument v mid-pipeline stavu.

### Poznámka k pořadí

FAZE 1 a 2 se NESMÍ přeskočit ani při "rychlé" opravě — i jednořádková změna z nového ChatGPT vlákna má projít alespoň `diamond-pick` + `judi-sentry` (pokud cituje §/judikaturu), jinak hrozí neověřená citace v podání (viz `writing-doc` Zákon č. 1, tabulka chybných citací).

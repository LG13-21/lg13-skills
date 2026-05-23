# Source Plugin Spec — listen-to-the-music

## OVERVIEW

Kazdy source = python modul v `L:/LG13/app/agent/listen_sources/`. Aggregator dynamicky najde tridy podedene od `Source` a spusti je v thread per source.

## MINIMAL CONTRACT

```python
from .base import Source, WakeEvent

class MyFooSource(Source):
    name = "myfoo"           # unikatni id, lowercase, no spaces
    interval_sec = 60        # poll period, default 30
    enabled = True           # set False to disable without removing file

    def __init__(self, instance: str, config: dict | None = None):
        super().__init__(instance, config)
        # optional: inicializace cursor, db, http session

    def poll(self) -> list[WakeEvent]:
        """Return new events detected since last poll. Dedupe handled by base.dedupe()."""
        events = []
        for thing in self._fetch():
            events.append(WakeEvent(
                source=self.name,
                event_id=f"unique-{thing.id}",   # stable across polls
                summary=f"foo: {thing.title[:80]}",
                payload_ref=str(thing.path),
                priority="P3",
                target=self.instance,
            ))
        return self.dedupe(events)
```

## WakeEvent FIELDS

| Field | Type | Required | Note |
|---|---|---|---|
| `source` | str | yes | == `self.name` |
| `event_id` | str | yes | stable, unique within source (idempotency key) |
| `summary` | str | yes | 1-line, <= 120 chars |
| `payload_ref` | str | no | path/URL/id k full datum |
| `priority` | str | no | `P0`/`P1`/`P2`/`P3`, default `P3` |
| `target` | str | no | instance name nebo `any`/`all`, default `""` |
| `ts` | str | no | auto-fill UTC ISO8601 Z pokud prazdne |

## DEDUPE

Base `dedupe()` mapuje na set `{source}::{event_id}`. Cap 5000 entries (FIFO trim).
Pokud tvuj source produkuje stejny event vickrat (file polling), dedupe to chyti.

## CONFIG

Per-source dict predan v `__init__`. Pristup pres `self.config.get('key', default)`.

```python
def poll(self):
    base_url = self.config.get("base_url", "http://localhost:8000")
    ...
```

Predani z aggregatoru: `--config config.json` kde:

```json
{
  "myfoo": {"base_url": "https://foo.example.com", "api_key": "..."}
}
```

## REGISTRATION

1. Vytvor `L:/LG13/app/agent/listen_sources/myfoo.py` s tridou
2. Pridej `"myfoo"` do `DEFAULT_SOURCES` v `listen_aggregator.py`
3. Otestuj: `python listen_aggregator.py --instance coder --sources myfoo --once`

## DOPORUCENA INTERVAL

- File watch (filesystem only): 5-15 s (levne)
- Lokalni HTTP poll: 30-45 s
- Externi API (GitHub, Slack): 60+ s (rate limit safety)
- Subprocess call (gh, instance_queue.py): 30+ s

## ERROR HANDLING

`poll()` muze vyhodit vyjimku — aggregator ji odchyti, vypise do stderr, pokracuje.
Pokud source je permanently down (chybi token, file dir neexistuje), vrat `[]` a soft-fail.

## CURSOR STATE

Pokud source potrebuje per-poll cursor (Slack ts, GitHub updated_at), uloz do:

```
L:/LG13/runtime/state/listen_<source>_cursor.json
```

Atomic write (`.tmp` + replace) jako vsude jinde v LG13.

## EXAMPLES

- File-based dedupe: `listen_sources/pingpong.py`, `tmonkey.py`, `chatgpt.py`
- Subprocess poll: `listen_sources/queue.py`, `github.py`
- HTTP poll: `listen_sources/plserver.py`
- Cursor + token: `listen_sources/slack.py`

## FUTURE EXTENSIONS

Snadne pridat:
- `ifttt` — IFTTT MCP poll (applet triggers)
- `linear` — Linear MCP issue tracker
- `email` — IMAP poll
- `isds` — datovka inbox (t002 only)
- `gdrive` — Google Drive new files via MCP

---
name: tmonkey
description: "Process fresh ChatGPT tmonkey exports — read inbox, identify Tom's requests [Ty:], route to instances, archive duplicates. Trigger when user says 'tmonkey', 'čti tmonkey', 'nové soubory z chatgpt', or when checking for fresh ChatGPT exports. Use this skill from ANY instance — it adapts to available file access."
user-invocable: true
---

# Tmonkey — ChatGPT Export Processor

## PURPOSE

Získat nové vstupy z ChatGPT a připravit je pro další zpracování.

---

## SMART READ PRINCIP

**"Číst vše, ale vědět co čtu a proč."**

Před plným čtením provést **fázi 0 — metadata scan**: získat tituly, priority, kategorie bez načítání plného textu do kontextu. Na základě toho vědomě rozhodnout co číst plně a proč.

```
Fáze 0: metadata scan → rozhodovací matice → fáze 1 plné čtení
```

| Signál | Akce |
|--------|------|
| P0 / Tom [Ty:] přímý požadavek | číst plně hned |
| P1 / role-relevant kategorie | číst plně |
| P2 / jiná instance / jiné téma | titul + summary, delegovat |
| P3 / duplikát / archiv | skip, mark-read |

**Context gate:** pokud ctx >50%, číst jen P0+P1. Zbytek mark-read bez čtení, zapsat titul do STAV_NOW.md.

**Per-day JSON** (pokud existuje `L:/LG13/atoms/daily/<YYYY-MM-DD>.json`): číst místo raw TXT — strukturovaný JSON s metadaty je levnější než parsing.

---

## EXECUTION

3-stupňový pickup per kernel CLAUDE.md (od nejlevnějšího):

```bash
# 1. PRIMARY — stack_reader (per-instance dedup, offset state)
python L:/LG13/app/agent/stack_reader.py --instance <name> --new --mark-read --limit 50 --format markdown

# 2. SECONDARY — atom_lookup (time-window, bez offset, CEST aware)
python L:/LG13/app/agent/atom_lookup.py --instance <name> --since '2h' --tz cest --format markdown --limit 100

# 3. FALLBACK — tmonkey_ts_reader (jen když pl_server :8790 timeout / stacks chybí)
python L:/LG13/app/agent/tmonkey_ts_reader.py --instance <name> --tail 200 --mark-read
```

**Kdy co:**
- `stack_reader --new --mark-read --limit 50` = default. Per-instance pickup, offset v `L:/LG13/runtime/stacks/_state/<inst>_offset.json`.
- `atom_lookup --since '2h' --tz cest` = time-window catch-up bez offset. Pro instance po >12h sleep `--since '24h'`.
- `tmonkey_ts_reader` = pouze když pl_server :8790 nereaguje.

CMD instance (t001/t002/t005/media): přidej `--format json` pro auto-parse.

---

## CO SE STANE

- stack_reader / atom_lookup vrátí nové atomy pro danou instanci
- atomy mají už hotový routing přes `atom_classifier` + `atom_dispatcher` (background daemon — instance neclassifikuje)
- offset state se posune (nové = unread)
- legal-relevant výtahy dělá pouze plnopřístupová instance (strat / main), ne CMD ani light worker (coder)

---

## OUTPUT

Stručný přehled:

- nové soubory
- rozdělení dle témat
- vytvořené extracty
- kam bylo co posláno

---

## RULES

- Claude NEčte raw soubory
- Claude NEparsuje obsah
- Claude pouze interpretuje výstup

---

## EXTRACT FORMAT (legal)

Plnopřístupová instance ukládá legal-relevantní výtah pro Lika do:

```
C:/Users/tom/Documents/tmonkey_legal/extracts/<YYYY-MM-DD>_<conv_slug>_legal.md
```

Plus log do `_extracts_log.json` (datum, source, output_path, řádky, hash).

Šablona výtahu (per ChatGPT proposal v slim souboru):

```markdown
---
source: <abs cesta k tmonkey souboru>
source_lines: <kolik řádků měl original>
extracted_at: <ISO timestamp>
conv_id: <z META, pokud je>
conv_title: <z META, pokud je>
extracted_by: strat
relevant_topics: [seznam témat]
---

# Legal extract — <conv_title> (<datum>)

## Strat summary (přečteno za Lika)
<3-6 vět>

## Tomovy [Ty:] požadavky (relevantní)
### #1 — <krátký popis>
> [Ty:] <přesný citát>

**ChatGPT odpověď (klíčový bod):**
<relevantní pasáže>

## Skipped (pro úplnost)
- Sekce mimo legal — odkaz na řádky originálu
```

Lik (čtenář) workflow: čte jen `extracts/<datum>_*_legal.md`, ne raw inbox/chatgpt/.

---

## ITERACE

Tato skill se iterativně zlepšuje. Po každém použití:
- Pokud metadata scan identifikoval špatnou kategorii → uprav threshold
- Pokud context gate příliš agresivně skipoval P1 → rozvolni
- Pokud per-day JSON chybí → ping coder (má za úkol append_to_daily())
- Výsledky iterace → ping strat s `[TMONKEY_IMPROVE]` v subject

Klíčové soubory ke sledování:
- `L:/LG13/inbox/chatgpt/json/<YYYY-MM-DD>/` — per-day JSON (coder task)
- `L:/LG13/runtime/stacks/<inst>_stack.jsonl` — stack pickup
- `L:/LG13/runtime/stacks/_state/<inst>_offset.json` — offset stav

---

## FINAL

→ fáze 0 scan → vědomé rozhodnutí → plné čtení relevantního → mark-read zbytek → iteruj

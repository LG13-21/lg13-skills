---
name: chatgpt-ask
description: "Posle otazku ChatGPT a ziska odpoved zpet jako LG13 atom. Pouzij kdyz instance potrebuje second-opinion, review, oponenta, gramatiku, nebo vysvetleni. ChatGPT je dobrej policajt a revizor (Tom). Workflow: chatgpt-send → pockej → chatgpt-force-read → stack_reader. Trigger: 'chatgpt ask', 'zeptej se chatgpt', 'potrebuju radu chatgpt', 'review v chatgpt', 'second opinion chatgpt', 'oponent', 'recenze chatgpt', 'at to chatgpt zkontroluje'."
user-invocable: true
---

# ChatGPT-Ask — send question, get atom back

## PURPOSE

Kdykoli instance potrebuje druhy nazor, review, oponenta nebo vysvetleni — ChatGPT poslouzi.
Workflow: **send** zpravy → **pockej** na odpoved → **force TM** aby precetl → atom zpet do stack.

---

## WORKFLOW (3 kroky)

### Krok 1 — Posli otazku

Pouzij skill `chatgpt-send`:
```
chatgpt-send project=Legal message="Q: <otazka anonymized>"
```
nebo do existujiciho threadu:
```
chatgpt-send thread=https://chatgpt.com/c/<id> message="Q: <otazka>"
```

Zapis si **thread URL** z outputu.

### Krok 2 — Pockej na odpoved

ChatGPT potrebuje cas. Typicky:
- Jednoducha otazka: 15-30s
- Review dokumentu: 45-90s
- Komplexni analyza: 2-3min

### Krok 3 — Force TM ingest + precti atom

```
chatgpt-force-read url=<thread URL z kroku 1>
```

Pak precti odpoved:
```bash
python L:/LG13/app/agent/stack_reader.py --instance <my-name> --new --mark-read --limit 50
```

---

## ANONYMIZATION CHECKLIST (pred kazdou query)

ChatGPT nema LG13 context ani pristup k case files — to je vyhoda. Ale nesmis leakovat:

- [ ] Zadne jmeno protistrany ani klienta
- [ ] Zadne RC
- [ ] Zadna spis. zn. (napr. `0 P 29/2026` → "civili rizeni o uprave pomeru")
- [ ] Zadne datum krome roku
- [ ] Zadne jmeno soudu / soudce
- [ ] Zadne LG13 internals (queue IDs, F-cycle, STOP ORDER)

Formuluj jako „Q: ..." ne „udělej X" — ChatGPT nema tvuj kontext, otazka musi byt sobestacna.

---

## USE CASES

| Instance | Priklad query |
|----------|--------------|
| legal | "Q: Je tento argument logicky konsistentni? [anonymized text]" |
| coder | "Q: Proc tento Python kod hazi tuto chybu: [error]" |
| writer | "Q: Zkontroluj grammatiku a styl teto vety: ..." |
| strat | "Q: Vidis diry v tomto rozhodovacim procesu: [popis]" |
| jcu | "Q: Co znamena tato akademicka politika: [text]" |

---

## NOTES

- **Single-thread**: pokud Lik a coder oba posilaji do stejneho threadu, nechej ~10s gap
- **No PII**: viz checklist — ChatGPT odpovedi mohou byt stored
- **New chat vs existing**: pro kazde nove tema = novy chat (project=Legal). Navazujici Q = stejny thread.
- **Alternativa pro dokumenty**: pushnout anonymized verzi na GitHub, pak pouzit `/github` special pres `chatgpt-send`

---

## RELATED

- `chatgpt-send` — step 1 (posle zpravu)
- `chatgpt-force-read` — step 3 (TM ingest odpovedi)
- `stack_reader` — step 3 (precte atom zpet)

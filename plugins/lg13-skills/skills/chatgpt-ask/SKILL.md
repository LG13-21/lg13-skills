---
name: chatgpt-ask
description: "Posle otazku ChatGPT a ziska odpoved zpet jako LG13 atom. Pouzij kdyz instance potrebuje second-opinion, review, oponenta, gramatiku, nebo vysvetleni. ChatGPT je dobrej policajt a revizor (Tom). Workflow: gpt-bridge (claude-in-chrome) → wake_signal → cge_legal_digest. Trigger: 'chatgpt ask', 'zeptej se chatgpt', 'potrebuju radu chatgpt', 'review v chatgpt', 'second opinion chatgpt', 'oponent', 'recenze chatgpt', 'at to chatgpt zkontroluje'."
user-invocable: true
---

# ChatGPT-Ask — send question, get atom back

## PURPOSE

Kdykoli instance potrebuje druhy nazor, review, oponenta nebo vysvetleni — ChatGPT poslouzi.
Workflow: **send** zpravy → **pockej** na odpoved → **force TM** aby precetl → atom zpet do stack.

---

## WORKFLOW (přes gpt-bridge, bez Edge)

Detail a smyčka: skill `gpt-bridge` (#770). Edge/CDP (`chatgpt-send`, `chatgpt-force-read`) je DEPRECATED.

1. **Init** (jednou): `python L:/GitHub/legal-ship-2026/scripts/gpt_bridge.py init --conv-id <conv_id> --run <nazev> --max-iter 10` (conv_id z `chatgpt.com/c/<conv_id>`; vlákno najdi `chatgpt-find`).
2. **ASK**: `gpt_bridge.py prompt --conv-id <id> --text "Q: <otazka>"` → vytištěný text (prefix `[BRIDGE run#n]`) vložit a odeslat v existujícím přihlášeném Chrome přes claude-in-chrome (tab `chatgpt.com/c/<id>`).
3. **WAIT**: `gpt_bridge.py wait --conv-id <id> --timeout 600` (čeká na wake_signal source=chatgpt, ne polling DOM) → odpověď | TIMEOUT | HUMAN_GATE.
4. **Další kolo?**: `gpt_bridge.py check --conv-id <id> --findings-file <f>` → CONTINUE | STOP:<důvod>.

Chrome vypadl / tab zmizel → BLOCKED, zeptat se Toma. Nikdy nespouštět Edge ani nerestartovat prohlížeč. Tomova zpráva v threadu = HUMAN_GATE (pauza).

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
- **Alternativa pro dokumenty**: pushnout anonymized verzi na GitHub a poslat odkaz pres gpt-bridge

---

## RELATED

- `gpt-bridge` — smyčka ASK/WAIT/check (nahrazuje chatgpt-send + chatgpt-force-read)
- `chatgpt-find` — najde conv_id offline

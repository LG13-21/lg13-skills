# WAVE SHIP PROTOKOL (Tom directive 2026-05-24)

## Kompletní podmínka SHIP (po odemčení T002 locku)

```
Tom UL + Legal UL + Strat UL + Coder UL + ChatGPT UL (Tom) + Claude desktop UL (Tom)
→ After ALL UL → čekat 15 min → T002 RTG check
→ RTG = 1.0 → SHIP
```

## Lock tracker (Wave 1a — vzor 2026-05-24)

| Lock | Instance | Stav |
|------|----------|------|
| Tom | Tom | UL po KONEC STOP |
| Legal | legal | UL — procesní kontrola PASS |
| Strat | strat | UL — konzistence PASS |
| Coder | coder | UL — bundle/tech PASS |
| ChatGPT | Tom (v ChatGPT) | UL |
| Claude desktop | Tom (cowork) | UL |
| **T002 RTG** | t002 | RTG = 1.0 → SHIP |

## Time capsule protokol

Po deklaraci posledního UL → t002 dostane time capsule s delay 15 min.
T002 provede RTG check (RTG = 1.0 = vše ready), pak odešle.

## DS ověření (incident 2026-05-24)

DS soudu NIKDY tipovat ani dohledávat z paměti — vždy ověřit z ISDS inboxu:

```bash
isds_sender.py --inbox
```

DS je v hlavičce každé přijaté zprávy od soudu (pole `dbIDSender`).
Je také viditelná v PDF od soudu (hlavička dopisu, řádek "ID DS:").

**Příklad:** OS České Budějovice = `ws6abvh` (ověřeno z V000003.PDF, přípis 20.4.2026 JUDr. Veselý).
**Chybná hodnota která byla použita:** `snkabbm` = Městský soud v Praze (ŠPATNĚ).

## Ping-pong protokol pro LOCK UL

Každá instance deklaruje UL přes ping-pong JSON:
```json
{
  "subject": "[LOCK UL] <instance> — Wave Xa LOCK odemcen",
  "decisions": {"<instance>_lock": "UL"}
}
```

Strat agreguje přijaté UL a hlídá kompletnost před T002 time capsule.

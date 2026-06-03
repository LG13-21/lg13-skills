# legal-daily-brief — Denní přehled lhůt, institucí a pipeline

> **Trigger:** "spusť daily brief", "legal brief", "/legal-daily-brief", "denní přehled"

## CO SKILL DĚLÁ

Spustí `scripts/legal_daily_brief.py` a zobrazí výsledek.
Generuje `daily_briefs/YYYY-MM-DD_legal_brief.md` s:
- STOP ORDER status banner
- Aktivní pipeline tabulka (instituce + deadline)
- Open GitHub issues (plány)
- Lhůty a termíny
- Dlouhodobé právní okruhy
- ISDS + komunikace checklist

## EXECUTION

```bash
cd L:/GitHub/legal-ship-2026
python scripts/legal_daily_brief.py
```

## OUTPUT

Soubor: `daily_briefs/YYYY-MM-DD_legal_brief.md`

## INTEGRACE DO SESSION STARTU

Volej jako krok 3-4 session bootstrapu (I165 direktiva):
1. load-from-store
2. issue-sync
3. **legal-daily-brief** ← zde
4. ping-pong heartbeat

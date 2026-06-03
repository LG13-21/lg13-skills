# LG13 Token Diet — known fixes

## Fix 1: L:\GitHub\CLAUDE.md smazat (Tom action)
Workspace CLAUDE.md způsobuje načítání legal-ship-2026 memory (4.1k case facts)
do každé coder/strat session. Smazat ručně:
  del "L:\GitHub\CLAUDE.md"
Dopad: -4k tokenů overhead per turn v coder/strat session.

## Fix 2: claude.yml max_turns + timeout (pending push)
Přidat do všech 4 bot workflows:
  max_turns: 5
  timeout_minutes: 8
Dopad: každý bot run max ~8 min místo neomezeného.

## Fix 3: Loop system — audit (viz níže)

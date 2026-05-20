# REGISTRY.md — LG13 Skill Library

> Auto-generated from SKILL.md frontmatter. Edit skills, not this table.
> To regenerate: `python scripts/gen_registry.py`

**Total skills: 47**

| Skill | Description | Status | User-invocable |
|-------|-------------|--------|----------------|
| `action-telemetry` | "Log akci + report top actions + share přes ping_pong. Tom 2026-05-10 cost optimization pr | stable | yes |
| `atom-search` | "Vyhledá atomy z konkrétní ChatGPT konverzace (conv_id) nebo dle instance/time window, seř | stable | yes |
| `autosave` | "Auto-save + auto-compact při 15-25% zbývajícího kontextu. Dokončí rozdělanou věc, uloží s | stable | yes |
| `avengers` | Team terminator — multiple instances collaborate on shared goal list. Director dispatches, | experimental | yes |
| `budget-manager` | "Řízení token budgetu napříč LG13 instancemi. Instance s touto rolí čte aktuální spotřebu, | stable | yes |
| `budget-watchdog` | Proactive token budget monitoring. Watches weekly/session limits, sends alerts, enforces t | experimental | yes |
| `chatgpt-ask` | "Posle otazku ChatGPT a ziska odpoved zpet jako LG13 atom. Pouzij kdyz instance potrebuje  | stable | yes |
| `chatgpt-find` | "Vyhledá vlákna v ChatGPT historii přes CDP + Playwright search form. Vrátí seznam threadů | stable | yes |
| `chatgpt-force-read` | "Prinuti TM (Tampermonkey) aby precetl a ingestoval ChatGPT vlakno — naviguje Edge na thre | stable | no |
| `chatgpt-search` | "Vyhledá text nebo konverzaci v ChatGPT chatech přes vyhledávání v sidebaru nebo přes Play | stable | yes |
| `chatgpt-send` | "Posle zpravu do ChatGPT vlakna pres Playwright CDP — ovlada Edge prohlizec a zapise zprav | stable | yes |
| `deferred-plans` | "Uloží nedokončený nebo odložený plán do gitu, aby ho příští session mohla zvednout. Trigg | stable | yes |
| `edge-check` | "Edge-to-autocompact zone check. Spočítá zone (green/yellow/orange/red) + action + turns_r | stable | yes |
| `file-catalog-search` | "Najít soubor přes librarian instance místo manual Glob. Standardizovaný entrypoint pro ev | stable | yes |
| `filing-pipeline` | "Kompletni pipeline pro pripravu pravniho podani. Phase 1 = Build (konsolidace, struktura, | stable | no |
| `git-tmonkey-search` | "Search v L:/GitHub/lg13-tampermonkey/ repo (userscripts) přes gh CLI + Grep fallback. Tri | stable | yes |
| `heartbeat` | Keep-alive ping-pong loop + keep-awake clause. Triggers: 'heartbeat', 'keep awake', 'stay  | stable | yes |
| `isds` | > | stable | no |
| `lare` | > | stable | no |
| `legal-total-analysis` | Lean meta-skill pre-flight audit DÁVKY právního podání před F1X.4 capsule build a ISDS ode | stable | no |
| `lg13-end` | "Ukončení session — uloží stav, aktualizuje CLAUDE.md, pošle report strat, compact. Trigge | stable | no |
| `lg13-init` | "Inicializace session — načte stav, přečte frontu, tmonkey, pl_stats, vygeneruje briefing. | stable | yes |
| `lg13-save` | "Průběžné uložení stavu session — uloží progress, aktualizuje CLAUDE.md pokud třeba, compa | stable | no |
| `locks-workflow` | > | stable | no |
| `ocr-git` | "OCR pipeline pro court/AT/OSPOD evidence — scan + index + search. Wrapper kolem legal_ocr | stable | yes |
| `ping-pong` | "LG13 cowork file-based komunikacni protokol pro inter-instance dialog (legal ↔ strat ↔ co | stable | yes |
| `plan-to-git` | Generates commented multi-step plan as GitHub issue for ChatGPT guided session. Templates  | stable | yes |
| `prtsc` | "Podiva se na posledni screenshoty z OneDrive Screenshots slozky a precte jejich obsah pom | stable | no |
| `rag-search` | "Search indexed knowledge base (FTS5 sandbox) přes ctx_search MCP. Token-efficient retriev | stable | yes |
| `save-min` | "Token-min save (3 kroky): queue --done + STAV append + save_checkpoint + edge calc. NIKDY | stable | yes |
| `skill-creator` | Creates a new skill from template + git commit. Triggers: 'skill creator', 'new skill', 'c | stable | yes |
| `slack-listen` | "Persistentní Slack listener — čte #lg13 (C0B3X5XC0JU), parsuje WAKE:<inst>:<msg> signály, | stable | yes |
| `strat-end` | "Strat session end — uloží vše, failne rozpracované tasky, aktualizuje CLAUDE.md, report,  | stable | yes |
| `strat-init` | "Strat session init — tmonkey, fronta, pl_stats, failed tasky, t002 dohled, daily briefing | stable | yes |
| `strat-save` | "Strat session save — checkpoint s progress reportem, CLAUDE.md update, t002 dohled, waiti | stable | yes |
| `team-launcher` | > | stable | no |
| `terminator` | Goal-list executor from git issue. Iterates goals, time-limited questions for blockers, co | stable | yes |
| `tmonkey` | "Process fresh ChatGPT tmonkey exports — read inbox, identify Tom's requests [Ty:], route  | stable | yes |
| `tmonkey-arm` | "Arm Monitor watcher na <inst>_stack.jsonl mtime change → notification → wake instance pro | stable | yes |
| `tmonkey-diag` | "Diagnostika tmonkey atom flow health — pl/stats, atom_lookup, dispatcher routing, kde se  | stable | yes |
| `tmonkey-listen` | "Persistentní příjem atomů — instance může normálně pracovat, každá nová zpráva ji probudí | stable | yes |
| `tmonkey-monitor` | "Zapni zvonění — arm Monitor na tmonkey_arm.py, každý nový atom okamžitě probudí instanci. | stable | yes |
| `tmonkey-web` | "Open Chrome, navigate to ChatGPT LG13 project, open recent conversations in sequence so T | stable | no |
| `token-limit-read` | "Read current Claude usage (session % / week % / plan tier) z TM script ingested data. Tok | stable | yes |
| `tool-picker` | "Decision tree: který tool kdy. Save-the-tokens hierarchie 1-7 + anti-patterns. Trigger: ' | stable | yes |
| `web-up` |  | stable | no |
| `zero-tokens` | "Zero-token execution stack: Python, Git, Ollama, context-mode. Kdy co použít, konkrétní s | stable | yes |

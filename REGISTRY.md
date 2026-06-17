# REGISTRY.md — LG13 Skill Library

> Auto-generated from SKILL.md frontmatter. Edit skills, not this table.
> To regenerate: `python scripts/gen_registry.py`

**Total skills: 103**

| Skill | Description | Status | User-invocable |
|-------|-------------|--------|----------------|
| `action-telemetry` | "Log akci + report top actions + share přes ping_pong. Tom 2026-05-10 cost optimization pr | stable | yes |
| `atom-read-all` | Use when receiving any wake event about atoms — enforces reading atom content before any r | stable | no |
| `atom-search` | "Vyhledá atomy z konkrétní ChatGPT konverzace (conv_id) nebo dle instance/time window, seř | stable | yes |
| `attachment-pipeline` | Orchestrator pro přílohy soudního podání — volá attachment-score, deferred-plans, filing-p | stable | yes |
| `attachment-score` | Ohodnotí přílohy soudního podání (PDF/PNG) dle síly důkazu, relevance a stavu. Výstup: sco | stable | yes |
| `autosave` | "Auto-save + auto-compact při 15-25% zbývajícího kontextu. Dokončí rozdělanou věc, uloží s | stable | yes |
| `avengers` | Team terminator — multiple instances collaborate on shared goal list. Director dispatches, | experimental | yes |
| `avengers-meeting` | This skill should be used when the user says "avengers meeting", "team planning", "team st | stable | no |
| `budget-manager` | "Řízení token budgetu napříč LG13 instancemi. Instance s touto rolí čte aktuální spotřebu, | stable | yes |
| `budget-watchdog` | Proactive token budget monitoring. Watches weekly/session limits AND GitHub Actions bot ru | stable | yes |
| `chat-reply` | Use when Tom asks for a reply via cockpit chat / Jarvis v2 chat, or when an instance shoul | stable | no |
| `chatgpt-ask` | "Posle otazku ChatGPT a ziska odpoved zpet jako LG13 atom. Pouzij kdyz instance potrebuje  | stable | yes |
| `chatgpt-find` | "Vyhledá vlákna v ChatGPT historii přes CDP + Playwright search form. Vrátí seznam threadů | stable | yes |
| `chatgpt-force-read` | "Prinuti TM (Tampermonkey) aby precetl a ingestoval ChatGPT vlakno — naviguje Edge na thre | stable | no |
| `chatgpt-search` | "Vyhledá text nebo konverzaci v ChatGPT chatech přes vyhledávání v sidebaru nebo přes Play | stable | yes |
| `chatgpt-send` | "Posle zpravu do ChatGPT vlakna pres Playwright CDP — ovlada Edge prohlizec a zapise zprav | stable | yes |
| `checkpoint` | > | stable | no |
| `clipboard-chat` | "Use when running or continuing block-by-block ChatGPT review of F39; or when user says '- | stable | no |
| `cockpit` | This skill should be used when the user asks to "show cockpit", "operation board", "status | stable | no |
| `comm-legal` | Use when checking ISDS and email communication status for sp. zn. 0 P 29/2026, scanning fo | stable | no |
| `compact-check` | "Soft/Hard compact range checker. Vrátí zone (green/soft/hard/over) + action + recommendat | stable | yes |
| `consistency-check` | Use when a legal filing document may have stale dates, wrong day counts, or paragraph inco | stable | yes |
| `cti-cele` | "Přečte celý long soubor (ChatGPT export, JSON, TXT, MD) v iteracích a extrahuje diamonds/ | stable | yes |
| `deep-read` | Systematické pomalé čtení VŠECH kanálů (issues + komentáře, ChatGPT exporty zpráva po zprá | stable | no |
| `deep-read-full` | Spustí deep_read --full-read pro aktuální instanci. Čte plný text nových zpráv od cursoru  | stable | yes |
| `deferred-plans` | "Uloží nedokončený nebo odložený plán do gitu, aby ho příští session mohla zvednout. Trigg | stable | yes |
| `diamond-pick` |  | stable | no |
| `diamond-sentry` | "Use when scanning for key insights (diamonds) from conversations, atoms, or documents. Au | stable | yes |
| `diamond-to-matrix` | "Převede diamonds.json (z diamond-sentry nebo diamond-pick) na prioritizovanou CHANGE_MATR | stable | yes |
| `dnd` | Use when you need to focus without interruptions — suspends blocker questions for a set ti | stable | no |
| `doc-polish` | "Spustí filing pipeline OD PROSTŘEDKA — re-run analýz jen na problémech z předchozího kola | stable | yes |
| `edge-check` | "Edge-to-autocompact zone check. Spočítá zone (green/yellow/orange/red) + action + turns_r | stable | yes |
| `email-read` | Use when the user wants to read, search, or check emails from seznam.cz or Outlook. Trigge | stable | no |
| `file-catalog-search` | Use when searching for a file by name or keyword anywhere on the system. Searches a pre-bu | stable | yes |
| `filing-pipeline` | "Kompletni pipeline pro pripravu pravniho podani. Phase 1 = Build (konsolidace, struktura, | stable | no |
| `ftp` | FTP upload/download/list na ftpx.forpsi.com (luky.ai-domy.cz). Trigger: "/ftp upload", "/f | stable | no |
| `git-tmonkey-search` | "Search v L:/GitHub/lg13-tampermonkey/ repo (userscripts) přes gh CLI + Grep fallback. Tri | stable | yes |
| `github-actions-if-yaml` | Use when writing GitHub Actions job or step `if:` conditions with multiple expressions joi | stable | no |
| `heartbeat` | Keep-alive ping-pong loop + keep-awake clause. Triggers: 'heartbeat', 'keep awake', 'stay  | stable | yes |
| `i-can-hear-u` |  | stable | no |
| `isds` | > | stable | no |
| `isds-ship-with-capsule` | | | stable | no |
| `issue-sync` | This skill should be used when the user asks to "sync issues", "read issues", "issue diges | stable | no |
| `judi-sentry` | Use when searching for relevant Czech court judgments (ÚS/NS), linking diamond findings to | stable | no |
| `lare` | > | stable | no |
| `lazy_boy` | Alias for atom-read-all. Invoke when any instance skips atoms/wake events without reading  | stable | yes |
| `legal-daily-brief` |  | stable | no |
| `legal-total-analysis` | Lean meta-skill pre-flight audit DÁVKY právního podání před F1X.4 capsule build a ISDS ode | stable | no |
| `lg13-end` | "Ukončení session. Alias pro restart. Trigger: 'session end', 'konec session', 'ukonči ses | stable | yes |
| `lg13-init` | "Inicializace session — načte stav, přečte frontu, tmonkey, pl_stats, vygeneruje briefing. | stable | yes |
| `lg13-save` | "Průběžné uložení stavu session. Alias pro save-min. Trigger: 'save', 'ulož stav', 'checkp | stable | yes |
| `listen-to-the-music` |  | stable | no |
| `load-from-store` | "Načte session plán/memory z MySQL (přes db_query) nebo git fallback. Triggery: load from  | stable | yes |
| `locks-workflow` | > | stable | no |
| `mysql` | MySQL dotaz přes luky.ai-domy.cz/api/db_proxy.php. Trigger: "/mysql q: SELECT ...", "/mysq | stable | no |
| `ocr-git` | "OCR pipeline pro court/AT/OSPOD evidence — scan + index + search. Wrapper kolem legal_ocr | stable | yes |
| `ping-pong` | "LG13 cowork file-based komunikacni protokol pro inter-instance dialog (legal ↔ strat ↔ co | stable | yes |
| `pipeline` | "Filing pipeline pro soudni podani. Mody: 'pipeline complete' (ph1→ph3), 'pipeline resume  | stable | no |
| `plan-to-git` | Generates commented multi-step plan as GitHub issue for ChatGPT guided session. Templates  | stable | yes |
| `pre-ship-external-prompts` |  | stable | no |
| `prtsc` | "Podiva se na posledni screenshoty z OneDrive Screenshots slozky a precte jejich obsah pom | stable | no |
| `rag-search` | "Search indexed knowledge base (FTS5 sandbox) přes ctx_search MCP. Token-efficient retriev | stable | yes |
| `rain` | Diagnóza + oprava toku atomů z TM ingesta do monitor-arm instancí. Triggery: 'rain', 'nete | stable | yes |
| `restart` | "Session transition: plan-to-store → remember → clear → (nové okno) remember from MySQL →  | stable | yes |
| `rocket-launcher` |  | stable | no |
| `rr` | Use when you need a quick status snapshot — current task, token budget, blockers, ping-pon | stable | no |
| `rt` |  | stable | no |
| `rtg` |  | stable | no |
| `rts` |  | stable | no |
| `save-min` | "Token-min save (3 kroky): queue --done + STAV append + save_checkpoint + edge calc. NIKDY | stable | yes |
| `save-to-store` | "Uloží aktuální session plán/memory do MySQL (přes db_query) + git backup. Triggery: save  | stable | yes |
| `self-context-slim-update` | "Use when context usage >50%, memory files bloated or duplicated, index overhead growing,  | stable | no |
| `session-bootstrap-vnext` | DEPRECATED — replaced by super-start. Use /lg13-skills:super-start instead. | stable | no |
| `skill-creator` | Creates a new skill from template + git commit. Triggers: 'skill creator', 'new skill', 'c | stable | yes |
| `skill-picker` | Use when the user asks "which skill should I use?", "what skill for X?", "help me pick a s | stable | no |
| `skills-list` | Use when you need to see all available skills as a formatted text table. Shows skill name, | stable | no |
| `skills-manual` | Use when you need detailed documentation for a specific skill (with skill name as argument | stable | no |
| `slack-listen` | "Persistentní Slack listener — čte #lg13 (C0B3X5XC0JU), parsuje WAKE:<inst>:<msg> signály, | stable | yes |
| `sr` | > | stable | no |
| `strat-end` | "Strat session end. Alias pro restart. Trigger: 'konec', 'zavíráme', 'strat end', 'ukonči  | stable | yes |
| `strat-init` | "Strat session init — tmonkey, fronta, pl_stats, failed tasky, t002 dohled, daily briefing | stable | yes |
| `strat-save` | "Strat session save — checkpoint. Alias pro save-min (strat varianta). Trigger: 'save', 'u | stable | yes |
| `super-start` | Use when starting a new full cowork session — arms all channels, reads all inboxes, sets g | stable | no |
| `team-launcher` | > | stable | no |
| `team-speak` | Use when Tom types a message that should be forwarded to all active ping-pong instances si | stable | no |
| `terminator` | Goal-list executor from git issue. Iterates goals, time-limited questions for blockers, co | stable | yes |
| `thread-harvest` | This skill should be used when the user says "přečti vlákna", "co leží nevykonáno", "projd | stable | no |
| `tmonkey` | "Process fresh ChatGPT tmonkey exports — read inbox, identify Tom's requests [Ty:], route  | stable | yes |
| `tmonkey-arm` | "Arm Monitor watcher na <inst>_stack.jsonl mtime change → notification → wake instance pro | stable | yes |
| `tmonkey-bot` |  | stable | no |
| `tmonkey-diag` | "Diagnostika tmonkey atom flow health — pl/stats, atom_lookup, dispatcher routing, kde se  | stable | yes |
| `tmonkey-listen` | "Persistentní příjem atomů — instance může normálně pracovat, každá nová zpráva ji probudí | stable | yes |
| `tmonkey-monitor` | "Zapni zvonění — arm Monitor na tmonkey_arm.py, každý nový atom okamžitě probudí instanci. | stable | yes |
| `tmonkey-web` | "Open Chrome, navigate to ChatGPT LG13 project, open recent conversations in sequence so T | stable | no |
| `token-limit-read` | "Read current Claude usage (session % / week % / plan tier) z TM script ingested data. Tok | stable | yes |
| `tom-notify` | This skill should be used when any instance needs to notify Tom urgently, send him a quest | stable | no |
| `tool-picker` | "Decision tree: který tool kdy. Save-the-tokens hierarchie 1-7 + anti-patterns. Trigger: ' | stable | yes |
| `uklid-coder` | Use for coder's regular maintenance duties — skills registry update, queue check, heartbea | stable | no |
| `unlock-gate` | > | stable | no |
| `vlastnak` | Use when an instance needs to write its own session goal prompt — a first-person startup p | stable | no |
| `web-up` |  | stable | no |
| `work-mode` | "Self-paced heartbeat loop — team nebo solo work mode. Bootstrap: Monitor arm + ScheduleWa | stable | yes |
| `zero-tokens` | "Zero-token execution stack: Python, Git, Ollama, context-mode. Kdy co použít, konkrétní s | stable | yes |

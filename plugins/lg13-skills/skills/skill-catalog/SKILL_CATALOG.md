# SKILL CATALOG (194 skills)

Generovano `skill_catalog.py build`. Vyber k ukolu: `skill_catalog.py pick "ukol"`.

## dev-proces (20)

| skill | zdroj | kdy |
|---|---|---|
| a11y-debugging | claude-plugins-official/chrome-devtools-mcp | Uses Chrome DevTools MCP for accessibility (a11y) debugging and auditing based on web.dev guidelines. Use when... |
| content-strategy | claude-plugins-official/searchfit-seo | Develop a content strategy for SEO and organic growth. Use when the user asks to "plan content", "content stra... |
| debug-optimize-lcp | claude-plugins-official/chrome-devtools-mcp | Guides debugging and optimizing Largest Contentful Paint (LCP) using Chrome DevTools MCP tools. Use this skill... |
| deferred-plans | lg13-skills | Uloží nedokončený nebo odložený plán do gitu, aby ho příští session mohla zvednout. Trigger: 'ulož plán', 'odl... |
| executing-plans | claude-plugins-official/superpowers | Use when you have a written implementation plan to execute in a separate session with review checkpoints |
| finishing-a-development-branch | claude-plugins-official/superpowers | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides... |
| memory-leak-debugging | claude-plugins-official/chrome-devtools-mcp | Diagnoses and resolves memory leaks in JavaScript/Node.js applications. Use when a user reports high memory us... |
| plan-to-git | lg13-skills | Generates commented multi-step plan as GitHub issue for ChatGPT guided session. Templates for research, review... |
| playground | claude-plugins-official/playground | Creates interactive HTML playgrounds — self-contained single-file explorers that let users configure something... |
| receiving-code-review | claude-plugins-official/superpowers | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear... |
| requesting-code-review | claude-plugins-official/superpowers | Use when completing tasks, implementing major features, or before merging to verify work meets requirements |
| skill-creator | lg13-skills | Creates a new skill from template + git commit. Triggers: 'skill creator', 'new skill', 'create skill', '/skil... |
| subagent-driven-development | claude-plugins-official/superpowers | Use when executing implementation plans with independent tasks in the current session |
| systematic-debugging | claude-plugins-official/superpowers | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| test-driven-development | claude-plugins-official/superpowers | Use when implementing any feature or bugfix, before writing implementation code |
| using-git-worktrees | claude-plugins-official/superpowers | Use when starting feature work that needs isolation from current workspace or before executing implementation ... |
| using-superpowers | claude-plugins-official/superpowers | Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before... |
| web-up | lg13-skills | Sestaví review web (HTML + ZIP + PDF přílohy) z aktuálního F-cyklu a nasadí ho FTP na `luky.ai-domy.cz/web_up/... |
| writing-plans | claude-plugins-official/superpowers | Use when you have a spec or requirements for a multi-step task, before touching code |
| writing-skills | claude-plugins-official/superpowers | Use when creating new skills, editing existing skills, or verifying skills work before deployment |

## infra (12)

| skill | zdroj | kdy |
|---|---|---|
| chrome-devtools | claude-plugins-official/chrome-devtools-mcp | Uses Chrome DevTools via MCP for efficient debugging, troubleshooting and browser automation. Use when debuggi... |
| chrome-devtools-cli | claude-plugins-official/chrome-devtools-mcp | Use this skill to write shell scripts or run shell commands to automate tasks in the browser or otherwise use ... |
| context-mode | context-mode/context-mode | / Use context-mode tools (ctx_execute, ctx_execute_file) instead of Bash/cat when processing large outputs. Tr... |
| ctx-doctor | context-mode/context-mode | / Run context-mode diagnostics. Checks runtimes, hooks, FTS5, plugin registration, npm and marketplace version... |
| ctx-index | context-mode/context-mode | / Index a local file or directory into context-mode's persistent FTS5 knowledge base so future ctx_search call... |
| ctx-insight | context-mode/context-mode | / Open the context-mode Insight dashboard in your default browser. Insight is the hosted analytics layer for A... |
| ctx-purge | context-mode/context-mode | / Purge the context-mode knowledge base. Permanently deletes all indexed content and resets session stats. Thi... |
| ctx-stats | context-mode/context-mode | / Show how much context window context-mode saved this session. Displays token consumption, context savings ra... |
| ctx-upgrade | context-mode/context-mode | / Update context-mode from GitHub and fix hooks/settings. Pulls latest, builds, installs, updates npm global, ... |
| ctx-usage-report | lg13-skills | Use when a larger task has just finished (new F-document version, audit, render, commit) and its token cost mu... |
| ftp | lg13-skills | FTP upload/download/list na ftpx.forpsi.com (luky.ai-domy.cz). Trigger: "/ftp upload", "/ftp ls", "/ftp downlo... |
| mysql | lg13-skills | MySQL dotaz přes luky.ai-domy.cz/api/db_proxy.php. Trigger: "/mysql q: SELECT ...", "/mysql q: path/to/query.s... |

## komunikace (33)

| skill | zdroj | kdy |
|---|---|---|
| ai-visibility | claude-plugins-official/searchfit-seo | Analyze and improve how a brand appears in AI-generated responses (ChatGPT, Claude, Gemini, Perplexity). Use w... |
| atom-read-all | lg13-skills | Use when receiving any wake event about atoms — enforces reading atom content before any routing decision. Pre... |
| atom-search | lg13-skills | Vyhledá atomy z konkrétní ChatGPT konverzace (conv_id) nebo dle instance/time window, seřadí ASC dle timestamp... |
| avengers | lg13-skills | Team terminator — multiple instances collaborate on shared goal list. Director dispatches, workers execute, sy... |
| avengers-meeting | lg13-skills | This skill should be used when the user says "avengers meeting", "team planning", "team standup", "team plan",... |
| change-discipline | user | Use when receiving a stream of incremental edits/ideas for the same document (pasted ChatGPT excerpts, dictate... |
| chat-reply | lg13-skills | Use when Tom asks for a reply via cockpit chat / Jarvis v2 chat, or when an instance should send a message bac... |
| chatgpt-ask | lg13-skills | Posle otazku ChatGPT a ziska odpoved zpet jako LG13 atom. Pouzij kdyz instance potrebuje second-opinion, revie... |
| chatgpt-attach | lg13-skills | Use when the user wants to SEND FILES (přílohy, PDF, md, obrázek) into a ChatGPT thread or upload a file into ... |
| chatgpt-find | lg13-skills | Vyhledá vlákna v ChatGPT historii OFFLINE nad ChatGPT_export/*.json (titul, URL, conv_id, volitelně i obsah zp... |
| chatgpt-force-read | lg13-skills | Prinuti TM (Tampermonkey) aby precetl a ingestoval ChatGPT vlakno — naviguje Edge na thread URL pres Playwrigh... |
| chatgpt-search | lg13-skills | Vyhledá text nebo konverzaci v ChatGPT chatech OFFLINE v lokálním exportu (cgpt_find.py, wave search). Bez Edg... |
| chatgpt-send | lg13-skills | Use when the user wants to SEND a message into a specific ChatGPT thread (chatgpt-send, /chatgpt-send, 'posli ... |
| cockpit | lg13-skills | This skill should be used when the user asks to "show cockpit", "operation board", "status report", "/cockpit"... |
| email-read | lg13-skills | Use when the user wants to read, search, or check emails from seznam.cz or Outlook. Triggers on "zkontroluj ma... |
| export-chatgpt-thread | user | Use when a ChatGPT thread must be exported to L:/GitHub/legal-ship-2026/ChatGPT_export via Claude in Chrome (p... |
| gpt-bridge | lg13-skills | Use when Claude needs to ask an existing ChatGPT thread a question and continue a multi-round review (advisory... |
| heartbeat | lg13-skills | Keep-alive ping-pong loop + keep-awake clause. Triggers: 'heartbeat', 'keep awake', 'stay alive', 'stuj na noh... |
| job-queue | user | Use when a CLI instance (legal, coder, strat) must hand work to another worker or to ChatGPT in the browser an... |
| keyword-clustering | claude-plugins-official/searchfit-seo | Cluster and organize keywords into topical groups for SEO. Use when the user asks to "cluster keywords", "grou... |
| lazy_boy | lg13-skills | Alias for atom-read-all. Invoke when any instance skips atoms/wake events without reading content. Enforces "e... |
| ping-pong | lg13-skills | LG13 cowork file-based komunikacni protokol pro inter-instance dialog (legal ↔ strat ↔ coder ↔ ...). Atomic JS... |
| pre-ship-external-prompts | lg13-skills | Generuje prompty pro **external pre-ship analýzu** od CDC (Claude Desktop Cowork) a ChatGPT. |
| slack-listen | lg13-skills | Persistentní Slack listener — čte #lg13 (C0B3X5XC0JU), parsuje WAKE:<inst>:<msg> signály, routuje do ping-pong... |
| slack-messaging | claude-plugins-official/slack | Guidance for composing well-formatted, effective Slack messages using standard markdown |
| slack-search | claude-plugins-official/slack | Guidance for effectively searching Slack to find messages, files, channels, and people |
| super-start | lg13-skills | Use when starting a new full cowork session — arms all channels, reads all inboxes, sets goal, activates super... |
| team-launcher | lg13-skills | > Spouští jednu nebo více LG13 instancí autonomně — headless nebo s oknem — bez Tomovy přítomnosti. Použij VŽD... |
| team-speak | lg13-skills | Use when Tom types a message that should be forwarded to all active ping-pong instances simultaneously — broad... |
| tom-actual | user | Use whenever a new F-document version is created/shipped in legal-ship-2026 (F62-F69 active wave), or when Tom... |
| tom-notify | lg13-skills | This skill should be used when any instance needs to notify Tom urgently, send him a question, escalate a bloc... |
| uklid-coder | lg13-skills | Use for coder's regular maintenance duties — skills registry update, queue check, heartbeat, git repo sync, fi... |
| work-mode | lg13-skills | Self-paced heartbeat loop — team nebo solo work mode. Bootstrap: Monitor arm + ScheduleWakeup fallback + read-... |

## legal-filing (52)

| skill | zdroj | kdy |
|---|---|---|
| VAM | lg13-skills | Use when analyzing document visual attention flow, scoring scan-readability, identifying dead zones, or optimi... |
| action-telemetry | lg13-skills | Log akci + report top actions + share přes ping_pong. Tom 2026-05-10 cost optimization pro coder/strat/legal. |
| ai-cleaning | user | Use when a text or file is about to leave the working folder (court filing, letter, attachment, exported chat ... |
| attachment-pipeline | lg13-skills | Orchestrator pro přílohy soudního podání — volá attachment-score, deferred-plans, filing-pipeline. Triggers: '... |
| attachment-score | lg13-skills | Ohodnotí přílohy soudního podání (PDF/PNG) dle síly důkazu, relevance a stavu. Výstup: scoring tabulka KEEP/DR... |
| attorney-assist | claude-plugins-official/legalzoom | Connects the user with a LegalZoom attorney for legal consultation. Use when a user asks about attorneys, lawy... |
| briefing-legal | user | Use when Tom wants a status overview of not-yet-sent court filings (F-documents still in progress — e.g. F41/F... |
| bumping-f-filing-version | user | Use when an F-numbered filing in legal-ship-2026 (F62, F64, F66...) needs a new version after a ChatGPT review... |
| cge-legal-digest | lg13-skills | Zpracuje ChatGPT_export vlákno (podle conv_id, napříč všemi jeho re-exporty) do rozsahu/přírůstku zpráv, otagu... |
| cge-search | lg13-skills | Fulltextové vyhledávání napříč ChatGPT JSON exporty (ChatGPT_export/*.json, 500+ souborů) a atom daily store (... |
| chatgpt-legal-discussion-review | user | Use when Tom wants Claude legal to discuss or review a filing (F-document) directly with the ChatGPT reading t... |
| clipboard-chat | lg13-skills | Use when running or continuing block-by-block ChatGPT review of the CURRENT filing (any F-cycle, not just F39/... |
| comm-legal | lg13-skills | Use when checking ISDS and email communication status for sp. zn. 0 P 29/2026, scanning for new documents, run... |
| consistency-check | lg13-skills | Use when a legal filing document may have stale dates, wrong day counts, or paragraph inconsistencies before r... |
| cti-cele | lg13-skills | Přečte celý long soubor (ChatGPT export, JSON, TXT, MD) v iteracích a extrahuje diamonds/legal facts/CHANGE_MA... |
| deferred-args-sweep | lg13-skills | Use when a ChatGPT thread (CGE export) may contain arguments that were deferred to another filing ('patří do F... |
| diamond-pick | lg13-skills | Automatizuje to co Tom dělá ručně v ChatGPT: čte drafty, exporty, poznámky → |
| diamond-sentry | lg13-skills | Use when scanning for key insights (diamonds) from conversations, atoms, or documents. Auto-detects current in... |
| diamond-to-matrix | lg13-skills | Převede diamonds.json (z diamond-sentry nebo diamond-pick) na prioritizovanou CHANGE_MATRIX. Missing pipeline ... |
| digest-to-filing | user | Use when cge_legal_digest.py (or a direct diamond_sentry.py run) has produced a batch of candidate legal argum... |
| dnd | lg13-skills | Use when you need to focus without interruptions — suspends blocker questions for a set time, converts them to... |
| doc-polish | lg13-skills | Spustí filing pipeline OD PROSTŘEDKA — re-run analýz jen na problémech z předchozího kola + kompletní test sui... |
| f-cycle-bootstrap | user | Use when starting a brand-new F-numbered filing (Fxx) in legal-ship-2026 — creates the folder, subfolders, met... |
| filing-pipeline | lg13-skills | Kompletni pipeline pro pripravu pravniho podani. Phase 1 = Build (konsolidace, struktura, zestihleni, podpurne... |
| go-on | user | Use when asked to continue, finish or move an already existing filing draft forward ("pokračuj", "go on", "dod... |
| image-ocr-catalog | user | Use when a folder of photographed documents (HEIC/JPG/PNG, e.g. exekuce spis, OSPOD spis, scanned pages) needs... |
| isds | lg13-skills | > ISDS datová schránka — použij tento skill pokaždé, když má instance odeslat DS, zobrazit přijaté zprávy, hle... |
| isds-ship-with-capsule | lg13-skills | / Řídí celý proces odeslání soudního dokumentu přes ISDS pro LG13 instanci t002. Zahrnuje: fyzická verifikace ... |
| jarvis | user | Use when an F-document (court filing under legal-ship-2026) gets a new version and Tom needs to review it chap... |
| judi-sentry | lg13-skills | Use when searching for relevant Czech court judgments (ÚS/NS), linking diamond findings to specific cases, or ... |
| lare | lg13-skills | > Legal-specific Argument Ranking Engine. Hodnotí právní argumenty 17-sloupcovým scoringem (síla, bezpečnost, ... |
| law-library | user | Use when drafting/auditing a Czech court filing and you need the verbatim wording of a § (paragraf) or to conf... |
| legal-daily-brief | lg13-skills | **Trigger:** "spusť daily brief", "legal brief", "/legal-daily-brief", "denní přehled" |
| legal-terminal-comm | user | Přímá strat ↔ Lik (legal cowork) komunikace přes task queue + soubory, když Lik běží v `claude` CLI terminálu ... |
| legal-total-analysis | lg13-skills | Lean meta-skill pre-flight audit DÁVKY právního podání před F1X.4 capsule build a ISDS odesláním. Generuje GO/... |
| locks-workflow | lg13-skills | > Řídí 5-locks schvalovací workflow pro soudní a formální podání v systému LG13. Verze 3 (Tom directive 2026-0... |
| ocr-git | lg13-skills | OCR pipeline pro court/AT/OSPOD evidence — scan + index + search. Wrapper kolem legal_ocr_catalogue.py. Trigge... |
| oq | user | Use when you have a question for Tom that blocks further work but isn't worth an inline interrupt right now — ... |
| pipeline | lg13-skills | Filing pipeline pro soudni podani. Mody: 'pipeline complete' (ph1→ph3), 'pipeline resume phN' (phN→ph3). Freez... |
| preparing-chatgpt-attachment | user | Use when Tom wants an exhibit (přepis WhatsApp, chronology, K-card) produced or extended in ChatGPT in the sam... |
| prtsc | lg13-skills | Podiva se na posledni screenshoty z OneDrive Screenshots slozky a precte jejich obsah pomoci token-free OCR (W... |
| rocket-launcher | lg13-skills | Spravuje ISDS rocket launcher engine (`isds_rocket_<FC>.py`) pro aktuální F-cyklus, generovaný |
| rr | lg13-skills | Use when you need a quick status snapshot — current task, token budget, blockers, ping-pong state. Run before ... |
| shopify-liquid-themes | claude-plugins-official/liquid-skills | Generate Shopify Liquid theme code (sections, blocks, snippets) with correct schema JSON, LiquidDoc headers, t... |
| slim-diet | user | Use when a legal filing has grown long through iterative additions (repeated arguments, restated grounds, bulk... |
| spis-ocr-catalog | user | Use when a folder of phone-photographed physical case-file pages (soud_spis, ospod_spis, exekuce spis — hundre... |
| terminator | lg13-skills | Goal-list executor from git issue. Iterates goals, time-limited questions for blockers, continues without Tom.... |
| total-analysis-all-in-one | user | / Kompletní právní analýza českého soudního podání — návrh PR/PO, žaloba, doplnění, vyjádření. Spusť VŽDY když... |
| unlock-all-locks | user | **Trigger:** "unlock locks", "projdi locky", "spusť locky", "/unlock-all-locks" |
| unlock-gate | lg13-skills | > Multi-step unlock workflow pro soudní podání F-cyklus. Spustí automated checks (LOCK 1–4) pro jeden soubor, ... |
| vertical-analysis | user | Use when a filing has many versions (F62.1 → F62.100), before freezing or after heavy cuts and restructures, w... |
| writing-doc | lg13-skills | Use when authoring or editing Czech court filings (návrhy, odvolání, doplnění, podněty, odvolání EXE) — covers... |

## ostatni (18)

| skill | zdroj | kdy |
|---|---|---|
| claude-md-improver | claude-plugins-official/claude-md-management | Audit and improve CLAUDE.md files in repositories. Use when user asks to check, audit, update, improve, or fix... |
| content-brief | claude-plugins-official/searchfit-seo | Generate a detailed content brief for a specific article or page. Use when the user asks to "create a content ... |
| content-translation | claude-plugins-official/searchfit-seo | Translate and localize website content for international SEO. Use when the user asks to "translate content", "... |
| ddd | user | Řeší opakovaný problém z této session: kdykoli se posune datum podpisu/podání, každý den-počet v textu (159→16... |
| dispatching-parallel-agents | claude-plugins-official/superpowers | Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies |
| github-actions-if-yaml | lg13-skills | Use when writing GitHub Actions job or step `if:` conditions with multiple expressions joined by // or && — es... |
| internal-linking | claude-plugins-official/searchfit-seo | Analyze and improve internal linking strategy for a website. Use when the user asks about "internal links", "l... |
| liquid-theme-a11y | claude-plugins-official/liquid-skills | Implement WCAG 2.2 accessibility patterns in Shopify Liquid themes. Covers e-commerce-specific components incl... |
| on-page-seo | claude-plugins-official/searchfit-seo | Optimize a specific page for on-page SEO. Use when the user asks to "optimize this page", "improve SEO for thi... |
| postiz | claude-plugins-official/postiz | ../../SKILL.md |
| schema-markup | claude-plugins-official/searchfit-seo | Generate JSON-LD structured data / schema markup for web pages. Use when the user asks to "add schema", "gener... |
| self-context-slim-update | lg13-skills | Use when context usage >50%, memory files bloated or duplicated, index overhead growing, or preparing for majo... |
| skills-list | lg13-skills | Use when you need to see all available skills as a formatted text table. Shows skill name, namespace, and shor... |
| skills-manual | lg13-skills | Use when you need detailed documentation for a specific skill (with skill name as argument) or a short manual ... |
| stop-stupid-questions | lg13-skills | Use when about to stop and ask Tom a small question — "mám to commitnout?", "co přesně potřebuješ?", "chceš A ... |
| technical-seo | claude-plugins-official/searchfit-seo | Perform a technical SEO audit on a website or codebase. Use when the user asks for "technical SEO", "site spee... |
| verification-before-completion | claude-plugins-official/superpowers | Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires runn... |
| vlastnak | lg13-skills | Use when an instance needs to write its own session goal prompt — a first-person startup prompt with clear don... |

## session (26)

| skill | zdroj | kdy |
|---|---|---|
| autosave | lg13-skills | Use when context is filling up (edge-check says consider/over, 20+ % used) or Tom says 'autosave', 'ulož a com... |
| budget-manager | lg13-skills | Řízení token budgetu napříč LG13 instancemi. Instance s touto rolí čte aktuální spotřebu, alokuje kapacitu ost... |
| budget-pacer | user | Use to pace this instance's token consumption against the live 5-hour/7-day account usage limit, self-capping ... |
| budget-watchdog | lg13-skills | Proactive token budget monitoring. Watches weekly/session limits AND GitHub Actions bot runs, sends alerts, en... |
| checkpoint | lg13-skills | > Průběžný snapshot stavu session. Uloží plán do MySQL + git, zapíše handoff note, reportuje stav do Jarvis. V... |
| edge-check | lg13-skills | Use when deciding whether to save or let compaction happen: context fills up, footer/statusline shows ctx usag... |
| frontend-design | claude-plugins-official/frontend-design | Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the use... |
| lg13-init | lg13-skills | Inicializace session — načte stav, přečte frontu, tmonkey, pl_stats, vygeneruje briefing. Trigger: 'init', 'st... |
| liquid-theme-standards | claude-plugins-official/liquid-skills | CSS, JavaScript, and HTML coding standards for Shopify Liquid themes. Covers BEM naming inside stylesheet tags... |
| load-from-store | lg13-skills | Načte session plán/memory z MySQL (přes db_query) nebo git fallback. Triggery: load from store, remember from ... |
| low-food-slow-down | user | Use when token-limit-read shows usage on track to hit the Claude session/weekly limit before it resets — high ... |
| no-food-sleep | user | Use when a Claude session/token usage limit has been hit and a reset countdown is known — the wait is longer t... |
| remember | claude-plugins-official/remember | Save session state for clean continuation next session. |
| restart | lg13-skills | Session transition: plan-to-store → remember → clear → (nové okno) remember from MySQL → plan-from-store. Přec... |
| save-min | lg13-skills | Token-min save (3 kroky): queue --done + STAV append + save_checkpoint + edge calc. NIKDY /compact bez prior s... |
| save-to-store | lg13-skills | Uloží aktuální session plán/memory do MySQL (přes db_query) + git backup. Triggery: save my memory, save plan ... |
| session-bootstrap-vnext [DEPRECATED] | lg13-skills | DEPRECATED — replaced by super-start. Use /lg13-skills:super-start instead. |
| session-end | lg13-skills | Ukončení session. Alias pro restart. Trigger: 'session end', 'konec session', 'ukonči session', 'zavíráme', '/... |
| session-save | lg13-skills | Průběžné uložení stavu session. Alias pro save-min. Trigger: 'save', 'ulož stav', 'checkpoint', '/session-save... |
| sr | lg13-skills | > Kompletní session startup skill. Volej při: nové session, po /clear, po probuzení z idle, z launcheru. Prove... |
| strat-end | lg13-skills | Strat session end. Alias pro restart. Trigger: 'konec', 'zavíráme', 'strat end', 'ukonči strat session'. |
| strat-init | lg13-skills | Strat session init — tmonkey, fronta, pl_stats, failed tasky, t002 dohled, daily briefing. Trigger: 'init' v s... |
| strat-save | lg13-skills | Strat session save — checkpoint. Alias pro save-min (strat varianta). Trigger: 'save', 'ulož stav', 'checkpoin... |
| token-limit-read | lg13-skills | Read current Claude usage (session % / week % / plan tier) z TM script ingested data. Token-free read, žádný A... |
| troubleshooting | claude-plugins-official/chrome-devtools-mcp | Uses Chrome DevTools MCP and documentation to troubleshoot connection and target issues. Trigger this skill wh... |
| zero-tokens | lg13-skills | Zero-token execution stack: Python, Git, Ollama, context-mode. Kdy co použít, konkrétní snippety. Trigger: 'ze... |

## tm-ingest (14)

| skill | zdroj | kdy |
|---|---|---|
| brainstorming | claude-plugins-official/superpowers | You MUST use this before any creative work - creating features, building components, adding functionality, or ... |
| git-tmonkey-search | lg13-skills | Search v L:/GitHub/lg13-tampermonkey/ repo (userscripts) přes gh CLI + Grep fallback. Trigger: 'git tmonkey', ... |
| i-can-hear-u | lg13-skills | **This skill should be used when** the user asks `/i-can-hear-u`, "spust listener", "poslouchej vsechny kanaly... |
| lex-atomic-render | user | Use when adding or changing visual elements (petit box, evidence table, signature block, meta grid, headings) ... |
| listen-to-the-music | lg13-skills | `/i-can-hear-u` je širší startup skill (8 kroků: daemon+Monitor+CGE+CDC+issues+Jarvis+PRTSC+handoff sem) — jeh... |
| rag-search | lg13-skills | Search indexed knowledge base (FTS5 sandbox) přes ctx_search MCP. Token-efficient retrieval místo full-file Re... |
| rain | lg13-skills | Diagnóza + oprava toku atomů z TM ingesta do monitor-arm instancí. Triggery: 'rain', 'neteče', 'nepršelo', 'at... |
| tmonkey | lg13-skills | Process fresh ChatGPT tmonkey exports — read inbox, identify Tom's requests [Ty:], route to instances, archive... |
| tmonkey-arm | lg13-skills | Arm Monitor watcher na <inst>_stack.jsonl mtime change → notification → wake instance pro pickup. Bez polling,... |
| tmonkey-bot | lg13-skills | Use when: "tmonkey", "co přišlo z chatgpt", "pošli příkaz do chatgpt", "tmonkey bot", "tmonkey status" |
| tmonkey-diag | lg13-skills | Diagnostika tmonkey atom flow health — pl/stats, atom_lookup, dispatcher routing, kde se ztrácí APPROVED→DISPA... |
| tmonkey-listen | lg13-skills | Persistentní příjem atomů — instance může normálně pracovat, každá nová zpráva ji probudí okamžitě. Jako mobil... |
| tmonkey-monitor | lg13-skills | Zapni zvonění — arm Monitor na tmonkey_arm.py, každý nový atom okamžitě probudí instanci. Normálně = zvonění v... |
| tmonkey-web | lg13-skills | Open Chrome, navigate to ChatGPT LG13 project, open recent conversations in sequence so Tampermonkey capture s... |

## vyhledavani (19)

| skill | zdroj | kdy |
|---|---|---|
| autoresearch | lg13-skills | Use when you need autonomous iterative research or improvement — argument strengthening, CDC gate progression,... |
| big-file-read | user | Use when asked to read/analyze a huge single source (chat export JSON, log file, long transcript, big spreadsh... |
| broken-links | claude-plugins-official/searchfit-seo | Find and fix broken links on a website or in a codebase. Use when the user asks to "check broken links", "find... |
| case-search | user | Use when you need to find something in the legal case materials but don't know which of the 7+ domain-specific... |
| ctx-search | context-mode/context-mode | / Search context-mode's persistent FTS5 knowledge base for previously indexed local project content, documenta... |
| deep-read | lg13-skills | Systematické pomalé čtení VŠECH kanálů (issues + komentáře, ChatGPT exporty zpráva po zprávě) chronologicky in... |
| deep-read-full | lg13-skills | Spustí deep_read --full-read pro aktuální instanci. Čte plný text nových zpráv od cursoru (ne jen Haiku-filter... |
| file-catalog-search | lg13-skills | Use when searching for a file by name or keyword anywhere on the system. Searches a pre-built TREE catalog (22... |
| issue-sync | lg13-skills | This skill should be used when the user asks to "sync issues", "read issues", "issue digest", "co je nového na... |
| rt | lg13-skills | Spocita oba scores (RTG + RTS) a vyda spojeny report s ship-ready verdict. |
| rtg | lg13-skills | Vrati RTG score (Ready To Go = muze zacit submission workflow). Threshold > 0.95. |
| rts | lg13-skills | Vrati RTS score (Ready To Ship = muze zmacknout datovku). Threshold > 0.98. |
| self-control-read | user | Use when a new F-filing version was just created after a batch of changes and needs independent review before ... |
| seo-audit | claude-plugins-official/searchfit-seo | Run a comprehensive SEO audit on a website or codebase. Use when the user asks to "audit SEO", "check my site'... |
| seo-audit-refresh | user | Use when running a repeat SEO audit on a site that already has a prior audit report on disk — symptoms include... |
| skill-picker | lg13-skills | Use when the user asks "which skill should I use?", "what skill for X?", "help me pick a skill", "skill picker... |
| thread-harvest | lg13-skills | This skill should be used when the user says "přečti vlákna", "co leží nevykonáno", "projdi exporty", "harvest... |
| tool-picker | lg13-skills | Decision tree: který tool kdy. Save-the-tokens hierarchie 1-7 + anti-patterns. Trigger: 'co použít', 'tool', '... |
| watching-away-thread | user | Use when Tom has left the PC (idle 30+ min) and is writing from his phone into a ChatGPT thread, and new repli... |

## Problemy

- session-bootstrap-vnext (lg13-skills): deprecated

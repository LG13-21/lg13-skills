# CHANGELOG — LG13 Skill Library

Format: `## [date] — title`

---

## [2026-05-31] — add consistency-check + attachment-score + attachment-pipeline
- New skill `consistency-check`: automatický check dat/dní/§§ v MD dokumentu před renderem; TDD RED evidence z LOCK 1 F29 auditu (datum stale, 121→122 dní)

## [2026-05-31] — add attachment-score + attachment-pipeline
- New skill `attachment-score`: hodnotí PDF/PNG přílohy soudního podání dle síly důkazu + relevance (scoring KEEP/DROP/CONSOLIDATE/DEFER)
- New skill `attachment-pipeline`: orchestrator volající attachment-score → deferred-plans → filing-pipeline; pokrývá celou pipeline příloh

---

## [2026-05-28] — add deep-read-full
- New skill `deep-read-full`: spustí deep_read --full-read pro aktuální instanci; čte plný text nových zpráv (ne jen diamonds)

---

## [2026-05-20] — Initial release

- Bulk import of 41 existing skills from local marketplace (previously unversioned)
- Established git repository `LG13-21/lg13-skills`
- Added REGISTRY.md, CHANGELOG.md, README.md
- Added skill templates (basic, pingpong, monitor, meta)
- **New skills:** heartbeat, terminator, avengers, skill-creator, plan-to-git

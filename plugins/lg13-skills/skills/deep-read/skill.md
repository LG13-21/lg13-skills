---
name: deep-read
description: Systematické pomalé čtení VŠECH kanálů (issues + komentáře, ChatGPT exporty zpráva po zprávě) chronologicky interleaved. Každá instance čte vše — relevantní označí ✅, zbytek ⬜ skip, zlaté rady 💎. Deduplikace přes automatický cursor per instance. Role a keywords jsou v editovatelném deep_read_config.json, kotvy se ukládají automaticky. Výstup = checklist + čtenářský deník. Spuštění: python L:/GitHub/lg13-coder/agent/skills/deep_read.py --instance coder. Trigger: "deep-read", "precti vse", "cti dusledne", "co jsem zamekal", "zlate rady z chatgpt", "vytahni rady z chatgpt", "co tam lezi neprecteho".
version: 1.1.0
---

# deep-read

Spustí: `python L:/GitHub/lg13-coder/agent/skills/deep_read.py --instance <name>`

Config (editovatelný): `L:/LG13/runtime/state/deep_read_config.json`
State (automatický): `L:/LG13/runtime/state/deep_read_state.json`
Filter lib: `agent/skills/deep_read_filter.py`

Vrací: checklist ✅/⬜/💎 + čtenářský deník per instance.

---
name: tmonkey-web
description: "Open Chrome, navigate to ChatGPT LG13 project, open recent conversations in sequence so Tampermonkey capture script saves them to L:\\LG13\\inbox\\chatgpt\\. Trigger: 'tmonkey web', 'tmonkey chrome', 'scrape chatgpt', 'zachyť chatgpt', 'otevři chatgpt a stáhni'. Use from any cowork instance with Chrome MCP access (strat, main, coder, web)."
---

# Tmonkey Web — Chrome-driven ChatGPT Capture

Automatizuje otevírání ChatGPT konverzací v projektu LG13 tak, aby uživatelský Tampermonkey skript (`suno_to_lg13` / tmonkey capturer) zachytil obsah a uložil do `L:\LG13\inbox\chatgpt\YYYY-MM\DD\`.

Tampermonkey skript běží v Chrome, ne v této instanci — my jen otevřeme stránku a počkáme. Skript sám detekuje konverzaci a pošle obsah na pl_server (`/pl/chatgpt/ingest`) → server zapíše soubor.

## Kdy použít

- Tom řekne "tmonkey web" / "stáhni poslední konverzace z chatgpt"
- Potřebuješ zachytit N nejnovějších konverzací (default: 2)
- Při session init, pokud tmonkey inbox nemá aktuální věci z dnešního dne

## Prerekvizity

- Chrome běží, MCP `mcp__claude-in-chrome__*` tooly dostupné (načíst přes ToolSearch)
- Tampermonkey extension aktivní s capture skriptem
- pl_server běží na `localhost:8790`
- Přístup na `L:\LG13\inbox\chatgpt\`

## Postup

### 1. Načti Chrome MCP tooly

```
ToolSearch "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__find,mcp__claude-in-chrome__computer"
```

### 2. Otevři tab group a projekt

```
tabs_context_mcp(createIfEmpty: true)  # získá tabId nebo vytvoří nový
navigate(tabId, "https://chatgpt.com/g/g-p-69880e4a53548191a37df1a2103f9f7f-luky-s-game-13/project")
wait 3s
```

**Fixní project URL** (Luky's Game 13):
`https://chatgpt.com/g/g-p-69880e4a53548191a37df1a2103f9f7f-luky-s-game-13/project`

Pokud se redirectne na `chatgpt.com/` s varováním "project not found" → špatný účet. Ověř sidebar, najdi správný link: `find("Luky's Game 13 project sidebar link")`.

### 3. Identifikuj N nejnovějších konverzací

```
find("list of conversations in project, with dates")
```

Konverzace jsou seřazené sestupně dle data (Apr 14 nahoře). Default N=2, ale Tom může říct jinak.

Pro každou konverzaci vyčti:
- Titulek
- Relativní datum (Apr 14, Apr 13, ...)
- Href `/g/g-p-.../c/{conv_id}`

### 4. Snapshot před-stavu inboxu

```bash
ls -la "L:/LG13/inbox/chatgpt/YYYY-MM/DD/"
```

Poznamenej si filenames + velikosti. Po capture porovnáš.

### 5. Otevři každou konverzaci a počkej

Pro každý `conv_id` v pořadí:

```
navigate(tabId, "https://chatgpt.com/g/g-p-69880e4a53548191a37df1a2103f9f7f-luky-s-game-13/c/{conv_id}")
wait 10s   # Tampermonkey potřebuje čas: načíst stránku, proskenovat DOM, poslat POST
```

**Důležité:**
- Mezi konverzacemi se vrať na project listing (`/project`) a znovu klikni, nebo naviguj přímo — obě fungují
- `wait 10s` je minimum, velké konverzace (80KB+) mohou potřebovat více
- Pokud tab zmizí / 404 → Chrome session ztracena, `tabs_context_mcp` znovu

### 6. Ověř capture

```bash
ls -la "L:/LG13/inbox/chatgpt/YYYY-MM/DD/"
```

Pro každou otevřenou konverzaci:
- Soubor existuje? ✓
- `mtime` je aktuální (za poslední ~1 min)? ✓
- Velikost je > 0?  ✓

Filename pattern: `{slug(project_name)}_{slug(conv_title)}.txt`
- Příklad: `luky_s_game_13_no_n_m_ra_jako_realita.txt`
- Slugifikace: ASCII lowercase, mezery → `_`, non-ASCII → znak zahozen nebo nahrazen (viz Tampermonkey skript)

### 7. Zavři tab (volitelné)

```
navigate(tabId, "chrome://newtab")
```

Podle `feedback_close_browser_tabs.md` — po použití zavřít/navigovat na blank.

## Chybové stavy

| Problém | Řešení |
|---------|--------|
| "Project not found / inaccessible" | Špatný účet. Ověř v sidebaru správný project link. |
| "Team plan failed to renew" banner | Notifikace Tomovi — AI_Tom workspace platbu vyřešit. Capture funguje i tak. |
| Tampermonkey neuloží | Zkontroluj `pl_server` běží (`curl localhost:8790/pl/stats`). Zkontroluj extension aktivní v Chrome. |
| Soubor existuje ale nerostl | Konverzace nemá nový obsah od minulého capture — OK. |
| 404 nebo redirect | Conv_id špatný nebo konverzace smazaná. Refresh project listing. |

## Po capture

Automaticky pokračuj standardním tmonkey workflow:

```
python L:/LG13/app/agent/tmonkey_ts_reader.py --instance <name> --tail 200 --mark-read
```

Pak routuj obsah dle skill `tmonkey` (legal → legal instance, Lukáš → t003+t001, atd.).

## Známé konstanty

| Item | Hodnota |
|------|---------|
| LG13 project URL | `https://chatgpt.com/g/g-p-69880e4a53548191a37df1a2103f9f7f-luky-s-game-13/project` |
| Projekt sidebar text | `Luky's Game 13` |
| Default N conversations | 2 |
| Wait po navigate | 10s |
| Inbox root | `L:\LG13\inbox\chatgpt\YYYY-MM\DD\` |
| pl_server endpoint | `http://localhost:8790/pl/chatgpt/ingest` |

## Bezpečnost

- NIKDY neposílej zprávy v chatu přes tento skill (žádný `type` do input boxu). Jen čtení.
- Pokud se objeví modal dialog (platba, souhlas) — neklikej, nahlas Tomovi.
- "Update payment" button NIKDY — to je `prohibited_action` (financial).

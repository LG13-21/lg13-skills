---
name: file-catalog-search
description: Use when searching for a file by name or keyword anywhere on the system. Searches a pre-built TREE catalog (227k+ files) instead of slow filesystem scan or repeated Glob calls.
user-invocable: true
---

# File Catalog Search — Hledání souborů přes TREE katalog

## PRAVIDLO

**Nikdy nespouštěj `find` nebo `Get-ChildItem -Recurse` pro hledání souborů.** Použij tento skill — katalog pokrývá 227 000+ souborů a vrací výsledky okamžitě.

## POUŽITÍ

```bash
python L:/LG13/app/agent/skills/file_catalog_search.py <pattern> [--limit N] [--root <root>] [--exact]
```

### Příklady

```bash
# Najdi soubor podle části názvu
python L:/LG13/app/agent/skills/file_catalog_search.py "atom_dispatcher"

# Najdi v konkrétním root adresáři
python L:/LG13/app/agent/skills/file_catalog_search.py "STAV_NOW" --root LG13

# Přesná shoda filename
python L:/LG13/app/agent/skills/file_catalog_search.py "jarvis_v2.html" --exact

# Více výsledků
python L:/LG13/app/agent/skills/file_catalog_search.py "chatgpt_ingest" --limit 20

# Hledej jen v GitHub repech
python L:/LG13/app/agent/skills/file_catalog_search.py "CLAUDE.md" --root GitHub
```

## PARAMETRY

| Parametr | Výchozí | Popis |
|----------|---------|-------|
| `pattern` | (required) | Hledaný řetězec — case-insensitive, substring celé cesty |
| `--limit N` | 50 | Max výsledků |
| `--root <str>` | všechny rooty | Filtruj dle rootu: `GitHub`, `LG13`, `Lukasek`, `Lukasek13` |
| `--exact` | false | Přesná shoda filename (ne substring v celé cestě) |

## POKRYTÍ KATALOGU

| Root | Pokrývá |
|------|---------|
| `L:\GitHub` | Všechny repozitáře (lg13-coder, legal-ship-2026, lg13-tampermonkey, …) |
| `L:\LG13` | Runtime, app, agent kód, skills, atoms |
| `L:\Lukasek` | Tomova data, archivy, projekty |
| `C:\Users\tom\OneDrive\Dokumenty\Lukasek13` | OneDrive dokumenty |

**Vyloučeno:** `node_modules`, `venv`, `.git`, `__pycache__`, `granite-docling-258M`

Katalog: auto-discovery z více umístění (nejnovější TREE soubor se použije automaticky):
1. `L:\Tree\OUT_INVENTORY\TREE_*.txt` ← **primární** (aktuální)
2. `L:\lukasek_auto_data\New9\OUT\OUT_INVENTORY\TREE_*.txt` ← fallback
3. `L:\GitHub\legal-ship-2026\ChatGPT_export\TREE_*.txt` ← fallback

Aktuální katalog: `TREE_2026-06-19_175819.txt` (19.7 MB)

## REFRESH (pokud nenajdeš čerstvě vytvořený soubor)

```powershell
# Primární (generuje do L:\Tree)
Set-Location "L:\Lukasek_Auto_Data\New9"
powershell -ExecutionPolicy Bypass -File ".\00_collect_tree.ps1"
# Trvá ~30–60s
```

## KDY POUŽÍT

- "kde je soubor X?"
- "najdi implementaci Y"
- "kde leží STAV_NOW.md strat instance?"
- Před jakýmkoli ručním Glob nebo find příkazem

## KDY NEPOUŽÍT

- Pokud cestu znáš → Read přímo (rychlejší)
- Hledáš obsah souboru → Grep tool (ne katalog — katalog má jen cesty)

## RELATED

- `L:\LG13\app\agent\skills\file_catalog_search.py` — search script
- `L:\lukasek_auto_data\New9\config.ps1` — konfigurace (SourceDirs, ExcludeDirNames)
- `L:\lukasek_auto_data\New9\00_collect_tree.ps1` — generátor katalogu

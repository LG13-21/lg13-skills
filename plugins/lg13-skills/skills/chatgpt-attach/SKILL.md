---
name: chatgpt-attach
description: "Use when the user wants to SEND FILES (přílohy, PDF, md, obrázek) into a ChatGPT thread or upload a file into a ChatGPT Project sources ('pošli soubor do chatgpt', 'nahraj do Projectu', cgpt --attach), or when attach_failed / upload_failed appears. Text-only send is chatgpt-send."
user-invocable: true
---

# ChatGPT Attach — přílohy a Project sources přes TM Executor (v1.11+)

Soubor se zkopíruje do `L:/LG13/runtime/ops/chatgpt_cmds/files/<token>/`, pl_server ho vystaví na `/pl/chatgpt/file?f=`, Executor (Tampermonkey) ho stáhne a vloží do composeru. Edge/CDP se nepoužívá.

## Podmínky
- pl_server běží (`localhost:8790`), otevřená karta cílového vlákna / Projectu, `LG13 Executor` ≥ 1.11.
- Typy: pdf, md, txt, png, jpg, jpeg. Max 25 MB na soubor.

## A) Příloha ke zprávě ve vlákně
```bash
python L:/GitHub/lg13-coder/agent/skills/cgpt_tm_send.py \
  --thread <conv_id|url> --text "text" --attach C:/cesta/soubor.pdf [--attach další.md] [--wait-reply 300]
```

## B) Soubor do Project sources
```bash
python L:/GitHub/lg13-coder/agent/skills/cgpt_project_upload.py \
  --project <url Projectu> --file C:/cesta/soubor.md [--file další] [--timeout 150]
```
`--replace` je jen v CLI a záměrně neimplementováno (nic nemaže).

## Fail módy
| výstup | příčina |
|---|---|
| `executor neodpovedel` | žádná karta / Executor neběží |
| `attach_failed:<krok>` | composer nepřijal soubor; krok říká kde (fetch, set_files, paste) |
| `upload_failed:<krok>` | totéž pro Project sources |
| `FAIL: nepodporovany typ` | přípona mimo povolené |

## Stav
Kód nasazen, E2E na živém ChatGPT zatím neproběhl (chybí testovací vlákno/Project a TM Executor 1.11 v Edge).

## Related
- `chatgpt-send` — jen text; issue #772

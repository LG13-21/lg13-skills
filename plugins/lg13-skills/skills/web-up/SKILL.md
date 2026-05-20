# Web-Up — Build + FTP deploy review webu

## PURPOSE

Sestaví review web (HTML + ZIP + PDF přílohy) z aktuálního F-cyklu a nasadí ho FTP na `luky.ai-domy.cz/web_up/`.

---

## PARAMETRY

| Parametr | Příklad | Popis |
|----------|---------|-------|
| `cycle=<F>` | `cycle=F17_0` | Kterou verzi buildovat + nasadit |
| `build-only` | — | Jen build, bez FTP uploadu |
| `deploy-only` | — | Jen FTP upload existujícího buildu |
| _(bez parametru)_ | — | Build + deploy aktuálního cyklu |

---

## REMOTE URL

```
https://luky.ai-domy.cz/web_up/
FTP: ftpx.forpsi.com → /subdoms/luky/web_up/
```

---

## EXECUTION

### Krok 1 — Build review webu

```python
# Spusť build skript pro daný F-cyklus
# Skript generuje: index.html + ZIP soubory + prilohy/
python C:/Users/tom/Documents/rizeni/pece_Matousek_909/doplneni_c1/F16_4/build_review_web_F16_4.py
```

Výstup: `web_<cycle>/` složka s `index.html`, ZIPy, `prilohy/` PDFka.

### Krok 2 — FTP deploy na web_up

```python
# Spusť deploy skript — uploadne do /subdoms/luky/web_up/
python C:/Users/tom/Documents/rizeni/pece_Matousek_909/doplneni_c1/F16_4/ftp_deploy_F16_4.py
```

FTP credentials jsou v deploy skriptu. Výsledek: `https://luky.ai-domy.cz/web_up/`

### Krok 3 — Ověření

Naviguj na `https://luky.ai-domy.cz/web_up/` a ověř:
- index.html se načetl
- ZIPy jsou dostupné ke stažení
- PDF přílohy jsou přístupné

---

## FTP CONFIG (reference)

```
FTP_HOST   = "ftpx.forpsi.com"
FTP_USER   = "www.ai-domy.cz"
FTP_TARGET = "/subdoms/luky/web_up"
```

---

## WORKFLOW

```
1. web-up cycle=F17_0
2. Build: generuje web_F17_0/ + ZIPy
3. Deploy: FTP → /subdoms/luky/web_up/
4. Verify: https://luky.ai-domy.cz/web_up/
5. Report: URL + seznam souborů + celková velikost
```

---

## NOTES

- Přejmenováno z `r-davka2-F15` → `web_up` (2026-05-16)
- Starý URL `r-davka2-F15` zůstává aktivní pro historii
- Pro nový F17.0 balík vždy nasazovat do `web_up`
- Skill `web-up` = wrapper pro build + deploy pipeline

---

## RELATED

- `ftp_deploy_F16_4.py` — referenční deploy skript
- `build_review_web_F16_4.py` — referenční build skript
- Pro F17.0 bude potřeba nový `build_review_web_F17_0.py` + `ftp_deploy_F17_0.py`

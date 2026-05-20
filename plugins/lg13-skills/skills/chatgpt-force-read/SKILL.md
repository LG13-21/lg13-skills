---
name: chatgpt-force-read
description: "Prinuti TM (Tampermonkey) aby precetl a ingestoval ChatGPT vlakno — naviguje Edge na thread URL pres Playwright CDP, TM script se spusti automaticky a zachyti konverzaci jako atom do pl_server pipeline. Pouzij kdyz chces 'force TM to read this thread', 'force ingest', 'at to TM precte', 'nacti odpoved z chatgpt do atomu', 'trigger TM ingest na tomto vlaknu'. NETRIGGERUJ kdyz uzivatel jen chce precist thread sam nebo stahnout obsah bez LG13 pipeline."
---

# ChatGPT Force-Read — navigate Edge → TM ingest → atom pipeline

## PURPOSE

Prinuti TM aby precetl ChatGPT vlakno a poslal obsah do LG13 atom pipeline.
Zadne psani, zadny TM Executor. Jen "otevri URL, TM precte."

---

## PARAMETRY / REZIMY

| Parametr | Priklad | Co dela |
|----------|---------|---------|
| `url=<URL>` | `url=https://chatgpt.com/c/abc` | Ingestuje jedno konkretni vlakno |
| `project=<P> today` | `project=Legal today` | Vsechna dnesni vlakna z projektu |
| `project=<P> -<N>days` | `project=Coding -10days` | Vlakna z poslednich N dni |
| `project=<P> last` | `project=Legal last` | Posledni vlakno (viz LAST TRACKING) |
| `project=<P> last<N>` | `project=Legal last3` | Poslednich N vlaken |
| _(bez parametru)_ | — | **MUST ASK** — viz BEZ PARAMETRU nize |

**Zkratky pro projekt:** `Legal`, `Coding`, `LG13`, `Personal` nebo jake jsou v sidebaru.

---

## CDP AUTOFIX (vždy první krok)

Před každým Playwright voláním ověř CDP port. Pokud nereaguje → restartuj Edge automaticky:

```python
import urllib.request, subprocess, time

def ensure_edge_cdp():
    try:
        urllib.request.urlopen("http://localhost:9222/json/version", timeout=2)
        return True
    except Exception:
        print("CDP nedostupný — restartuji Edge...")
        subprocess.run(["powershell","-Command","Get-Process msedge -ErrorAction SilentlyContinue | Stop-Process -Force"], capture_output=True)
        time.sleep(2)
        subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe","--remote-debugging-port=9222","--profile-directory=Default"])
        time.sleep(5)
        return True

ensure_edge_cdp()
```

Po navigate přenést Edge na plochu (maximalizovat):

```python
subprocess.run(["powershell","-Command","""
    Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;public class W{[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);}'
    $p=Get-Process msedge|Sort MainWindowHandle -Desc|Select -First 1
    if($p -and $p.MainWindowHandle -ne 0){[W]::ShowWindow($p.MainWindowHandle,3);[W]::SetForegroundWindow($p.MainWindowHandle)}
"""], capture_output=True)
```

---

## EXECUTION — 3 rezimy

### Rezim A: znama URL (rychle)

```
chatgpt-force-read url=https://chatgpt.com/c/<thread_id>
```

Spust Python skript nize s `THREAD_URL` vyplnenym.

### Rezim A2: projekt + "today" (batch ingest dnesniho dne)

```
chatgpt-force-read project=Legal today
```

Otevri projekt v sidebaru, scrape vsechna vlakna kde datum = dnes, projdi je postupne (kazde navigate + 8s cekani).

```python
# Pseudokod — scrape today's threads from project
threads_today = [t for t in threads if t['date'] == today]
for t in threads_today:
    page.goto(t['url'], timeout=20000)
    page.wait_for_timeout(8000)
    print(f"Ingested: {t['title']}")
```

### BEZ PARAMETRU — AUTO-CHOICE po 60s

**Nikdy nečekej na odpověď indefinitely.** Pokud uživatel neodpoví do 60s → pokračuj s defaultem.

Pattern:
```
1. Zobraz otázku + default: "Který projekt? Default: Recents (bez projektu). Pokračuji za 60s..."
2. Spusť countdown: time.sleep(60)
3. Pokud přišla odpověď → použij ji. Pokud ne → použij default.
```

Default bez parametru = **Recents, last 1 vlákno** (nejnovější v sidebaru bez filtru projektu).

Kratší timeout (30s) pokud instance běží autonomně bez aktivního uživatele.

### Rezim B: interaktivni vyber projektu + vlakna

**Krok 1 — scrape projekty a vlakna z ChatGPT sidebar:**

```python
from playwright.sync_api import sync_playwright
import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    ctx = browser.contexts[0]
    import sys as _s; _s.path.insert(0,'L:/LG13/app/agent')
    from chatgpt_tab_manager import get_or_open_tab, cleanup_tab
    page, _obu = get_or_open_tab(ctx)  # reuse or open; cap enforced

    # Projekty ze sidebaru
    projects = page.evaluate("""() => {
        const items = [...document.querySelectorAll('nav a, [data-testid*=project], li a')];
        return items
            .filter(el => el.href && el.href.includes('/g/') || el.textContent.trim().length > 0)
            .map(el => ({text: el.textContent.trim(), href: el.href || ''}))
            .filter(el => el.text && !el.href.includes('/c/'))
            .slice(0, 15);
    }""")

    # Posledni vlakna (Recents)
    threads = page.evaluate("""() => {
        const links = [...document.querySelectorAll('nav a[href*="/c/"], ol a[href*="/c/"]')];
        return links.slice(0, 10).map(el => ({
            title: el.textContent.trim().slice(0, 60),
            url: el.href
        }));
    }""")

    print(json.dumps({"projects": projects, "threads": threads}, ensure_ascii=False))
```

**Krok 2 — prezentuj vyber + auto-choice:**
- Zobraz projekty + "Default: Recents. Pokračuji za 60s pokud neodpovíš."
- `AskUserQuestion` použij jen pokud je uživatel aktivně přítomen
- Timeout 60s → default = první vlákno z Recents
- Po vyberu projektu: klikni na projekt v sidebaru, znovu scrape threads, nabídni top 10

**Krok 3 — navigate + TM ingest:**

```python
page.goto(selected_url, timeout=20000)
page.wait_for_timeout(8000)  # TM ingest potrebuje ~3-8s
print(f"Navigated: {page.url}")
print("TM ingest should have fired.")
cleanup_tab(page, _obu)  # close if we opened it; reused tabs stay open
```

---

## PREREKVIZITY

- Edge s CDP: `--remote-debugging-port=9222`
- TM ingest script aktivni: `lg13_chatgpt_ingest.user.js v4.9.2+`

---

## WORKFLOW S TMONKEY-ARM

```
1. arm tmonkey-arm pro svou instanci
2. chatgpt-force-read (rezim A nebo B)
3. TM ingest → atom → stack file → mtime change
4. tmonkey-arm detekuje → wake-up notification
5. stack_reader --new --mark-read --limit 50
```

---

## AUTO-ARM TMONKEY-ARM

Po každém úspěšném navigate — automaticky spusť `tmonkey-arm` skill pro svou instanci:
```
tmonkey-arm  →  Monitor watcher na <inst>_stack.jsonl mtime change
```
Tím instance automaticky dostane notification jakmile TM ingest dorazí — bez pollingu, bez čekání.
Nezapisuj nic, jen arm. Pokud tmonkey-arm už běží → skip (idempotentní).

## CEKAT NA TM INGEST (povinne)

Kratke vlakno (2-10 zprav) = ~3-5s. Dlouhe vlakno (100-200 zprav) = 15-30s.
**Nezavirej page dokud TM nepotvrdil ingest** — cekej na atom v pl_server nebo na stack file mtime change.

```python
# Po navigate — poll stack file dokud se nezmeni mtime
import time, os
stack = f"L:/LG13/runtime/stacks/<instance>_stack.jsonl"
mtime_before = os.path.getmtime(stack) if os.path.exists(stack) else 0
page.goto(url, timeout=20000)
for _ in range(30):  # max 30s
    time.sleep(1)
    mtime_now = os.path.getmtime(stack) if os.path.exists(stack) else 0
    if mtime_now > mtime_before:
        print("TM ingest confirmed")
        break
```

## LAST TRACKING

Skill si pamatuje ktere vlakno bylo naposledy ingestovano per projekt:
`L:/LG13/runtime/ops/chatgpt_last_read.json`

```json
{"Legal": {"url": "...", "ts": "...", "title": "..."}, "Coding": {...}}
```

Po kazdem uspesnem ingestu: aktualizuj tento soubor.
Pri `last` / `last3` parametru: precti soubor a naviguj na posledni(ch) N vlaken.

## DYNAMICKY REFRESH

Po ingestu vlakna — pokud ocekavaš odpoved:
- Posledni aktivita < 5 min: refresh kazdych 60s
- Posledni aktivita 5-30 min: refresh kazdych 5 min
- Posledni aktivita > 30 min: refresh na pozadavek

Kombinuj s `tmonkey-arm` — watcher detekuje stack file mtime change automaticky.

## NOTES

- WAIT_MS=8000 — TM ingest potrebuje cas po page load (minimum)
- Pokud atom neprijde: vlakno mozna nema novou odpoved od posledniho ingestu (dedup) — OK
- Force-refresh: navigate na tutez URL znovu = TM reingestuje
- Po chatgpt-send: pockej ~30-60s nez ChatGPT dokonci odpoved, pak force-read

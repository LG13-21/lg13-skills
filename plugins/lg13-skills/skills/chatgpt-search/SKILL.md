---
name: chatgpt-search
description: "Vyhledá text nebo konverzaci v ChatGPT chatech přes vyhledávání v sidebaru nebo přes Playwright CDP. Trigger: 'hledej v chatgpt', 'najdi konverzaci kde jsem říkal', 'chatgpt search', 'kde jsem to říkal chatgpt', 'prohledej moje chaty'. Použij kdykoli Tom chce najít starší konverzaci nebo konkrétní obsah v ChatGPT historii."
user-invocable: true
---

# ChatGPT Search — vyhledávání v historii chatů

## PREREKVIZITY

Edge s přihlášením na chatgpt.com (persistent profile `C:/Users/tom/AppData/Local/Microsoft/Edge/User Data`).
Playwright Edge funguje bez CDP.

---

## EXECUTION

### Rychlé vyhledávání přes ChatGPT search bar

```python
import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

QUERY = "<hledaný text>"

async def run():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir='C:/Users/tom/AppData/Local/Microsoft/Edge/User Data',
            channel='msedge', headless=False,
            args=['--profile-directory=Default']
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto('https://chatgpt.com/', timeout=20000)
        await page.wait_for_timeout(3000)

        # Klikni na search (ikonka lupa nebo Ctrl+K)
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(1000)
        await page.keyboard.type(QUERY)
        await page.wait_for_timeout(2000)

        # Precti vysledky
        results = await page.evaluate('''() => {
            const items = [...document.querySelectorAll("[data-testid*=search], .search-result, li a[href*=\"/c/\"]")];
            return items.slice(0, 10).map(el => ({
                title: el.textContent.trim().slice(0, 80),
                href: el.href || el.closest("a")?.href || ""
            }));
        }''')
        for r in results:
            print(r['title'], '->', r['href'][-30:] if r['href'] else '')
        await ctx.close()

asyncio.run(run())
```

### Výběr a čtení konverzace

Po nalezení URL — předej do `chatgpt-force-read url=<URL>` pro TM ingest do LG13 pipeline.
Nebo přečti přímo přes Playwright (viz `chatgpt-force-read` skill).

---

## PARAMETRY

| Vstup | Příklad | Co dělá |
|-------|---------|---------|
| `query=<text>` | `query=force read skill tipy` | Vyhledá v historii |
| `project=<P>` | `project=Coding` | Omezí na projekt |
| _(bez parametru)_ | — | Zeptá se co hledat |

---

## BEZ PARAMETRU — dotazník

```
1. "Co hledám v ChatGPT historii?"
2. "V jakém projektu? (Legal / Coding / LG13 / všechny)"
3. "Chceš jen najít URL, nebo rovnou načíst obsah?"
```

---

## WORKFLOW S FORCE-READ

```
chatgpt-search query=<co hledám>
    ↓
výsledky → seznam URL
    ↓
chatgpt-force-read url=<URL>
    ↓
TM ingest → atom → stack → LG13 pipeline
```

---

## NOTES

- ChatGPT search hledá v názvech konverzací, ne v obsahu. Pro full-text obsahu = git-tmonkey-search skill (pokud bylo ingestováno).
- Pokud search bar nereaguje na Ctrl+K: zkus kliknout na ikonku lupy v sidebaru.
- Výsledky jsou omezené na konverzace které ChatGPT indexoval (obvykle posledních ~6 měsíců).

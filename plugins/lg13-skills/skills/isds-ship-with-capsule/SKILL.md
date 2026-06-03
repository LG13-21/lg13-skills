---
name: isds-ship-with-capsule
description: |
  Řídí celý proces odeslání soudního dokumentu přes ISDS pro LG13 instanci t002.
  Zahrnuje: fyzická verifikace příloh, live ISDS ověření DS adresáta, 5 LOCK UL check
  (legal/t002/strat/coder/tom), time capsule (min. 60 min pro soud), /cockpit report
  každé kolo loopu, a post-ship notifikace.
  
  VŽDY použij tento skill když: "ship wave", "odešli datovku", "spusť ISDS filing",
  "time capsule wave", "loop dokud se nepošle", "wave 1 ship", "wave 2 ship",
  "/isds-ship-with-capsule", nebo kdykoli jde o pipeline odeslání dokumentu přes datovou schránku
  s lock mechanismem. NIKDY nenechávej pipeline bez tohoto skillu — každý krok je kritický.
---

# isds-ship-with-capsule

T002 je jediný odesílatel. Ale Tom odesílá sám přes ISDS — t002 jen řídí pipeline, ověřuje, hlídá locks a informuje. Každý krok je kritický — chyba DS adresáta pošle dokument na špatný soud.

## PIPELINE (v pořadí, nepřeskakovat)

### Krok 1 — Identifikace bundlu

Zjisti jaká wave se posílá a kde jsou soubory:

```bash
python -c "
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
for d in sorted(Path('L:/GitHub/legal-ship-2026').glob('ISDS_Wave*')):
    print(d.name, list(d.glob('*.pdf')))
"
```

Přečti `DATOVKA_TEXT.md` (nebo `ISDS_Wave*/DATOVKA_TEXT.md`) — zjisti:
- DS adresáta (DS ID)
- Předmět datovky
- Seznam příloh

### Krok 2 — Fyzická verifikace příloh

```bash
python -c "
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
wave_dir = Path('L:/GitHub/legal-ship-2026/ISDS_Wave1a')  # uprav dle wave
for f in sorted(wave_dir.glob('*.pdf')):
    print(f'OK {f.name}: {f.stat().st_size} B')
"
```

Porovnej s `DATOVKA_TEXT.md`. Pokud příloha chybí → STOP, informuj legal, neodesílej.

### Krok 3 — ISDS live verify DS ⚠️ KRITICKÉ

**VŽDY ověř DS adresáta přes ISDS API — nikdy nevěř jen ds_adresar.json.**

```bash
python L:/LG13/app/agent/isds_sender.py --verify <DS_ID>
```

Zkontroluj `firmName` a `adCity`. Musí odpovídat očekávané instituci.

> **Historická chyba 2026-05-24 (#74):** `snkabbm` = Městský soud Praha (ŠPATNĚ), `ws6abvh` = OS České Budějovice (SPRÁVNĚ). Commit 090690b zavedl chybné DS — odhaleno až live verify. Bez tohoto kroku by dokument šel na špatný soud.

Pokud DS nesouhlasí → oprav `DATOVKA_TEXT.md`, commit, informuj legal, znovu ověř.

### Krok 4 — Lock check (5 keepers)

Sesbírej LOCK UL deklarace z ping_pong souborů:

```bash
python -c "
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

base = Path('L:/LG13/runtime/ops/ping_pong')
locks = {'legal': False, 't002': False, 'strat': False, 'coder': False, 'tom': False}

for f in sorted(base.glob('*_lock_ul.json')):
    try:
        msg = json.loads(f.read_text(encoding='utf-8'))
        sender = msg.get('from', '')
        decisions = msg.get('decisions', {})
        if any('UL' in str(v) for v in decisions.values()):
            if sender in locks:
                locks[sender] = True
    except:
        pass

for k, v in locks.items():
    print(f'{k}: {\"UL\" if v else \"WAIT\"}')
print(f'ALL_UL: {all(locks.values())}')
"
```

Pokud `ALL_UL: False` → čekej, reportuj stav v cockpitu, nepokračuj.

Tom lock = Tom napsal GO přímo nebo schválil v dashboardu. STOP ORDER #1452 ruší **výhradně** fráze `KONEC STOP` od Toma osobně.

### Krok 5 — Time capsule

Po všech UL + Tom GO nastavit time capsule:

```bash
python -c "
import sys, time, json
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

# Default: soud = 3600s (60 min). ASAP = 300s. Tom TSEND override = 0.
wait_sec = 3600
capsule = {
    'wave': 'Wave1',
    'bundle_dir': 'ISDS_Wave1a/',
    'ds_verified': 'ws6abvh',
    'created_at': time.strftime('%Y-%m-%dT%H%M%SZ', time.gmtime()),
    'deliver_after': time.strftime('%Y-%m-%dT%H%M%SZ', time.gmtime(time.time() + wait_sec)),
    'wait_sec': wait_sec,
    'approved_by': 'tom'
}
out = Path('L:/LG13/runtime/ops/time_capsules/')
out.mkdir(parents=True, exist_ok=True)
(out / 'active_capsule.json').write_text(json.dumps(capsule, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Time capsule set. deliver_after: {capsule[\"deliver_after\"]}')
"
```

Výjimky:
- Soud = 60 min (default)
- ASAP v instrukci = 5 min
- `0 min` jen Tomův osobní TSEND override

### Krok 6 — /cockpit report (každé kolo loopu)

Generuj přehled bez cockpit.py (script neexistuje — inline):

```markdown
# COCKPIT — Wave Ship | <timestamp>

## LOCKS
Legal:[UL/WAIT] T002:[UL/WAIT] Strat:[UL/WAIT] Coder:[UL/WAIT] Tom:[GO/WAIT]

## DS VERIFY
<DS_ID> = <firmName>, <adCity> — [VERIFIED OK / ERROR]

## PŘÍLOHY
<N>/<total> OK | chybí: <seznam>

## TIME CAPSULE
[ACTIVE until <deliver_after> / EXPIRED / NOT SET]
Zbývá: <minuty> min

## STATUS
WAITING_LOCKS | WAITING_CAPSULE | READY_TO_SHIP | SHIPPED
```

### Krok 7 — Čekání na expiraci capsule

Každých 60s zkontroluj:

```bash
python -c "
import sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
cap_path = Path('L:/LG13/runtime/ops/time_capsules/active_capsule.json')
if not cap_path.exists():
    print('NO CAPSULE')
else:
    cap = json.loads(cap_path.read_text(encoding='utf-8'))
    now = time.strftime('%Y-%m-%dT%H%M%SZ', time.gmtime())
    ready = now >= cap['deliver_after']
    print(f'deliver_after: {cap[\"deliver_after\"]}')
    print(f'now: {now}')
    print(f'READY: {ready}')
"
```

### Krok 8 — Informovat Toma (SHIP signal)

Po expiraci capsule — informuj Toma:

> "⏰ Time capsule vypršela. **Wave [X] ready k odeslání.**
> DS: `ws6abvh` = Okresní soud v Českých Budějovicích ✅
> Přílohy: 4/4 OK
> Tom — odešli přes ISDS manuálně."

**T002 NIKDY neodesílá autonomně.** Jen informuje.

### Krok 9 — Post-ship (po Tomově potvrzení)

```bash
python L:/LG13/app/agent/instance_queue.py --send --to strat --from-inst t002 \
  --msg "ODESLANO: ISDS → ws6abvh | Wave1 F24 vyjádření k AS" --priority P2

python L:/LG13/app/agent/instance_queue.py --send --to t001 --from-inst t002 \
  --msg "ODESLANO: ISDS → ws6abvh | Wave1 F24 vyjádření k AS" --priority P2
```

Aktualizuj STAV_NOW.md, smaž time capsule soubor, spusť save-min.

## COCKPIT LOOP PATTERN

Když Tom zadá `/goal /loop 60s until wave shipped`:

1. Každé kolo: Krok 4 (lock check) + Krok 7 (capsule check) + Krok 6 (cockpit report)
2. Pokud locks chybí → pingni příslušnou instanci
3. Pokud capsule chybí a locks jsou OK → nastav capsule (Krok 5)
4. Pokud capsule expired → informuj Toma (Krok 8)
5. Po shipu: post-ship (Krok 9) → goal clear

## HARD RULES

1. DS VŽDY ověřit live přes `isds_sender.py --verify` — ds_adresar.json může být zastaralý
2. Tom odesílá VÝHRADNĚ sám — t002 jen připravuje a informuje  
3. Time capsule min. 60 min pro soud (výjimka jen Tomův TSEND override)
4. 5 LOCKS required: legal + t002 + strat + coder + tom
5. Nikdy nepokračovat pokud přílohy fyzicky chybí

## RELATED

- Recipe: `L:/Lukasek/recipes/isds.md`
- Skill: `locks-workflow`  
- Parent CLAUDE.md: STOP ORDER #1452, 5 LOCKS spec
- Historická chyba: snkabbm≠ws6abvh (2026-05-24, issue #74, commit 090690b)
- Goal template: `L:/GitHub/legal-ship-2026/runtime/ops/avengers_goals.json`

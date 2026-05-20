#!/usr/bin/env python3
"""
audit.py — Čtení/zápis meta.json + CHANGELOG.txt pro locks-workflow.

Použití:
  python audit.py --folder <cesta> --lock strat --status PASS --by "legal" --notes "..."
  python audit.py --folder <cesta> --lock strat --status PASS --by "legal" --dry-run
  python audit.py --folder <cesta> --status-only [--json]
  python audit.py --folder <cesta> --version-add F10.1_S+_ASAP --author strat --notes "..."
  python audit.py --folder <cesta> --changelog "Text záznamu"
  python audit.py --folder <cesta> --parse-lockstring "S+L+O+"
"""
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

LOCK_MAP = {
    'strat': 'strat_check',
    'legal': 'legal_check',
    't002':  't002_check',
    'tom':   'tom_approve',
    'time':  'time_lock',
}

STATUS_SYMBOLS = {
    'PASS': '✅',
    'FAIL': '❌',
    'PASS with condition': '⚠️',
    None: '⏳',
}

# Whitelist pro tom_approve.by — STOP ORDER: jen tyhle hodnoty jsou platné
TOM_APPROVE_WHITELIST = {'tom', 'tom_dashboard', 'tom_direct'}


# ─── parse_lockstring ──────────────────────────────────────────────────────────

def parse_lockstring(s: str) -> dict:
    """
    Parsuje lock_string jako sekvenci 2-char tokenů.
    Příklady: "S+L+O+" → {S: '+', L: '+', O: '+', T: None, C: None}
              "S+L-"   → {S: '+', L: '-', O: None, T: None, C: None}

    Nepoužívej split('+') — to selže na "S+L-O+".
    Každý token je vždy právě 1 písmeno + 1 symbol (+/-/?).
    """
    codes = {'S': None, 'L': None, 'O': None, 'T': None, 'C': None}
    pattern = re.findall(r'([SLOTC])([+\-?])', s.upper())
    for code, symbol in pattern:
        codes[code] = symbol
    return codes


def lockstring_from_dict(d: dict) -> str:
    """Sestav lock_string z dict {S:'+', L:'+', O:None, ...} → 'S+L+'"""
    return ''.join(f"{k}{v}" for k, v in d.items() if v is not None)


def lockstring_from_meta(meta: dict) -> str:
    """Sestav lock_string ze stavu meta.json locks."""
    locks = meta.get('locks', {})
    lock_order = [('strat', 'S'), ('legal', 'L'), ('t002', 'O'), ('tom', 'T'), ('time', 'C')]
    key_map = {'strat': 'strat_check', 'legal': 'legal_check',
               't002': 't002_check', 'tom': 'tom_approve', 'time': 'time_lock'}
    parts = []
    for name, code in lock_order:
        val = locks.get(key_map[name])
        if val:
            status = val.get('status', '')
            symbol = '+' if 'PASS' in status else '-'
            parts.append(f"{code}{symbol}")
    return ''.join(parts)


# ─── meta.json read/write s concurrency check ─────────────────────────────────

def read_meta(folder: Path) -> dict:
    meta_path = folder / 'meta.json'
    if not meta_path.exists():
        raise FileNotFoundError(f'meta.json nenalezen v {folder}')
    return json.loads(meta_path.read_text(encoding='utf-8'))


def write_meta_safe(folder: Path, meta: dict, expected_stav: str = None, expected_verze: str = None):
    """
    Atomický zápis meta.json s concurrency check.
    Pokud expected_stav nebo expected_verze jsou zadány, ověří že se nezměnily od čtení.
    Vyvolá RuntimeError při konfliktu.
    """
    meta_path = folder / 'meta.json'

    if expected_stav is not None or expected_verze is not None:
        current = json.loads(meta_path.read_text(encoding='utf-8'))
        if expected_stav is not None and current.get('stav') != expected_stav:
            raise RuntimeError(
                f'CONCURRENCY_CONFLICT: stav se změnil od čtení: '
                f'expected="{expected_stav}", actual="{current.get("stav")}". Opakuj operaci.'
            )
        if expected_verze is not None and current.get('aktualni_verze') != expected_verze:
            raise RuntimeError(
                f'CONCURRENCY_CONFLICT: aktualni_verze se změnila od čtení: '
                f'expected="{expected_verze}", actual="{current.get("aktualni_verze")}". Opakuj operaci.'
            )

    tmp = meta_path.with_suffix('.tmp')
    tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(meta_path)


def changelog_append(folder: Path, text: str, dry_run: bool = False):
    if dry_run:
        print(f'[DRY RUN] CHANGELOG append:\n  {text}')
        return
    changelog = folder / 'CHANGELOG.txt'
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M')
    entry = f'\n{ts}\n{text}\n'
    with open(changelog, 'a', encoding='utf-8') as f:
        f.write(entry)


# ─── Lock operace ──────────────────────────────────────────────────────────────

def set_lock(folder: Path, lock_name: str, status: str, by: str, notes: str, dry_run: bool = False):
    """Zapíše výsledek jednoho zámku do meta.json (s concurrency check)."""
    meta = read_meta(folder)
    expected_stav = meta.get('stav')
    expected_verze = meta.get('aktualni_verze')

    key = LOCK_MAP.get(lock_name)
    if not key:
        raise ValueError(f'Neznámý zámek: {lock_name}. Platné: {list(LOCK_MAP.keys())}')

    # Matouš guard
    if lock_name == 'tom' and 'PASS' in status:
        if by not in TOM_APPROVE_WHITELIST:
            raise ValueError(
                f'MATOUŠ GUARD: tom_approve.by="{by}" není v whitelistu {TOM_APPROVE_WHITELIST}. '
                f'STOP — Tomův approve nelze zaznamenat bez explicitní Tomovy akce.'
            )

    entry = {
        'status': status,
        'by': by,
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'notes': notes,
    }

    if dry_run:
        print(f'[DRY RUN] locks.{key} = {json.dumps(entry, ensure_ascii=False)}')
        return

    meta['locks'][key] = entry
    write_meta_safe(folder, meta, expected_stav=expected_stav, expected_verze=expected_verze)
    changelog_append(folder, f'LOCK {lock_name.upper()} → {status} (by {by})\n  {notes}')
    print(f'{STATUS_SYMBOLS.get(status, "?")} Lock {lock_name.upper()} nastaven: {status}')


def add_version(folder: Path, version_tag: str, author: str, notes: str, dry_run: bool = False):
    """Přidá entry do versions[] v meta.json."""
    meta = read_meta(folder)
    expected_stav = meta.get('stav')
    expected_verze = meta.get('aktualni_verze')

    entry = {
        'v': version_tag,
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'author': author,
        'notes': notes,
    }

    if dry_run:
        print(f'[DRY RUN] versions.append({json.dumps(entry, ensure_ascii=False)})')
        print(f'[DRY RUN] aktualni_verze = "{version_tag}"')
        return

    meta.setdefault('versions', []).append(entry)
    meta['aktualni_verze'] = version_tag
    write_meta_safe(folder, meta, expected_stav=expected_stav, expected_verze=expected_verze)
    changelog_append(folder, f'VERZE {version_tag} vytvořena (author: {author})\n  {notes}')
    print(f'✅ Verze {version_tag} zaznamenána v meta.json')


def update_stav(folder: Path, stav: str, dry_run: bool = False):
    meta = read_meta(folder)
    if dry_run:
        print(f'[DRY RUN] stav = "{stav}" (bylo: "{meta.get("stav")}")')
        return
    expected_verze = meta.get('aktualni_verze')
    meta['stav'] = stav
    write_meta_safe(folder, meta, expected_verze=expected_verze)
    print(f'✅ Stav aktualizován: {stav}')


# ─── Status output ─────────────────────────────────────────────────────────────

def get_status_dict(folder: Path) -> dict:
    """Vrátí status jako dict (pro --json output a dashboard integraci)."""
    meta = read_meta(folder)
    locks = meta.get('locks', {})

    lock_states = {}
    for lock_name in ['strat', 'legal', 't002', 'tom', 'time']:
        key = LOCK_MAP[lock_name]
        val = locks.get(key)
        if val:
            lock_states[lock_name] = {
                'code': {'strat':'S','legal':'L','t002':'O','tom':'T','time':'C'}[lock_name],
                'status': val.get('status'),
                'symbol': '+' if 'PASS' in val.get('status','') else '-',
                'by': val.get('by'),
                'timestamp': val.get('timestamp'),
                'notes': val.get('notes'),
            }
        else:
            lock_states[lock_name] = {
                'code': {'strat':'S','legal':'L','t002':'O','tom':'T','time':'C'}[lock_name],
                'status': None,
                'symbol': '?',
                'by': None,
                'timestamp': None,
                'notes': None,
            }

    lock_string = lockstring_from_meta(meta)
    parsed = parse_lockstring(lock_string)

    # Capsule info
    capsule_info = None
    capsule_start = meta.get('capsule_start_ts')
    capsule_min = meta.get('time_capsule_minutes', 60)
    if capsule_start:
        start_dt = datetime.fromisoformat(capsule_start)
        elapsed = (datetime.now() - start_dt).total_seconds() / 60
        remaining = max(0.0, capsule_min - elapsed)
        capsule_info = {
            'start_ts': capsule_start,
            'minutes_total': capsule_min,
            'elapsed_min': round(elapsed, 1),
            'remaining_min': round(remaining, 1),
            'done': remaining <= 0,
        }

    # Přílohy check
    prilohy_meta = meta.get('prilohy', [])
    prilohy_status = []
    for p in prilohy_meta:
        phys = (folder / 'prilohy' / p['soubor']).exists()
        prilohy_status.append({
            'c': p['c'],
            'nazev': p.get('nazev', ''),
            'soubor': p['soubor'],
            'physical': phys,
        })

    return {
        'folder': str(folder),
        'sp_zn': meta.get('rizeni', {}).get('sp_zn', '?'),
        'typ_podani': meta.get('typ_podani', '?'),
        'stav': meta.get('stav', '?'),
        'aktualni_verze': meta.get('aktualni_verze', '?'),
        'asap': meta.get('asap', False),
        'lock_string': lock_string,
        'lock_string_parsed': parsed,
        'locks': lock_states,
        'capsule': capsule_info,
        'prilohy': prilohy_status,
        'prilohy_ok': all(p['physical'] for p in prilohy_status),
    }


def print_status(folder: Path):
    s = get_status_dict(folder)

    print(f"\n{'='*60}")
    print(f"LOCK STATUS — {s['sp_zn']}")
    print(f"{'='*60}")
    print(f"Typ podání:     {s['typ_podani']}")
    print(f"Aktuální verze: {s['aktualni_verze']}")
    print(f"Stav:           {s['stav']}")
    print(f"ASAP:           {s['asap']}")
    print(f"Lock string:    {s['lock_string'] or '(none)'}")

    print(f"\nZÁMKY:")
    for name, lk in s['locks'].items():
        if lk['status']:
            sym = STATUS_SYMBOLS.get(lk['status'], '?')
            ts = (lk['timestamp'] or '')[:16]
            print(f"  {sym} {name.upper():8} {lk['status']:25} {ts}  by {lk['by']}")
        else:
            print(f"  ⏳ {name.upper():8} (pending)")

    if s['capsule']:
        c = s['capsule']
        if c['done']:
            print(f"\n✅ CAPSULE UPLYNULA — {c['elapsed_min']} min / {c['minutes_total']} min — ready pro lock send")
        else:
            print(f"\n⏰ CAPSULE BĚŽÍ — zbývá {c['remaining_min']} min z {c['minutes_total']} min")

    print(f"\nPŘÍLOHY ({len(s['prilohy'])} v meta):")
    for p in s['prilohy']:
        sym = '✅' if p['physical'] else '⛔'
        print(f"  {sym} P{p['c']}: {p['nazev'][:50]}")

    print()


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Audit meta.json a CHANGELOG.txt')
    parser.add_argument('--folder', type=Path, required=True, help='Složka podání')
    parser.add_argument('--lock', choices=list(LOCK_MAP.keys()), help='Zámek k nastavení')
    parser.add_argument('--status', help='Status: PASS|FAIL|PASS with condition')
    parser.add_argument('--by', default='legal', help='Kdo provádí lock')
    parser.add_argument('--notes', default='', help='Poznámky k locku')
    parser.add_argument('--version-add', metavar='TAG', help='Přidat verzi (např. F10.1_S+_ASAP)')
    parser.add_argument('--author', default='legal', help='Autor verze')
    parser.add_argument('--stav', help='Aktualizovat pole stav v meta.json')
    parser.add_argument('--changelog', help='Přidat záznam do CHANGELOG.txt')
    parser.add_argument('--status-only', action='store_true', help='Jen zobrazit status')
    parser.add_argument('--json', action='store_true', help='Status jako JSON (pro dashboard)')
    parser.add_argument('--parse-lockstring', metavar='STR', help='Parsuj lock_string a zobraz')
    parser.add_argument('--dry-run', action='store_true', help='Zobraz co by se zapsalo, nic nezapisuj')
    args = parser.parse_args()

    if args.parse_lockstring:
        result = parse_lockstring(args.parse_lockstring)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.status_only or args.json:
        if args.json:
            s = get_status_dict(args.folder)
            print(json.dumps(s, ensure_ascii=False, indent=2))
        else:
            print_status(args.folder)
    elif args.lock and args.status:
        set_lock(args.folder, args.lock, args.status, args.by, args.notes, dry_run=args.dry_run)
    elif args.version_add:
        add_version(args.folder, args.version_add, args.author, args.notes or '', dry_run=args.dry_run)
    elif args.stav:
        update_stav(args.folder, args.stav, dry_run=args.dry_run)
    elif args.changelog:
        if args.dry_run:
            print(f'[DRY RUN] CHANGELOG append: {args.changelog}')
        else:
            changelog_append(args.folder, args.changelog)
            print(f'✅ CHANGELOG aktualizován')
    else:
        print_status(args.folder)


if __name__ == '__main__':
    main()

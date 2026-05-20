#!/usr/bin/env python3
"""
lock.py — Hlavní CLI entry point pro locks-workflow skill.

Rozumí příkazům:
  lock init <md_file> [--folder <cesta>] [--asap] [--sp-zn "0 P 29/2026"]
  lock check [--folder <cesta>]
  lock strat [pass|fail] [--reason "..."] [--folder <cesta>]
  lock legal [pass|fail] [--reason "..."] [--folder <cesta>]
  lock t002  [pass|fail] [--reason "..."] [--folder <cesta>]
  lock tom   submit | approve | reject [--reason "..."] [--folder <cesta>]
  lock send  [--tsend-override] [--folder <cesta>]
  lock status [--folder <cesta>]
  lock cancel [--reason "..."] [--folder <cesta>]

Lze volat přes: python lock.py strat pass --folder C:\\...\\0P29_2026_doplneni_c1
NEBO volat jako modul (import lock; lock.run(['strat', 'pass', '--folder', '...']))
"""
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

SCRIPTS_DIR = Path(__file__).parent
LOCK_ORDER = ['strat', 'legal', 't002', 'tom']
LOCK_CODES = {'strat': 'S', 'legal': 'L', 't002': 'O', 'tom': 'T', 'time': 'C'}


# ─── Pomocné funkce ────────────────────────────────────────────────

def read_meta(folder: Path) -> dict:
    return json.loads((folder / 'meta.json').read_text(encoding='utf-8'))


def write_meta(folder: Path, meta: dict):
    p = folder / 'meta.json'
    tmp = p.with_suffix('.tmp')
    tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(p)


def changelog_append(folder: Path, text: str):
    p = folder / 'CHANGELOG.txt'
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M')
    with open(p, 'a', encoding='utf-8') as f:
        f.write(f'\n{ts}\n{text}\n')


def current_lock_string(meta: dict) -> str:
    """Sestav lock_string ze stavu meta.json locks."""
    locks = meta.get('locks', {})
    parts = []
    for lock_name in LOCK_ORDER:
        key = {'strat': 'strat_check', 'legal': 'legal_check',
               't002': 't002_check', 'tom': 'tom_approve'}[lock_name]
        val = locks.get(key)
        if val:
            status = val.get('status', '')
            symbol = '+' if 'PASS' in status else '-'
            parts.append(f"{LOCK_CODES[lock_name]}{symbol}")
    return ''.join(parts)


def next_version_tag(meta: dict, new_lock_symbol: str) -> str:
    """Vrátí nový F-tag po přidání zámku."""
    current = meta.get('aktualni_verze', 'F10.0')
    # Najdi base F number
    import re
    m = re.match(r'F(\d+)\.(\d+)', current)
    if m:
        major = int(m.group(1))
        minor = int(m.group(2)) + 1
    else:
        major, minor = 10, 1

    lock_str = current_lock_string(meta) + new_lock_symbol
    asap = '_ASAP' if meta.get('asap') else ''
    return f'F{major}.{minor}_{lock_str}{asap}'


def check_lock_order(meta: dict, required_previous: str) -> bool:
    """Ověří že předchozí zámek je PASS."""
    locks = meta.get('locks', {})
    key = {'strat': 'strat_check', 'legal': 'legal_check',
           't002': 't002_check', 'tom': 'tom_approve'}.get(required_previous)
    if not key:
        return True
    val = locks.get(key)
    return val is not None and 'PASS' in val.get('status', '')


def copy_to_new_version(folder: Path, old_tag: str, new_tag: str):
    """Vytvoří kopii MD a PDF se novým tagem."""
    for ext in ['.md', '.pdf']:
        old_files = list(folder.glob(f'*{old_tag.split("_")[0]}*{ext}'))
        for src in old_files:
            if old_tag.replace('_ASAP', '') in src.stem or 'v2fmt' in src.stem:
                continue
            dst = folder / f'{new_tag}{ext}'
            if not dst.exists():
                shutil.copy2(src, dst)
                print(f'  📄 Kopie: {src.name} → {dst.name}')


# ─── Příkazy ───────────────────────────────────────────────────────

def cmd_check(folder: Path):
    """lock check — spustí všechny forenzní kontroly."""
    print(f'\n🔍 LOCK CHECK — {folder.name}')
    print('=' * 60)

    meta = read_meta(folder)

    # Najdi aktuální MD soubor
    current_v = meta.get('aktualni_verze', '')
    md_files = list(folder.glob('*.md'))
    md_file = None
    for f in sorted(md_files, key=lambda x: x.stat().st_mtime, reverse=True):
        if 'v8' in f.name or 'F10' in f.name:
            md_file = f
            break
    if not md_file and md_files:
        md_file = md_files[0]

    if md_file:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / 'forensics.py'),
             '--md', str(md_file), '--folder', str(folder)],
            capture_output=True, text=True, encoding='utf-8'
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

    # Lock status
    result2 = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / 'audit.py'),
         '--folder', str(folder), '--status-only'],
        capture_output=True, text=True, encoding='utf-8'
    )
    print(result2.stdout)


def cmd_lock(folder: Path, lock_name: str, status: str, reason: str = '', by: str = 'proxy', dry_run: bool = False):
    """Provede lock check a zapíše výsledek (nebo pouze zobrazí v dry_run mode)."""
    meta = read_meta(folder)

    # Ověř pořadí zámků
    prev_required = {'legal': 'strat', 't002': 'legal', 'tom': 't002'}.get(lock_name)
    if prev_required and not check_lock_order(meta, prev_required):
        print(f'⛔ CHYBA: Nelze provést lock {lock_name.upper()} — předchozí zámek ({prev_required.upper()}) není PASS.')
        print(f'   Zachovej pořadí: STRAT → LEGAL → T002 → TOM')
        sys.exit(1)

    # Forenzika pro strat lock
    if lock_name == 'strat' and status == 'pass':
        md_files = sorted(folder.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)
        if md_files:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / 'forensics.py'),
                 '--md', str(md_files[0]), '--folder', str(folder), '--json'],
                capture_output=True, text=True, encoding='utf-8'
            )
            try:
                data = json.loads(result.stdout)
                if data.get('composite') == 'STOP':
                    print('⛔ FORENZIKA FAILED — nelze provést STRAT PASS:')
                    for b in data.get('markers', {}).get('hard_blocks', []):
                        print(f'  ⛔ Řádek {b["line"]}: {b["content"]}')
                    print('\n   Odstraň interní markery a opakuj.')
                    sys.exit(1)
            except json.JSONDecodeError:
                pass

    # Zapiš lock
    lock_key = {'strat': 'strat_check', 'legal': 'legal_check',
                't002': 't002_check', 'tom': 'tom_approve'}[lock_name]
    normalized = 'PASS' if status.lower() in ('pass', 'p') else 'FAIL'

    # Nová verze tag
    sym = f'{LOCK_CODES[lock_name]}+'  if normalized == 'PASS' else f'{LOCK_CODES[lock_name]}-'
    new_tag = next_version_tag(meta, sym)

    if dry_run:
        print(f'[DRY RUN] locks.{lock_key}.status = "{normalized}"')
        print(f'[DRY RUN] locks.{lock_key}.by = "{by}"')
        print(f'[DRY RUN] aktualni_verze = "{new_tag}"')
        print(f'[DRY RUN] CHANGELOG append: LOCK {lock_name.upper()} → {normalized}')
        print(f'[DRY RUN] Soubor by vznikl: {new_tag}.{{md,pdf}}')
        return

    old_stav = meta.get('stav')
    old_verze = meta.get('aktualni_verze')

    meta['locks'][lock_key] = {
        'status': normalized,
        'by': by,
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'notes': reason or f'Lock {lock_name.upper()} {normalized}',
    }
    meta['aktualni_verze'] = new_tag
    meta['versions'].append({
        'v': new_tag,
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'author': by,
        'notes': f'LOCK {lock_name.upper()} {normalized}. {reason}',
    })

    # Stav
    if normalized == 'PASS':
        next_lock = {'strat': 'waiting_legal', 'legal': 'waiting_t002',
                     't002': 'waiting_tom', 'tom': 'time_capsule'}.get(lock_name, 'done')
        meta['stav'] = next_lock

    # Atomický zápis s concurrency check
    try:
        from scripts.audit import write_meta_safe
        write_meta_safe(folder, meta, expected_stav=old_stav, expected_verze=old_verze)
    except ImportError:
        write_meta(folder, meta)
    changelog_append(folder, f'LOCK {lock_name.upper()} → {normalized} (by {by})\n  {reason}')

    sym_display = '✅' if normalized == 'PASS' else '❌'
    print(f'{sym_display} Lock {lock_name.upper()} → {normalized}')
    print(f'   Nová verze: {new_tag}')

    if normalized == 'PASS' and lock_name == 'tom':
        print(f'\n⏰ TOM APPROVE — spouštím time capsule...')
        subprocess.run([sys.executable, str(SCRIPTS_DIR / 'capsule.py'),
                        '--start', '--folder', str(folder)])

    # Routing chybových zpráv
    if normalized == 'FAIL':
        routing = {'strat': 'strat', 'legal': 'legal', 't002': 't002', 'tom': 'strat'}
        target = routing.get(lock_name, 'strat')
        print(f'\n📨 FAIL → odesílám zprávu na {target.upper()}:')
        print(f'   python L:/LG13/app/agent/instance_queue.py --send --to {target} --from-inst legal')
        print(f'   --msg "LOCK_FAIL: {lock_name.upper()} — {reason}" --priority P1')


def cmd_status(folder: Path):
    subprocess.run([sys.executable, str(SCRIPTS_DIR / 'audit.py'),
                    '--folder', str(folder), '--status-only'])

    # Capsule status
    subprocess.run([sys.executable, str(SCRIPTS_DIR / 'capsule.py'),
                    '--status', '--folder', str(folder)])


def main():
    parser = argparse.ArgumentParser(
        description='LG13 locks-workflow — 5-locks schvalovací systém',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Příklady:
  lock check --folder C:\\Users\\tom\\Documents\\podani\\0P29_2026_doplneni_c1
  lock strat pass --folder ...\\0P29_...
  lock legal fail --reason "Chybí §465c komunikační protokol" --folder ...
  lock t002 pass --by t002 --folder ...
  lock tom approve --folder ...
  lock send --folder ...
  lock status --folder ...
        """
    )
    parser.add_argument('command', choices=['check', 'strat', 'legal', 't002', 'tom', 'send', 'status', 'cancel'])
    parser.add_argument('action', nargs='?', choices=['pass', 'fail', 'submit', 'approve', 'reject'])
    parser.add_argument('--folder', type=Path, required=True, help='Složka podání')
    parser.add_argument('--reason', default='', help='Důvod (pro FAIL nebo REJECT)')
    parser.add_argument('--by', default='legal', help='Kdo provádí lock')
    parser.add_argument('--tsend-override', action='store_true', help='Přeskočit time capsule (jen Tom osobně) — NENAHRAZUJE T+ lock')
    parser.add_argument('--dry-run', action='store_true', help='Zobraz co by se zapsalo, nic nezapisuj')
    args = parser.parse_args()

    folder = args.folder
    if not folder.exists():
        print(f'⛔ Složka nenalezena: {folder}')
        sys.exit(1)

    if args.command == 'check':
        cmd_check(folder)
    elif args.command in ('strat', 'legal', 't002'):
        action = args.action or 'pass'
        if args.dry_run:
            print(f'[DRY RUN] lock {args.command} {action} --folder {folder} --by {args.by}')
            print(f'[DRY RUN] reason: {args.reason or "(none)"}')
            print(f'[DRY RUN] Spustí forenziku a zobrazí co by se zapsalo bez reálného zápisu.')
        cmd_lock(folder, args.command, action, args.reason, args.by, dry_run=args.dry_run)
    elif args.command == 'tom':
        action = args.action or 'submit'
        if action == 'submit':
            print('📋 TOM SUBMIT — draft připraven pro Tomovu kontrolu')
            cmd_status(folder)
            print('\nPo kontrole zadej: lock tom approve --folder ...')
        else:
            # Tom approve: by musí být v whitelistu
            by = args.by if args.by in ('tom', 'tom_dashboard', 'tom_direct') else 'tom'
            if args.dry_run:
                print(f'[DRY RUN] lock tom {action} --by {by}')
                print(f'[DRY RUN] Matouš guard whitelist check: {by} ✅')
            else:
                cmd_lock(folder, 'tom', action, args.reason, by, dry_run=False)
    elif args.command == 'send':
        meta = read_meta(folder)

        # Matouš guard — T+ lock musí být od Toma, TSEND override NENAHRAZUJE T+
        tom_lock = meta.get('locks', {}).get('tom_approve', {})
        if tom_lock:
            tom_by = tom_lock.get('by', '')
            if tom_by not in ('tom', 'tom_dashboard', 'tom_direct'):
                print(f'⛔ MATOUŠ GUARD: tom_approve.by="{tom_by}" není v whitelistu.')
                print('   TSEND override nenahrazuje T+ lock. Nelze odeslat.')
                sys.exit(1)
        else:
            print('⛔ SEND ODMÍTNUT: TOM lock není PASS. Nelze odeslat.')
            sys.exit(1)

        # Ověř capsule
        if not args.tsend_override:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / 'capsule.py'), '--check', '--folder', str(folder)]
            )
            if result.returncode != 0:
                subprocess.run([sys.executable, str(SCRIPTS_DIR / 'capsule.py'),
                                '--status', '--folder', str(folder)])
                print('\n⛔ Capsule ještě neuplynula. Počkej nebo použij --tsend-override (zkracuje jen C+, ne T+).')
                sys.exit(1)
        print('✅ Capsule OK — připravuji ISDS balíček...')
        # Inventář
        result2 = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / 'forensics.py'),
             '--inventory', '--folder', str(folder)],
            capture_output=True, text=True, encoding='utf-8'
        )
        print(result2.stdout)
        print('📨 Předávám t002 k odeslání přes isds_sender.py')
    elif args.command == 'status':
        if getattr(args, 'json', False):
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / 'audit.py'),
                 '--folder', str(folder), '--json'],
                capture_output=True, text=True, encoding='utf-8'
            )
            print(result.stdout)
        else:
            cmd_status(folder)
    elif args.command == 'cancel':
        meta = read_meta(folder)
        if not args.dry_run:
            meta['stav'] = 'cancelled'
            write_meta(folder, meta)
            changelog_append(folder, f'CANCELLED — {args.reason}')
        print(f'{"[DRY RUN] " if args.dry_run else ""}❌ Podání zrušeno: {args.reason}')


if __name__ == '__main__':
    main()

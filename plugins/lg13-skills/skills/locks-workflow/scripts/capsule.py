#!/usr/bin/env python3
"""
capsule.py — Time capsule logika pro locks-workflow.

Time capsule = idle lhůta po TOM approve. Zabrání unáhlenému odeslání.
ASAP podání: 5 min. Ostatní: dle adresáta (soud 60+ min).

Použití:
  python capsule.py --start --folder <cesta>          # zahájí capsule (zapíše capsule_start_ts)
  python capsule.py --status --folder <cesta>         # zbývající čas
  python capsule.py --check --folder <cesta>          # vrátí 0 pokud uplynula, 1 pokud ne
  python capsule.py --elapsed-minutes --folder <cesta> # kolik minut uběhlo
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Výchozí limity dle adresáta
DEFAULT_MINUTES = {
    'soud':   60,
    'ds':     60,
    'email':  60,
    'asap':   5,
}


def read_meta(folder: Path) -> dict:
    meta_path = folder / 'meta.json'
    return json.loads(meta_path.read_text(encoding='utf-8'))


def write_meta_field(folder: Path, key: str, value):
    meta_path = folder / 'meta.json'
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    meta[key] = value
    tmp = meta_path.with_suffix('.tmp')
    tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(meta_path)


def start_capsule(folder: Path):
    """Zapiš capsule_start_ts = now do meta.json."""
    meta = read_meta(folder)
    now = datetime.now().isoformat(timespec='seconds')
    meta['capsule_start_ts'] = now
    meta['stav'] = 'time_capsule'

    asap = meta.get('asap', False)
    minutes = meta.get('time_capsule_minutes', DEFAULT_MINUTES['asap' if asap else 'soud'])

    meta['time_capsule_minutes'] = minutes

    meta_path = folder / 'meta.json'
    tmp = meta_path.with_suffix('.tmp')
    tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(meta_path)

    print(f'⏰ CAPSULE ZAHÁJENA: {now}')
    print(f'   Délka: {minutes} min ({"ASAP" if asap else "standard"})')
    print(f'   Odeslat po: {_add_minutes(now, minutes)}')


def get_status(folder: Path) -> dict:
    meta = read_meta(folder)
    start_ts = meta.get('capsule_start_ts')
    minutes = meta.get('time_capsule_minutes', 60)
    asap = meta.get('asap', False)

    if not start_ts:
        return {'started': False, 'elapsed_min': 0, 'remaining_min': minutes, 'done': False}

    start_dt = datetime.fromisoformat(start_ts)
    elapsed = (datetime.now() - start_dt).total_seconds() / 60
    remaining = max(0.0, minutes - elapsed)
    done = remaining <= 0

    return {
        'started': True,
        'start_ts': start_ts,
        'elapsed_min': round(elapsed, 1),
        'remaining_min': round(remaining, 1),
        'total_min': minutes,
        'done': done,
        'asap': asap,
    }


def _add_minutes(iso_ts: str, minutes: int) -> str:
    from datetime import timedelta
    dt = datetime.fromisoformat(iso_ts)
    return (dt + timedelta(minutes=minutes)).strftime('%H:%M')


def main():
    parser = argparse.ArgumentParser(description='Time capsule management')
    parser.add_argument('--folder', type=Path, required=True)
    parser.add_argument('--start', action='store_true', help='Zaháj capsule')
    parser.add_argument('--status', action='store_true', help='Zobraz status')
    parser.add_argument('--check', action='store_true', help='Exit 0 pokud uplynula, 1 pokud ne')
    parser.add_argument('--elapsed-minutes', action='store_true', help='Počet uplynutých minut')
    args = parser.parse_args()

    if args.start:
        start_capsule(args.folder)

    elif args.status:
        s = get_status(args.folder)
        if not s['started']:
            print('⏳ Capsule nezahájena')
        elif s['done']:
            print(f'✅ CAPSULE UPLYNULA — {s["elapsed_min"]} min / {s["total_min"]} min')
            print('   Ready pro `lock send`')
        else:
            print(f'⏰ CAPSULE BĚŽÍ — zbývá {s["remaining_min"]} min z {s["total_min"]} min')
            print('   Ještě neodesílat!')

    elif args.check:
        s = get_status(args.folder)
        sys.exit(0 if s['done'] else 1)

    elif args.elapsed_minutes:
        s = get_status(args.folder)
        print(s['elapsed_min'])


if __name__ == '__main__':
    main()

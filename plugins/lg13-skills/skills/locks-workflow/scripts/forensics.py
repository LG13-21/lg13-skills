#!/usr/bin/env python3
"""
forensics.py — Forenzní grep pro interní markery + inventář příloh
Součást locks-workflow skill pro LG13 systém.

Použití:
  python forensics.py --md <soubor.md> [--folder <cesta-k-podani>]
  python forensics.py --inventory --folder <cesta-k-podani>
"""
import sys
import re
import json
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Interní markery, které NESMÍ být v soudním dokumentu (v prvních 30 řádcích)
# Toto jsou přesně ty vzory, co způsobily incidenty 15.4. a 16.4.2026
HARD_BLOCK_PATTERNS = [
    r'NEPOSILAT',
    r'NEPOSLAT',
    r'NEPOSÍLAT',
    r'\bSTOP\b',
    r'\bDRAFT\b',
    r'\bTBD\b',
    r'\bTODO\b',
    r'P1-\d+',           # P1-1, P1-2 tasky
    r'Verze:',
    r'faktická oprava',  # incident 16.4.
    r'factual correction',
    r'faktická korekce',
    r'\[OPRAVA\]',
    r'\[FIX\]',
    r'CHANGELOG',
    r'version\s+history',
]

# Markery hledané v celém dokumentu (méně přísné — jen warning)
SOFT_WARN_PATTERNS = [
    r'TODO',
    r'FIXME',
    r'\[PENDING\]',
    r'\[CHECK\]',
]


def check_markers(md_path: Path, header_lines: int = 30) -> dict:
    """
    Zkontroluje interní markery v MD souboru.
    Vrátí dict s 'hard_blocks' (seznam) a 'soft_warnings' (seznam).
    hard_blocks = FAIL → neodesílat
    soft_warnings = jen upozornění
    """
    text = md_path.read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()
    header = '\n'.join(lines[:header_lines])
    full = text

    hard_blocks = []
    for pattern in HARD_BLOCK_PATTERNS:
        for i, line in enumerate(lines[:header_lines], 1):
            if re.search(pattern, line, re.IGNORECASE):
                hard_blocks.append({
                    'pattern': pattern,
                    'line': i,
                    'content': line.strip()[:120],
                })

    soft_warnings = []
    for pattern in SOFT_WARN_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE) and i > header_lines:
                soft_warnings.append({
                    'pattern': pattern,
                    'line': i,
                    'content': line.strip()[:120],
                })

    return {
        'hard_blocks': hard_blocks,
        'soft_warnings': soft_warnings,
        'pass': len(hard_blocks) == 0,
    }


def check_prilohy_references(md_path: Path, prilohy_dir: Path) -> dict:
    """
    Ověří konzistenci mezi odkazem v textu (příloha č. X) a fyzickými soubory.
    """
    text = md_path.read_text(encoding='utf-8', errors='replace')

    # Najdi čísla příloh zmíněná v textu
    refs_in_text = set(re.findall(r'příloha[^\d]*č\.\s*(\d+)', text, re.IGNORECASE))
    refs_in_text |= set(re.findall(r'P(\d+)\b', text))  # zkrácená forma P1, P2

    # Fyzické soubory v prilohy/
    physical = []
    if prilohy_dir.exists():
        physical = sorted([f.name for f in prilohy_dir.glob('priloha*.pdf')])

    physical_nums = set(re.findall(r'priloha(\d+)', ' '.join(physical)))

    missing_physical = refs_in_text - physical_nums
    extra_physical = physical_nums - refs_in_text

    return {
        'refs_in_text': sorted(refs_in_text),
        'physical_files': physical,
        'physical_count': len(physical),
        'missing_physical': sorted(missing_physical),
        'extra_physical': sorted(extra_physical),
        'pass': len(missing_physical) == 0,
    }


def check_zpetvzeti(md_path: Path, meta_path: Path) -> dict:
    """
    Ověří že DM zpětvzetí z meta.json je zmíněn v textu dokumentu.
    """
    if not meta_path.exists():
        return {'skip': True, 'reason': 'meta.json nenalezen'}

    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    ds_msgs = meta.get('related_ds_messages', [])

    # Najdi zpětvzetí zprávu
    zpetvzeti = [m for m in ds_msgs if 'zpětvzetí' in m.get('subject', '').lower()
                 or 'zpetv' in m.get('note', '').lower()]

    if not zpetvzeti:
        return {'skip': True, 'reason': 'žádné zpětvzetí v meta.json'}

    text = md_path.read_text(encoding='utf-8', errors='replace')
    results = []
    for z in zpetvzeti:
        dm_id = str(z.get('dm_id', ''))
        found = dm_id in text
        results.append({'dm_id': dm_id, 'found_in_text': found})

    all_found = all(r['found_in_text'] for r in results)
    return {
        'zpetvzeti_messages': results,
        'pass': all_found,
    }


def inventory_isds_package(folder: Path) -> dict:
    """
    Inventarizace co půjde do ISDS ZIP.
    Bezpečné: pouze priloha*.pdf + finální F*.pdf
    Nebezpečné: .md, .json, CHANGELOG, meta, risk assessment, interní soubory
    """
    allowed_for_isds = []
    blocked_from_isds = []

    # Finální PDF (F*.pdf ve složce)
    for f in sorted(folder.glob('F*.pdf')):
        allowed_for_isds.append(str(f.name))

    # Přílohy
    prilohy_dir = folder / 'prilohy'
    if prilohy_dir.exists():
        for f in sorted(prilohy_dir.glob('*.pdf')):
            allowed_for_isds.append(f'prilohy/{f.name}')

    # Detekce nebezpečných souborů
    dangerous_patterns = ['*.md', '*.json', 'CHANGELOG*', '*meta*', '*risk*',
                         '*compliance*', '*.txt', '*.xlsx', '*.docx']
    for pattern in dangerous_patterns:
        for f in folder.glob(pattern):
            blocked_from_isds.append(f.name)

    return {
        'safe_for_isds': allowed_for_isds,
        'blocked': blocked_from_isds,
        'warning': len(blocked_from_isds) > 0,
    }


def main():
    parser = argparse.ArgumentParser(description='Forenzní kontrola LG13 podání')
    parser.add_argument('--md', type=Path, help='Cesta k MD souboru')
    parser.add_argument('--folder', type=Path, help='Cesta k podání složce')
    parser.add_argument('--inventory', action='store_true', help='Pouze inventář ISDS balíčku')
    parser.add_argument('--json', action='store_true', help='Výstup jako JSON')
    args = parser.parse_args()

    results = {}

    if args.inventory and args.folder:
        results['inventory'] = inventory_isds_package(args.folder)
    elif args.md:
        results['markers'] = check_markers(args.md)
        if args.folder:
            prilohy_dir = args.folder / 'prilohy'
            results['prilohy'] = check_prilohy_references(args.md, prilohy_dir)
            meta_path = args.folder / 'meta.json'
            results['zpetvzeti'] = check_zpetvzeti(args.md, meta_path)
            results['inventory'] = inventory_isds_package(args.folder)

    # Composite výsledek
    all_pass = all(
        v.get('pass', True)
        for v in results.values()
        if isinstance(v, dict) and 'pass' in v
    )
    results['composite'] = 'GO' if all_pass else 'STOP'

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"FORENZNÍ CHECK — {'✅ GO' if all_pass else '⛔ STOP'}")
        print(f"{'='*60}")

        if 'markers' in results:
            m = results['markers']
            print(f"\n[MARKERY] {'✅ PASS' if m['pass'] else '❌ FAIL'}")
            for b in m.get('hard_blocks', []):
                print(f"  ⛔ Řádek {b['line']}: {b['content']}")
            for w in m.get('soft_warnings', []):
                print(f"  ⚠️  Řádek {w['line']}: {w['content']}")

        if 'prilohy' in results:
            p = results['prilohy']
            print(f"\n[PŘÍLOHY] {'✅ PASS' if p['pass'] else '❌ FAIL'} ({p['physical_count']} fyzicky)")
            if p['missing_physical']:
                print(f"  ⛔ Chybí fyzicky: P{', P'.join(p['missing_physical'])}")
            if p['extra_physical']:
                print(f"  ⚠️  Extra bez odkazu: P{', P'.join(p['extra_physical'])}")

        if 'zpetvzeti' in results:
            z = results['zpetvzeti']
            if not z.get('skip'):
                print(f"\n[ZPĚTVZETÍ] {'✅ PASS' if z['pass'] else '❌ FAIL'}")
                for r in z.get('zpetvzeti_messages', []):
                    icon = '✅' if r['found_in_text'] else '⛔'
                    print(f"  {icon} DM {r['dm_id']}")

        if 'inventory' in results:
            inv = results['inventory']
            print(f"\n[ISDS INVENTÁŘ] {'⚠️  VAROVÁNÍ' if inv['warning'] else '✅ OK'}")
            print(f"  Bezpečné pro ISDS ({len(inv['safe_for_isds'])} souborů):")
            for f in inv['safe_for_isds']:
                print(f"    ✅ {f}")
            if inv['blocked']:
                print(f"  ⛔ NEODESÍLAT ({len(inv['blocked'])} souborů):")
                for f in inv['blocked']:
                    print(f"    ⛔ {f}")

        print()


if __name__ == '__main__':
    main()

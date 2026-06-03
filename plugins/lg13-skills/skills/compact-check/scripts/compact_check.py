"""
compact_check.py — Soft/Hard compact range checker

Zones:
  green  <soft_start     → work normally
  soft   soft_start..hard_start → plan compact (save, warn team, finish turn)
  hard   hard_start..window    → compact ASAP (save + autocompact fires)
  over   >window              → emergency (shouldn't happen)

Per-instance defaults (tokens):
  strat:  soft=180k, hard=230k, window=250k
  legal:  soft=180k, hard=230k, window=250k
  coder:  soft=160k, hard=210k, window=230k
  default: soft=170k, hard=220k, window=250k

Usage:
  python compact_check.py --ctx-now 185000 [--instance strat] [--json]
"""
import argparse, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

INSTANCE_THRESHOLDS = {
    'strat':  {'soft': 180_000, 'hard': 230_000, 'window': 250_000},
    'legal':  {'soft': 180_000, 'hard': 230_000, 'window': 250_000},
    'coder':  {'soft': 160_000, 'hard': 210_000, 'window': 230_000},
    'lmt':    {'soft': 150_000, 'hard': 200_000, 'window': 220_000},
    'web':    {'soft': 150_000, 'hard': 200_000, 'window': 220_000},
    'writer': {'soft': 150_000, 'hard': 200_000, 'window': 220_000},
    'main':   {'soft': 180_000, 'hard': 230_000, 'window': 250_000},
}
DEFAULT_THRESHOLDS = {'soft': 170_000, 'hard': 220_000, 'window': 250_000}

def detect_instance():
    cwd = os.getcwd().lower()
    for name in INSTANCE_THRESHOLDS:
        if name in cwd:
            return name
    inst_file = os.path.join(os.getcwd(), '.lg13_instance')
    if os.path.exists(inst_file):
        return open(inst_file, encoding='utf-8').read().strip()
    return 'unknown'

def check(ctx_now: int, instance: str) -> dict:
    t = INSTANCE_THRESHOLDS.get(instance, DEFAULT_THRESHOLDS)
    soft, hard, window = t['soft'], t['hard'], t['window']

    pct = round(ctx_now / window * 100, 1)
    tokens_to_soft = max(0, soft - ctx_now)
    tokens_to_hard = max(0, hard - ctx_now)
    tokens_remaining = max(0, window - ctx_now)

    avg_tok_per_turn = 5000
    turns_to_soft = round(tokens_to_soft / avg_tok_per_turn, 1)
    turns_to_hard = round(tokens_to_hard / avg_tok_per_turn, 1)
    turns_remaining = round(tokens_remaining / avg_tok_per_turn, 1)

    if ctx_now < soft:
        zone = 'green'
        action = 'work'
        recommendation = 'Pokračuj normálně.'
        compact_signal = False
        urgency = 0
    elif ctx_now < hard:
        zone = 'soft'
        action = 'plan-compact'
        recommendation = (
            f'Soft limit. Dokonči aktuální task, pak save-min + ping-pong. '
            f'Hard limit za ~{turns_to_hard} turnů ({tokens_to_hard:,} tokenů).'
        )
        compact_signal = True
        urgency = 1
    elif ctx_now < window:
        zone = 'hard'
        action = 'compact-now'
        recommendation = (
            f'Hard limit. Save-min IHNED + autocompact. '
            f'Window za ~{turns_remaining} turnů.'
        )
        compact_signal = True
        urgency = 2
    else:
        zone = 'over'
        action = 'emergency'
        recommendation = 'Přes window. Compact must have failed. Notify strat P0.'
        compact_signal = True
        urgency = 3

    return {
        'instance': instance,
        'ctx_now': ctx_now,
        'pct': pct,
        'zone': zone,
        'action': action,
        'recommendation': recommendation,
        'compact_signal': compact_signal,
        'urgency': urgency,
        'thresholds': {
            'soft': soft,
            'hard': hard,
            'window': window
        },
        'remaining': {
            'to_soft_tokens': tokens_to_soft,
            'to_hard_tokens': tokens_to_hard,
            'to_window_tokens': tokens_remaining,
            'turns_to_soft': turns_to_soft,
            'turns_to_hard': turns_to_hard,
            'turns_remaining': turns_remaining,
        }
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ctx-now', type=int, required=True,
                        help='Aktuální počet tokenů v kontextu')
    parser.add_argument('--instance', type=str, default=None,
                        help='Instance name (auto-detected z CWD pokud chybí)')
    parser.add_argument('--json', action='store_true',
                        help='Výstup jako JSON (default: human-readable)')
    args = parser.parse_args()

    instance = args.instance or detect_instance()
    result = check(args.ctx_now, instance)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        z = result
        t = z['thresholds']
        r = z['remaining']
        print(f"compact-check [{z['instance']}]")
        print(f"  ctx: {z['ctx_now']:,} / {t['window']:,} = {z['pct']}%")
        print(f"  zone: {z['zone'].upper()}  action: {z['action']}")
        print(f"  soft={t['soft']:,}  hard={t['hard']:,}  window={t['window']:,}")
        print(f"  to_soft: {r['to_soft_tokens']:,} tok ({r['turns_to_soft']} turnů)")
        print(f"  to_hard: {r['to_hard_tokens']:,} tok ({r['turns_to_hard']} turnů)")
        print(f"  recommendation: {z['recommendation']}")
        if z['compact_signal']:
            print(f"  ⚠️  compact_signal=TRUE — urgency={z['urgency']}")

if __name__ == '__main__':
    main()

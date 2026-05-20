#!/usr/bin/env bash
# Inline bash wrapper pro legal-total-analysis skill.
# Použití: bash total_analysis.sh <DAVKA_TAG>
#   např. bash total_analysis.sh F13
# Pre-flight check: folder + matrix + prehled existují, pak invoke Python helper.

set -euo pipefail

TAG="${1:-}"
if [[ -z "$TAG" ]]; then
    echo "USAGE: $0 <DAVKA_TAG>  (např. F13, F14)" >&2
    echo "  Volitelně: --root <path> --strict --quick" >&2
    exit 2
fi
shift || true

ROOT="C:/Users/tom/Documents/rizeni/pece_Matousek_909/doplneni_c1"
EXTRA=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --root) ROOT="$2"; shift 2 ;;
        --strict) EXTRA+=("--strict"); shift ;;
        --quick) EXTRA+=("--mode" "quick"); shift ;;
        --no-reuse) EXTRA+=("--no-reuse"); shift ;;
        *) EXTRA+=("$1"); shift ;;
    esac
done

FOLDER="${ROOT}/optimize_output_${TAG}"
MATRIX_CANDIDATES=(
    "${ROOT}/ARE_${TAG}_LEGAL.md"
    "${ROOT}/ARE_F11_1_LEGAL.md"
)
PREHLED_CANDIDATES=(
    "${ROOT}/F11_1_NEAPLIKOVANE_ZMENY_PREHLED.md"
    "${ROOT}/${TAG}_PREHLED.md"
)

if [[ ! -d "$FOLDER" ]]; then
    echo "FATAL: folder neexistuje: $FOLDER" >&2
    exit 2
fi

MATRIX=""
for c in "${MATRIX_CANDIDATES[@]}"; do
    [[ -f "$c" ]] && MATRIX="$c" && break
done
if [[ -z "$MATRIX" ]]; then
    echo "FATAL: matrix nenalezena. Zkoušeno: ${MATRIX_CANDIDATES[*]}" >&2
    exit 2
fi

PREHLED=""
for c in "${PREHLED_CANDIDATES[@]}"; do
    [[ -f "$c" ]] && PREHLED="$c" && break
done
if [[ -z "$PREHLED" ]]; then
    echo "FATAL: prehled nenalezen. Zkoušeno: ${PREHLED_CANDIDATES[*]}" >&2
    exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${SCRIPT_DIR}/total_analysis.py"

echo "[total-analysis] folder=$FOLDER"
echo "[total-analysis] matrix=$MATRIX"
echo "[total-analysis] prehled=$PREHLED"
echo "[total-analysis] extra=${EXTRA[*]:-}"

python "$PY" \
    --folder "$FOLDER" \
    --matrix "$MATRIX" \
    --prehled "$PREHLED" \
    "${EXTRA[@]:-}"

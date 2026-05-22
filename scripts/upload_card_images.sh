#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:8000/api/v1}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
IMAGES_DIR="${1:-${DIR:-}}"

usage() {
    cat <<'EOF'
Usage:
  scripts/upload_card_images.sh <images_dir>

Env:
  API_BASE_URL   Base API url, default: http://localhost:8000/api/v1
  PYTHON_BIN     Python executable for helper snippets, default: python3

How matching works:
  - file name without extension is matched to card title
  - matching ignores case, spaces, hyphens, underscores, and punctuation

Examples:
  scripts/upload_card_images.sh assets/cards
  API_BASE_URL=http://localhost:8000/api/v1 scripts/upload_card_images.sh img/cards
EOF
}

if [[ -z "${IMAGES_DIR}" ]]; then
    usage
    exit 1
fi

if [[ ! -d "${IMAGES_DIR}" ]]; then
    echo "Images directory not found: ${IMAGES_DIR}" >&2
    exit 1
fi

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Required command not found: $1" >&2
        exit 1
    fi
}

content_type_for() {
    local ext="$1"
    case "${ext,,}" in
        png) echo "image/png" ;;
        jpg|jpeg) echo "image/jpeg" ;;
        webp) echo "image/webp" ;;
        gif) echo "image/gif" ;;
        *) echo "" ;;
    esac
}

require_cmd curl
require_cmd "${PYTHON_BIN}"

cards_json="$(mktemp)"
payload_json="$(mktemp)"
trap 'rm -f "${cards_json}" "${payload_json}"' EXIT

echo "Fetching cards from ${API_BASE_URL}/cards"
curl -fsS "${API_BASE_URL}/cards" -o "${cards_json}"

processed=0
uploaded=0
skipped=0
failed=0

while IFS= read -r -d '' file; do
    processed=$((processed + 1))
    filename="$(basename "${file}")"
    stem="${filename%.*}"
    ext="${filename##*.}"
    content_type="$(content_type_for "${ext}")"

    if [[ -z "${content_type}" ]]; then
        echo "skip  ${filename}  unsupported extension"
        skipped=$((skipped + 1))
        continue
    fi

    match="$("${PYTHON_BIN}" - "${cards_json}" "${stem}" <<'PY'
import json
import re
import sys

cards_path = sys.argv[1]
raw_name = sys.argv[2]


def normalize(value: str) -> str:
    return re.sub(r"[^0-9a-zа-яё]+", "", value.lower())


with open(cards_path, "r", encoding="utf-8") as fh:
    cards = json.load(fh)

target = normalize(raw_name)
for card in cards:
    title = str(card["title"])
    if normalize(title) == target:
        print(f'{card["id"]}|{title}')
        break
PY
)"

    if [[ -z "${match}" ]]; then
        echo "skip  ${filename}  card not found by title"
        skipped=$((skipped + 1))
        continue
    fi

    card_id="${match%%|*}"
    card_title="${match#*|}"

    "${PYTHON_BIN}" - "${card_title}" "${filename}" "${content_type}" "${file}" > "${payload_json}" <<'PY'
import base64
import json
import sys
from pathlib import Path

title = sys.argv[1]
filename = sys.argv[2]
content_type = sys.argv[3]
file_path = Path(sys.argv[4])

payload = {
    "title": title,
    "filename": filename,
    "content_base64": base64.b64encode(file_path.read_bytes()).decode("ascii"),
    "content_type": content_type,
}

json.dump(payload, sys.stdout, ensure_ascii=False)
PY

    if curl -fsS \
        -X POST \
        "${API_BASE_URL}/cards/${card_id}/image" \
        -H "Content-Type: application/json" \
        --data @"${payload_json}" \
        >/dev/null
    then
        echo "ok    ${filename}  -> ${card_title} (${card_id})"
        uploaded=$((uploaded + 1))
        continue
    fi

    echo "fail  ${filename}  -> ${card_title} (${card_id})" >&2
    failed=$((failed + 1))
done < <(find "${IMAGES_DIR}" -maxdepth 1 -type f \( \
    -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' -o -iname '*.gif' \
\) -print0 | sort -z)

echo
echo "Summary:"
echo "  processed: ${processed}"
echo "  uploaded:  ${uploaded}"
echo "  skipped:   ${skipped}"
echo "  failed:    ${failed}"

if [[ "${failed}" -gt 0 ]]; then
    exit 1
fi

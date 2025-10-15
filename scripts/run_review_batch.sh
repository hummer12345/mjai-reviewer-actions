#!/usr/bin/env bash
set -euo pipefail
LIST_FILE="${1:-logs/list.txt}"
OUT_DIR="${2:-reports/$(date +%Y%m)}"
SKIP_EXISTING="${SKIP_EXISTING:-1}"
processed=0

if [[ ! -f "$LIST_FILE" ]]; then
  echo "Not found: $LIST_FILE" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

idx=0
while IFS= read -r url; do
  # 空行・コメント行はスキップ
  if [[ -z "${url// }" ]] || [[ "$url" =~ ^# ]]; then
    continue
  fi

  # 対局IDをファイル名に取り出す（log=XXXX 部分）
  gid="game_${idx}"
  if [[ "$url" =~ log=([^&]+) ]]; then
    gid="${BASH_REMATCH[1]}"
  fi

  target_dir="${OUT_DIR}/${gid}"
  target_index="${target_dir}/index.html"
  mkdir -p "$target_dir"

  if [[ "$SKIP_EXISTING" == "1" && -s "$target_index" ]]; then
    echo "[mjai-reviewer] skip existing report -> ${target_index}"
    idx=$((idx+1))
    continue
  fi

  echo "[mjai-reviewer] $url -> ${target_index}"

  # HTMLを標準出力に出す(-o -)ので、ファイルに保存
  mjai-reviewer -e akochan --no-open -u "$url" -o - > "$target_index"
  processed=$((processed+1))

  idx=$((idx+1))
done < "$LIST_FILE"

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  if (( processed > 0 )); then
    echo "new_reports=true" >> "$GITHUB_OUTPUT"
    echo "processed_count=${processed}" >> "$GITHUB_OUTPUT"
  else
    echo "new_reports=false" >> "$GITHUB_OUTPUT"
    echo "processed_count=0" >> "$GITHUB_OUTPUT"
  fi
fi

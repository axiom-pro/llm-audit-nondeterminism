#!/usr/bin/env bash
# M2 本計測 v2（監査反映）: 是正ターゲット + easy追加。
# 各セル前に ollama stop でモデルを unload → cold reload で cross-cell KV 状態を独立化。
# 既存 fixtures は上書きせず .prev へ退避（凍結データ損失ガード）。
set -e
cd "$(dirname "$0")"
OUT="../fixtures/audit_logs.jsonl"
OLLAMA_EXE="${OLLAMA_EXE:-ollama}"   # 公開用: 絶対パスを埋めない。ローカルは `OLLAMA_EXE=/path/to/ollama.exe` で上書き
PY="python"
M15="qwen2.5-coder:1.5b"
M7="qwen2.5-coder:7b"
NEXP=51
NBASE=11

if [ -f "$OUT" ]; then echo "backup $OUT -> $OUT.prev"; mv "$OUT" "$OUT.prev"; fi

cold() { "$OLLAMA_EXE" stop "$1" >/dev/null 2>&1 || true; }         # unload for independence

cell() {  # cell MODEL TARGET TEMP SEEDMODE N LABEL
  cold "$1"
  PYTHONUTF8=1 $PY audit_run.py --out "$OUT" --model "$1" --target "../targets/$2" \
    --temp "$3" --seed-mode "$4" --thread 4 --n "$5" --cell "$6"
}

# --- 探索条件 temp0.7 (N=51) ---
cell "$M15" target_a.py     0.7 vary $NEXP d_15b_a
cell "$M15" target_clean.py 0.7 vary $NEXP d_15b_clean
cell "$M15" target_decoy.py 0.7 vary $NEXP d_15b_decoy
cell "$M15" target_easy.py  0.7 vary $NEXP d_15b_easy
cell "$M7"  target_a.py     0.7 vary $NEXP d_7b_a
cell "$M7"  target_clean.py 0.7 vary $NEXP d_7b_clean
cell "$M7"  target_decoy.py 0.7 vary $NEXP d_7b_decoy
cell "$M7"  target_easy.py  0.7 vary $NEXP d_7b_easy

# --- temp0 基準 (決定性・N=11) ---
cell "$M15" target_a.py    0 fixed $NBASE a_15b_a
cell "$M15" target_easy.py 0 fixed $NBASE a_15b_easy
cell "$M7"  target_a.py    0 fixed $NBASE a_7b_a
cell "$M7"  target_easy.py 0 fixed $NBASE a_7b_easy

echo "=== AGGREGATE ==="
PYTHONUTF8=1 $PY aggregate.py --json-out ../results/m2_summary.json
echo "M2 v2 ALL DONE -> $OUT"

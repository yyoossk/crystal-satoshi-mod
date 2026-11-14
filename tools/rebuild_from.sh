#!/bin/bash
# build_all.sh の 第N弾から 後だけ（前の ROM は build/ に ある もの）
set -e
N=$1
ROOT=$(cd "$(dirname "$0")/.." && pwd); cd "$ROOT/tools"
grep -E "^python3 build_phase[0-9]+\.py" build_all.sh | while read -r line; do
  k=$(echo "$line" | sed -E 's/^python3 build_phase([0-9]+)\.py.*/\1/')
  if [ "$k" -ge "$N" ]; then echo "== $k"; eval "${line%%#*}" > ../build/log_p$k.txt 2>&1 || { echo "FAIL $k"; tail -20 ../build/log_p$k.txt; exit 1; }; fi
done
cp ../build/p84.gbc "../build/クリスタル_サトシMOD.gbc"
echo DONE

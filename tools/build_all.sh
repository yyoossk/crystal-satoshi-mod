#!/bin/bash
# クリスタル サトシMOD 一括ビルド
#   ベース = 日本版クリスタル + 第7弾 IPS（第1〜9弾の内容）→ 第10〜16弾を順に当てる
#   できあがり: build/クリスタル_サトシMOD.gbc
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd); cd "$ROOT/tools"
mkdir -p ../build
python3 apply_ips.py "../crystal/Pocket Monsters - Crystal Version (Japan).gbc" "../base/クリスタル_サトシMOD_第7弾.ips" ../build/p9.gbc
python3 build_phase10.py ../build/p9.gbc  ../build/p10.gbc ../build/p10.ips   # トレーナーの絵
python3 build_phase11.py ../build/p10.gbc ../build/p11.gbc ../build/p11.ips   # ポケモンタワー
python3 build_phase12.py ../build/p11.gbc ../build/p12.gbc ../build/p12.ips   # ゲームコーナー・アジト・大事な道具・タワーの野生・ラジオ塔
python3 build_phase13.py ../build/p12.gbc ../build/p13.gbc ../build/p13.ips   # ゆうれい戦・サカキの見た目・トレーナーデータ移動
python3 build_phase14.py ../build/p13.gbc ../build/p14.gbc ../build/p14.ips   # シルフカンパニー
python3 build_phase15.py ../build/p14.gbc ../build/p15.gbc ../build/p15.ips   # フラグ拡張・おつきみやま
python3 build_phase16.py ../build/p15.gbc ../build/p16.gbc ../build/p16.ips   # サントアンヌ号・船着き場・マサキの家
python3 build_phase17.py ../build/p16.gbc ../build/p17.gbc ../build/p17.ips   # シゲル（研究所・22番道路×2・ハナダ）・トキワジムのサカキ
python3 build_phase18.py ../build/p17.gbc ../build/p18.gbc ../build/p18.ips   # ヤマブキのロケット団
cp ../build/p18.gbc "../build/クリスタル_サトシMOD.gbc"
python3 -c "import zlib,sys;print('CRC32 %08X' % zlib.crc32(open(sys.argv[1],'rb').read()))" "../build/クリスタル_サトシMOD.gbc"

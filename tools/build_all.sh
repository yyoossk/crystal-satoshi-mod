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
python3 build_phase19.py ../build/p18.gbc ../build/p19.gbc ../build/p19.ips   # グレンじま（町・ポケモンやしき・研究所・ジム・ショップ）
python3 build_phase20.py ../build/p19.gbc ../build/p20.gbc ../build/p20.ips   # 無人発電所
python3 build_phase21.py ../build/p20.gbc ../build/p21.gbc ../build/p21.ips   # ふたごじま
python3 build_phase22.py ../build/p21.gbc ../build/p22.gbc ../build/p22.ips   # 20ばんすいどう
python3 build_phase23.py ../build/p22.gbc ../build/p23.gbc ../build/p23.ips   # チャンピオンロード（シルバー戦も）
python3 build_phase24.py ../build/p23.gbc ../build/p24.gbc ../build/p24.ips   # 23ばんどうろ（見張り7人）・セキエイこうげん
python3 build_phase25.py ../build/p24.gbc ../build/p25.gbc ../build/p25.ips   # ハナダシティ（赤）・家・自転車屋・ハナダのどうくつ
python3 build_phase26.py ../build/p25.gbc ../build/p26.gbc ../build/p26.ips   # ニビシティ（赤）・ニビかがくはくぶつかん
python3 build_phase27.py ../build/p26.gbc ../build/p27.gbc ../build/p27.ips   # 2ばんどうろ（赤）・トキワのもり・ゲート・いあいぎり
python3 build_phase28.py ../build/p27.gbc ../build/p28.gbc ../build/p28.ips   # サファリゾーン（赤）・サファリゲーム・きんのいれば
python3 build_phase29.py ../build/p28.gbc ../build/p29.gbc ../build/p29.ips   # トキワシティ（赤）・とどけもの・ずかん・つなぎ目の描き直し
python3 build_phase30.py ../build/p29.gbc ../build/p30.gbc ../build/p30.ips   # 1ばんどうろ・マサラタウン（赤）・オーキドに連れられて研究所へ・段差
python3 build_phase31.py ../build/p30.gbc ../build/p31.gbc ../build/p31.ips   # 22ばんどうろ（赤）・シゲルの待ち位置・ゲートの見張り（グレーバッジ）
python3 build_phase32.py ../build/p31.gbc ../build/p32.gbc ../build/p32.ips   # 3・4ばんどうろ（赤）・おつきみやまポケモンセンター
python3 build_phase33.py ../build/p32.gbc ../build/p33.gbc ../build/p33.ips   # 24・25・9・10ばんどうろ（赤）・ゴールデンボール橋
python3 build_phase34.py ../build/p33.gbc ../build/p34.gbc ../build/p34.ips   # 5〜8ばんどうろ（赤）・ヤマブキのゲート（のどが渇いた見張り）
cp ../build/p34.gbc "../build/クリスタル_サトシMOD.gbc"
python3 -c "import zlib,sys;print('CRC32 %08X' % zlib.crc32(open(sys.argv[1],'rb').read()))" "../build/クリスタル_サトシMOD.gbc"

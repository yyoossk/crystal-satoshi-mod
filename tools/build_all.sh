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
python3 build_phase35.py ../build/p34.gbc ../build/p35.gbc ../build/p35.ips   # 11〜15ばんどうろ（赤）・ゲート・カビゴンとポケモンのふえ・ディグダのあな入口
python3 build_phase36.py ../build/p35.gbc ../build/p36.gbc ../build/p36.ips   # 16〜19・21ばんどうろ（赤）・サイクリングロードのゲート・カビゴン・そらをとぶの家
python3 build_phase37.py ../build/p36.gbc ../build/p37.gbc ../build/p37.ips   # クチバシティ（赤）・船のチケットの確認・ポッポの家・つりおやじ・交換の家
python3 build_phase38.py ../build/p37.gbc ../build/p38.gbc ../build/p38.ips   # セキチクシティ（赤）・展示のポケモンと図鑑・マサキのおじいさんの家・いいつりざお
python3 build_phase39.py ../build/p38.gbc ../build/p39.gbc ../build/p39.ips   # シオンタウン（赤）・フジ老人のポケモンハウス・カラカラの家
python3 build_phase40.py ../build/p39.gbc ../build/p40.gbc ../build/p40.ips   # タマムシシティ（赤）・食堂（コインケース）・ゲームコーナー社長の家・ホテル
python3 build_phase41.py ../build/p40.gbc ../build/p41.gbc ../build/p41.ips   # タマムシデパート・タマムシマンション（赤）・イーブイ・しょうじょう
python3 build_phase42.py ../build/p41.gbc ../build/p42.gbc ../build/p42.ips   # ヤマブキシティ（赤）・ロケット団の占拠・かくとう道場・ものまね娘・ポッポの家
python3 build_phase43.py ../build/p42.gbc ../build/p43.gbc ../build/p43.ips   # 地下通路（赤）・5〜8ばんどうろの入口・ニドラン交換
python3 build_phase44.py ../build/p43.gbc ../build/p44.gbc ../build/p44.ips   # かくとう道場・ものまね娘の家（赤の部屋）・タイルセットの色を表にまとめる
python3 build_phase45.py ../build/p44.gbc ../build/p45.gbc ../build/p45.ips   # サント・アンヌ号の出航・船のシゲルが立ち去る
python3 build_phase46.py ../build/p45.gbc ../build/p46.gbc ../build/p46.ips   # イワヤマトンネル・ディグダのあな・5ばんどうろの育て屋（赤）・29ばんどうろの修正
python3 build_phase47.py ../build/p46.gbc ../build/p47.gbc ../build/p47.ips   # 殿堂入りのあと：マサラから再開・オーキドのチケット・ワカバタウンへの船・ヒビキの家と母・シロガネやまのヒビキ
python3 build_phase48.py ../build/p47.gbc ../build/p48.gbc ../build/p48.ips   # ポケモンじいさんの家のオーキド・リーグの切り替え（ライジングバッジ）・ジョウトのムサシとコジロウ
python3 build_phase49.py ../build/p48.gbc ../build/p49.gbc ../build/p49.ips   # ジョウトのセリフ（ウツギはかせ・じょしゅ・ワカバの女の人・お母さんの電話など）
python3 build_phase50.py ../build/p49.gbc ../build/p50.gbc ../build/p50.ips   # ジョウトの殿堂入りのあと：カントーのジムリーダーと再戦（クリスタルの手持ち）
python3 build_phase51.py ../build/p50.gbc ../build/p51.gbc ../build/p51.ips   # グリーンをシゲルに統一（トキワジム・電話）
python3 build_phase52.py ../build/p51.gbc ../build/p52.gbc ../build/p52.ips   # ライバル（シゲル）の名前を自由に：赤のオーキドの話で名前を決める
python3 build_phase53.py ../build/p52.gbc ../build/p53.gbc ../build/p53.ips   # オープニングを赤フルカラーから（コピーライト・ゲームフリーク・ゲンガーとニドリーノ・タイトル・曲と効果音）
python3 build_phase54.py ../build/p53.gbc ../build/p54.gbc ../build/p54.ips   # カントーの殿堂入りとスタッフロールを赤どおりに・戦闘後のセリフの不具合・前のセーブのライバル名
python3 build_phase55.py ../build/p54.gbc ../build/p55.gbc ../build/p55.ips   # カントーのジムを赤どおりに（ジムリーダーのセリフ・わざマシン・セキチクはキョウ・ジムの案内人）・はしごで壁に埋まる不具合
python3 build_phase56.py ../build/p55.gbc ../build/p56.gbc ../build/p56.ips   # ムサシとコジロウのマップの絵と色をピカチュウ・フルカラーから
python3 build_phase57.py ../build/p56.gbc ../build/p57.gbc ../build/p57.ips   # 151匹そろう版（カントーの野生・つり・カセキ2つ・どうじょう2匹・イーブイ3匹・Lv37進化）・もらうポケモンの不具合・トキワのもりの野生
python3 build_phase58.py ../build/p57.gbc ../build/p58.gbc ../build/p58.ips   # フシギダネ・ヒトカゲ・ゼニガメをピカチュウ版どおりにもらえる（ハナダのメラニー・24ばんどうろ・クチバのジュンサーさん）
python3 build_phase59.py ../build/p58.gbc ../build/p59.gbc ../build/p59.ips   # タマムシのけいひんをピカチュウ版どおりに（ケーシィ・ロコン・プクリン・ストライク・カイロス・ポリゴン）
python3 build_phase60.py ../build/p59.gbc ../build/p60.gbc ../build/p60.ips   # ジョウトは第二世代だけ（野生・つり・ずつき・いわくだき・むしとり・もらう・止まっている・景品・交換）
python3 build_phase61.py ../build/p60.gbc ../build/p61.gbc ../build/p61.ips   # 御三家・セレビィキット：セレビィ（鳥なし、$47:$7E40 へ）・ジョウトの御三家3びき（rgbds 1.0.4）
python3 build_phase62.py ../build/p61.gbc ../build/p62.gbc ../build/p62.ips   # 御三家・セレビィ・交換進化キット：交換進化だけ（ほかは入っている）
python3 build_phase63.py ../build/p62.gbc ../build/p63.gbc ../build/p63.ips   # セレビィ：つかまえていなければ つぎの殿堂入りで また出る
python3 build_phase64.py ../build/p63.gbc ../build/p64.gbc ../build/p64.ips   # クリスタル追加機能キット（全機能・60fps・バグ修正）：4MB に（rgbds 1.0.4）
python3 build_phase65.py ../build/p64.gbc ../build/p65.gbc ../build/p65.ips   # サファリゾーンで のこりの 歩数と ボールを いつも 表示（キットの SafariHUD を MOD の サファリに）
cp ../build/p65.gbc "../build/クリスタル_サトシMOD.gbc"
python3 -c "import zlib,sys;print('CRC32 %08X' % zlib.crc32(open(sys.argv[1],'rb').read()))" "../build/クリスタル_サトシMOD.gbc"

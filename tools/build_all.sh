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
python3 build_phase66.py ../build/p65.gbc ../build/p66.gbc ../build/p66.ips   # ムサシとコジロウの戦闘の絵を2色に（コジロウは青紫・ムサシは赤紫の髪。ピカチュウフルカラーと同じ）
python3 build_phase67.py ../build/p66.gbc ../build/p67.gbc ../build/p67.ips   # $80 以降の バンクの スクリプトが サブスクリプトから 正しく もどる（連れ歩きに 話しかけた とき など）
python3 build_phase68.py ../build/p67.gbc ../build/p68.gbc ../build/p68.ips   # オープニングと タイトルの 曲・効果音を 赤（日本版）の 音の しくみで（赤の バンク $1F を $9D に）
python3 build_phase69.py ../build/p68.gbc ../build/p69.gbc ../build/p69.ips   # カントー（赤の マップ）の 段差を 赤と 同じに（手前から とびこえる・ほかの 向きは かべ）
python3 build_phase70.py ../build/p69.gbc ../build/p70.gbc ../build/p70.ips   # 曲が 元に もどる・お母さんの 所へ 歩いて ポケギア・シゲルの ねえさんが ポケギアに タウンマップ
python3 build_phase71.py ../build/p70.gbc ../build/p71.gbc ../build/p71.ips   # 主人公の見た目を赤フルカラーと同じに（フィールド・自転車・名前の画面・戦闘の後ろ姿・トレーナーカード・色）
python3 build_phase72.py ../build/p71.gbc ../build/p72.gbc ../build/p72.ips   # サトシの部屋の PC・ファミコン、1階の テレビ、オーキド研究所の PC の メールを 赤と 同じに
python3 build_phase73.py ../build/p72.gbc ../build/p73.gbc ../build/p73.ips   # カントーの ポケモンセンターの 人と ことばを 赤と 同じに
python3 build_phase74.py ../build/p73.gbc ../build/p74.gbc ../build/p74.ips   # 負けた 戦いの あと 次の トレーナーで リセットされる 不具合を なおす
python3 build_phase75.py ../build/p74.gbc ../build/p75.gbc ../build/p75.ips   # カントーの フレンドリィショップの 人と ことばを 赤と 同じに・おつきみやまの わざマシンを 12に
python3 build_phase76.py ../build/p75.gbc ../build/p76.gbc ../build/p76.ips   # 怪力の 岩が 赤と 同じく 段差を こえて 動く（チャンピオンロード 3F）
python3 build_phase77.py ../build/p76.gbc ../build/p77.gbc ../build/p77.ips   # 赤と 同じく 東の 岸（タイル $32）を なみのりで 進める（19・20ばんどうろ）
python3 build_phase78.py ../build/p77.gbc ../build/p78.gbc ../build/p78.ips   # カントーでは 野生の ポケモンが にげださない（赤と 同じ。サンダーなど）
python3 build_phase79.py ../build/p78.gbc ../build/p79.gbc ../build/p79.ips   # 赤の カウンター ごしに 話せる（ハナダの じてんしゃや・シオンタワー・シルフなど）
python3 build_phase80.py ../build/p79.gbc ../build/p80.gbc ../build/p80.ips   # 殿堂入りの あと クチバの みなとの とおりみちの ワープが きえていた 不具合を なおす（第75弾の 影響）
python3 build_phase81.py ../build/p80.gbc ../build/p81.gbc ../build/p81.ips   # はじめての ふねで まごむすめが もどったときの とうちゃくの ことばを ワカバタウンに
python3 build_phase82.py ../build/p81.gbc ../build/p82.gbc ../build/p82.ips   # ロケットだんの ラジオとう せんきょなどは ジョウトの バッジの かずだけで きめる
python3 build_phase83.py ../build/p82.gbc ../build/p83.gbc ../build/p83.ips   # カントーの チャンピオンの サトシに あわない ものがたりの ことばを なおす
python3 build_phase84.py ../build/p83.gbc ../build/p84.gbc ../build/p84.ips   # ジョウトの バッジ 8こで オーキドが シロガネやまを ひらく
python3 build_phase85.py ../build/p84.gbc ../build/p85.gbc ../build/p85.ips   # こうそくせんの はじめての こうかいの あとしまつ（おじいさんの さわぎを くりかえさない）
python3 build_phase86.py ../build/p85.gbc ../build/p86.gbc ../build/p86.ips   # ジョウトの でんどういりの あと リニアが うごく（ヤマブキの えき・モノマネむすめの ていきけん）
python3 build_phase87.py ../build/p86.gbc ../build/p87.gbc ../build/p87.ips   # カントーの ジムりーダーの さいせんの ことば（3ねんご）・カツラの さいせん（ふたごじま）
python3 build_phase88.py ../build/p87.gbc ../build/p88.gbc ../build/p88.ips   # 3ねんごの カントーの ジム（トキワは シゲルの ジム・ニビの あんないにん）
python3 build_phase89.py ../build/p88.gbc ../build/p89.gbc ../build/p89.ips   # カントーの 町（クチバ・シオン・タマムシ・ヤマブキ）へ 建物から 出るのが 遅かった（人の 絵の 読みなおし）
python3 build_phase90.py ../build/p89.gbc ../build/p90.gbc ../build/p90.ips   # 研究所の さいしょの バトルの あとの 連れ歩きが こわれた ピカチュウに なる 不具合
python3 build_phase91.py ../build/p90.gbc ../build/p91.gbc ../build/p91.ips   # シゲル戦と 負けたときを 赤と 同じに（マサラタウンの 家の 前に もどる・負けたときの ことば）
python3 build_phase92.py ../build/p91.gbc ../build/p92.gbc ../build/p92.ips   # カントーの 町・道路の 地名の 看板の 色を クリスタルと 同じに
python3 build_phase93.py ../build/p92.gbc ../build/p93.gbc ../build/p93.ips   # ポケモンの 入った ボール（研究所・イーブイ・かくとう道場）と セキチクの ビリリダマの 見た目（ピカチュウフルカラー）
python3 build_phase94.py ../build/p93.gbc ../build/p94.gbc ../build/p94.ips   # ボールを 選ぶ ときの ポケモンの 絵を カラーに
python3 build_phase95.py ../build/p94.gbc ../build/p95.gbc ../build/p95.ips   # マップの つながり（マサラタウン ⇔ 1ばんどうろ など）で 止まる 不具合（人の 絵の 読みなおし）
python3 build_phase96.py ../build/p95.gbc ../build/p96.gbc ../build/p96.ips   # 建物の 出入りを はやく（ドアの 暗く・明るく なる 時間を 半分に）
python3 build_phase97.py ../build/p96.gbc ../build/p97.gbc ../build/p97.ips   # カントーの 町・道路も 朝・昼・夜で 色が かわる（クリスタルと 同じ）
python3 build_phase98.py ../build/p97.gbc ../build/p98.gbc ../build/p98.ips   # シゲルが 出てくる・去る ときの 曲を 赤の「ライバルあらわる」に（赤の 音の しくみ）
python3 build_phase99.py ../build/p98.gbc ../build/p99.gbc ../build/p99.ips   # シゲルの フィールドの 絵の 色を 赤フルカラーと 同じ 青に
python3 build_phase100.py ../build/p99.gbc ../build/p100.gbc ../build/p100.ips   # ずかんの ぶんぷは いる 地方の 地図から（ジョウトは 着いてから）・ずかんは さいしょ 番号順
python3 build_phase101.py ../build/p100.gbc ../build/p101.gbc ../build/p101.ips   # おつきみやま などの 地名（看板）と 洞くつでの 看板の 色
python3 build_phase102.py ../build/p101.gbc ../build/p102.gbc ../build/p102.ips   # トキワのもり（と ディグダのあな・ふたごじま）の 曲を 赤と 同じに
python3 build_phase103.py ../build/p102.gbc ../build/p103.gbc ../build/p103.ips   # ムサシとコジロウは 戦いの あと 暗く なって から いなく なる（ピカチュウ版と 同じ）
python3 build_phase104.py ../build/p103.gbc ../build/p104.gbc ../build/p104.ips   # カントーの トレーナーは 勝っても 消えない・ハナダの ショップ・マサキの 家（ピカチュウ版と 同じ 動き）
python3 build_phase105.py ../build/p104.gbc ../build/p105.gbc ../build/p105.ips   # 新しい トレーナーの 種類（ギャンブラー・でんきやのオヤジ など）に 見つかった ときの 曲
python3 build_phase106.py ../build/p105.gbc ../build/p106.gbc ../build/p106.ips   # サントアンヌごうの かんぱんの 扉（右へ 歩いて 船の 中へ もどれる）
python3 build_phase107.py ../build/p106.gbc ../build/p107.gbc ../build/p107.ips   # サントアンヌごうが さる ところ（波の 動き・けむりの 色を 赤フルカラーと 同じに）
python3 build_phase108.py ../build/p107.gbc ../build/p108.gbc ../build/p108.ips   # クチバジムの マチスの 前の 扉（赤と 同じ 2まいの 扉）
python3 build_phase109.py ../build/p108.gbc ../build/p109.gbc ../build/p109.ips   # ポケギアの タウンマップ（カントーで 下を 押しても ジョウトの 地名に 行かない）
python3 build_phase110.py ../build/p109.gbc ../build/p110.gbc ../build/p110.ips   # 2026/11/16 の 報告（ショップ・どく・マサキの 電話・連れ歩きの 列・ほか）
python3 build_phase111.py ../build/p110.gbc ../build/p111.gbc ../build/p111.ips   # ゲートの 入口の 横の かべ
python3 build_phase112.py ../build/p111.gbc ../build/p112.gbc ../build/p112.ips   # カントーの ジムを 赤の 部屋に
python3 build_phase113.py ../build/p112.gbc ../build/p113.gbc ../build/p113.ips   # なみのりで マップの つなぎめを こえる
python3 build_phase114.py ../build/p113.gbc ../build/p114.gbc ../build/p114.ips   # ヤマブキジムの ワープ床
python3 build_phase115.py ../build/p114.gbc ../build/p115.gbc ../build/p115.ips   # ジョウトで ひでんマシンを 二重に もらわない
python3 build_phase116.py ../build/p115.gbc ../build/p116.gbc ../build/p116.ips   # 殿堂入り後の チャンピオンロードは 岩なしで 通れる
python3 build_phase117.py ../build/p116.gbc ../build/p117.gbc ../build/p117.ips   # ジョウトの 殿堂入り後の おつきみやまの ライバル
python3 build_phase118.py ../build/p117.gbc ../build/p118.gbc ../build/p118.ips   # グリーン（再戦）の レベルを クリスタルどおりに
python3 build_phase119.py ../build/p118.gbc ../build/p119.gbc ../build/p119.ips   # クリスタル元からの バグ（たたかい・AI）
python3 build_phase120.py ../build/p119.gbc ../build/p120.gbc ../build/p120.ips   # クリスタル元からの バグ（そのほか）
python3 build_phase121.py ../build/p120.gbc ../build/p121.gbc ../build/p121.ips   # クリスタル元からの バグ（こんらん・イブキ・マニア・いろ）
python3 build_phase122.py ../build/p121.gbc ../build/p122.gbc ../build/p122.ips   # ジムの 案内の 人が 赤の わざマシンの わざを おしえる
python3 build_phase123.py ../build/p122.gbc ../build/p123.gbc ../build/p123.ips   # 報告の直し（はじめの部屋・テキスト・シゲル・オーキド・連れ歩き・研究所・タイムカプセルの道具）
cp ../build/p123.gbc "../build/クリスタル_サトシMOD.gbc"
python3 -c "import zlib,sys;print('CRC32 %08X' % zlib.crc32(open(sys.argv[1],'rb').read()))" "../build/クリスタル_サトシMOD.gbc"

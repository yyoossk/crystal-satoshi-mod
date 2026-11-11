クリスタル サトシMOD ソース一式
================================

このフォルダの build_all.sh を動かすと、いまの ROM と同じものができます。
（できあがり: build/クリスタル_サトシMOD.gbc）

■ 中身
  tools/   ビルド用の Python スクリプト（第10〜48弾）と build_all.sh
  base/    第7弾の IPS（第1〜9弾の内容。これを当てたものが土台）
  out/     ピカチュウフルカラーから取り出したタイルセット・ゆうれいの絵・空きフラグ表

■ 自分で用意するもの（著作物のため入っていません）
  crystal/Pocket Monsters - Crystal Version (Japan).gbc   日本版クリスタル
  pkfc/pkfc.gbc                                            ポケットモンスターピカチュウフルカラー
  aka/Pocket Monsters - Aka (Japan) (SGB Enhanced).gb      ポケットモンスター赤（セリフの取り出し用）
  safref/ref.gbc                                           サファリゾーン入りの日本版クリスタル改造ロム（サファリのバトル部分の取り出し用・第28弾）
  ref/pokecrystal  https://github.com/pret/pokecrystal  3c813b0b4d82b39bf62185aceffb76fd6026c70b（make してできる pokecrystal.gbc と tools/lzcompress を使う）
  ref/pokered      https://github.com/pret/pokered      c5d8f2bdb34771527f0507e48e5f3a4308acd4d9
  ref/pokeyellow   https://github.com/pret/pokeyellow   ca1e8ba5c866e02cfa350ec9b3e5ce2e92f9ac39（make してできる pokeyellow.sym を使う）
  ※ make には RGBDS v1.0.4 を使いました

■ ビルド
  Python 3 を入れて、
    bash tools/build_all.sh

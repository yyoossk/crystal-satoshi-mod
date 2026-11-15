#!/usr/bin/env python3
"""ブログ用 HTML（画像入り）：ポケットモンスター クリスタル カントー＆ジョウト
「クリスタル 追加機能パッチ」のブログ用 HTML（引数1）を手本にして作る。共通の機能の節・画像はそこから使う。"""
import base64, io, re, sys, zlib, hashlib
from PIL import Image
R = '/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/run/'
SC = '/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/'
NAME = 'ポケットモンスター クリスタル カントー＆ジョウト'
VER = '1.1.0'
HISTORY = [   # 新しい 順（日付, 版, 内容の リスト）
    ('2026/11/15', '1.1.0', ['カントーの町・道路も、朝・昼・夜で色が変わるようにしました',
                             'シゲルが出てくるとき・去るときの曲を、赤と同じシゲルの曲にしました',
                             'シゲルのフィールドの色を、赤フルカラーと同じにしました',
                             'トキワのもり・ディグダのあな・ふたごじまの曲を、赤と同じにしました',
                             'マップのつなぎめで一瞬止まるのを直しました。建物の出入りを速くしました',
                             'ずかんの「ぶんぷ」を、いる地方の地図から出すようにしました。ぶんぷでSTARTを押すと固まるのを直しました',
                             'ずかんの並びを、はじめから番号順にしました',
                             'おつきみやまなどで地名の看板がちがうのと、洞くつでの看板の色を直しました',
                             '手持ちで連れ歩きをやめると、持っていないピカチュウが出るのを直しました',
                             'ムサシとコジロウが、戦いのあと急に消えないようにしました（ピカチュウ版と同じ）',
                             'カントーのトレーナーが、勝ったあとに消えてしまうのを直しました',
                             'ハナダのショップで、店員の前に人が立って買えないのを直しました',
                             'マサキの家のイベントの動きを、ピカチュウ版と同じにしました',
                             'ギャンブラーなどのトレーナーに見つかったとき、曲が鳴らないのを直しました',
                             'サントアンヌごう：かんぱんから戻れない・階段で移動できないのを直しました。船が去るときの波とけむりを赤フルカラーと同じにしました',
                             'クチバジムのマチスの前の扉を、赤と同じにしました',
                             'ポケギアのタウンマップで↓を押し続けると、ジョウトの地名に入ってしまうのを直しました']),
    ('2026/11/15', '1.0.0', ['初回リリース']),
]
ROM = open(SC + 'build/p109.gbc', 'rb').read()
CRC = '%08X' % zlib.crc32(ROM); SHA = hashlib.sha1(ROM).hexdigest()
REF = open(sys.argv[1], encoding='utf-8').read()

H2S = 'margin:36px 0 12px;padding:10px 14px;font-size:21px;color:#fff;background:linear-gradient(90deg,#0e3a66,#2b7bb9);border-radius:6px;border-left:8px solid #9ad8f5;'
H3S = 'margin:24px 0 8px;padding:4px 0 4px 10px;font-size:18px;color:#0e3a66;border-left:5px solid #2b7bb9;border-bottom:1px dashed #8cc8e6;'
def H2(t): return f'<h2 style="{H2S}">{t}</h2>'
def H3(t): return f'<h3 style="{H3S}">{t}</h3>'
def P(t): return f'<p style="line-height:1.85;margin:8px 0;">{t}</p>'
def UL(items): return '<ul style="line-height:1.85;margin:6px 0 10px;">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
def BOX(t): return f'<div style="border:2px solid #2b7bb9;background:#eaf7fd;border-radius:8px;padding:10px 14px;margin:12px 0;line-height:1.85;">{t}</div>'


def uri(path, scale=2):
    im = Image.open(R + path).convert('RGB')
    if scale != 1: im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


def IMG(*paths, cap=None):
    imgs = ''.join(f'<img src="{uri(p)}" alt="" width="320" height="288" style="width:320px;max-width:100%;height:auto;image-rendering:pixelated;border:3px solid #8cc8e6;border-radius:4px;background:#000;" />' for p in paths)
    c = f'<div style="text-align:center;font-size:13px;color:#3d6480;margin:-4px 0 10px;">{cap}</div>' if cap else ''
    return f'<div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:12px 0;">{imgs}</div>' + c


# ---- 手本の「追加した機能」の節（番号 → html）
a = REF.index('>追加した機能</h2>'); a = REF.index('<h3', a)
b = REF.index('<h2', a)
body = REF[a:b]
secs = {}
for m in re.finditer(r'<h3[^>]*>(\d+)\. (.*?)</h3>(.*?)(?=<h3|\Z)', body, re.S):
    secs[int(m.group(1))] = (m.group(2), m.group(3))
assert len(secs) == 54, len(secs)

def sub(n, old, new):
    t, h = secs[n]; assert h.count(old) == 1, (n, old); secs[n] = (t, h.replace(old, new))
def drop_imgs(n):
    t, h = secs[n]; secs[n] = (t, re.sub(r'<div style="display:flex.*?</div>(<div style="text-align:center;font-size:13px;color:#3d6480;[^"]*">.*?</div>)?', '', h, flags=re.S))

# この パッチに あわせて 直す
sub(44, 'ジョウトとカントーのバッジを<b>16こ全部</b>集めたあとは、', 'ジョウトとカントーのバッジを<b>16こ全部</b>集めて、<b>ジョウトで殿堂入りしたあと</b>は、')
sub(44, 'バッジがそろう前は元のゲームのままです。', 'このパッチではカントーのバッジを先に集めるので、ジョウトで殿堂入りする前（はじめてのジョウトのリーグ）は元のゲームのままです。')
secs[51] = (secs[51][0], P('タマムシデパート3F（初代シリーズのデパート）で わざマシン18をくれる店員が、わざマシン18をもらったあと・<b>ジョウトで殿堂入りしたあと</b>に話しかけると、「わざマシン01ー17」「わざマシン18ー35」「わざマシン36ー50」から選べるお店になります。') +
          P('ジムリーダーや人からもらう、1回しか手に入らないわざマシン（32こ）が買えます。元から売っているわざマシンもそのまま並びます。ほかの店で売っているもの、ゲームコーナーの景品、毎週もらえるおんがえし・やつあたりは並びません。値段は元のゲームと同じです。'))
sub(54, '元のゲームにあったバグ（29か所）を、通常版・60fps版の両方で直しています。', '元のゲームにあったバグ（29か所）を直しています。')
t46, h46 = secs[46]
h46 = re.sub(r'<div style="display:flex.*?</div>(<div style="text-align:center;font-size:13px;color:#3d6480;[^"]*">.*?</div>)?', '', h46, flags=re.S)
secs[46] = (t46, P('サファリゾーン（初代シリーズのサファリゾーン）の中では、歩いているあいだも画面の下に、残りの歩数とボールの数をいつも表示します（スタートメニューにも今までどおり出ます）。') + IMG('t65/00000_walk.png'))
KEEP = [n for n in range(1, 55) if n not in (8, 9, 18, 27, 28)]

o = ['<meta charset="utf-8" />', '<div style="font-size:16px;color:#333;max-width:760px;margin:0 auto;">']
hb = io.BytesIO(); Image.open(R + 'blog/img/header.png').convert('RGB').save(hb, 'JPEG', quality=90)
o.append(f'<div style="text-align:center;margin:0 0 16px;"><img src="data:image/jpeg;base64,{base64.b64encode(hb.getvalue()).decode()}" alt="{NAME}" style="width:100%;max-width:760px;height:auto;border-radius:8px;" /></div>')
o.append(P(f'『ポケットモンスター クリスタル』を、<b>サトシ</b>になって マサラタウンから旅立つ物語に作りかえたパッチです。'
           'カントーでは初代ポケモンシリーズ（赤・緑・青・ピカチュウ）のストーリーをたどり、<b>カントーで151匹すべて</b>ゲットできるようにしました。'
           'カントーで殿堂入りしたあとは、船でワカバタウンへ渡って、ジョウトでクリスタルの物語が始まります。ジョウトでは<b>第二世代のポケモンをすべて</b>ゲットできるようにしました。'))
o.append(P('さらに「クリスタル 追加機能パッチ」の機能（Bボタンダッシュ・連れ歩き・<b>60fps</b> など）と、元のゲームのバグ修正も入っています。'))
o.append(BOX('<b>ゲームボーイカラー専用です</b><br />パッチを当てたファイルは、拡張子を <b>.gbc</b> にして、<b>ゲームボーイカラーのコア（モード）</b>で起動してください。<br />'
             'パッチを当てると ROM は <b>4MB</b>（4,194,304 バイト・<b>MBC30</b>）になります。<b>4MB の MBC30 に対応したエミュレーター</b>で遊んでください。<br />'
             '<b>動くもの</b>：SameBoy（動作を確かめています）・mGBA・BGB・VBA-M（2.1.5 以降）・Pizza Boy GBC Pro（5.4.5 以降）・RetroArch の SameBoy コア／mGBA コア など<br />'
             '<b>動かないもの</b>：gambatte（RetroArch の gambatte コアや、gambatte を使う中華エミュレーター機をふくむ）・ゲームボーイカラー本体＋エバードライブなどのフラッシュカート（MBC30 の 4MB に対応したカートリッジでないと動きません）<br />'
             '対応していないものでは、著作権の画面のあと オープニングに進まずに止まります。'))

orig_list = ['サトシになって マサラタウンから旅立つ（オープニング・タイトルも初代シリーズ）', 'カントーは初代ポケモンシリーズのストーリー（マップ・トレーナー・ジムリーダー・四天王）',
             'ムサシとコジロウ（カントーとジョウト）', 'カントーで151匹すべてゲットできる', 'フシギダネ・ヒトカゲ・ゼニガメがもらえる', 'タマムシのゲームコーナーの景品',
             '殿堂入りしたら船でジョウトへ', 'ジョウトでは第二世代のポケモンをすべてゲットできる', 'ジョウトの御三家は3匹ともらえる', '通信交換で進化するポケモンはレベル37で進化',
             'セレビィ（レベル70）', 'ジョウトは3年後の物語', 'リニアが走る（ヤマブキシティに駅）', 'カントーのジムリーダーと再戦', 'シロガネやまのヒビキ', 'サファリゾーン（初代シリーズ）']
o.append(BOX('<b>ここが変わります（まとめ）</b><ul style="margin:4px 0 0;padding-left:1.4em;">' + ''.join(f'<li>{x}</li>' for x in orig_list) +
             ''.join(f'<li>{secs[n][0]}</li>' for n in KEEP) + '</ul>'))

# バグ報告（手本と同じ。値だけ この パッチ）
i = REF.index('バグ報告をする前に確認してください'); i = REF.rindex('<div', 0, REF.rindex('<div', 0, i))
j = REF.index('ギガファイル便にアップロードしたリンク）</div></div>', i) + len('ギガファイル便にアップロードしたリンク）</div></div>')
bug = REF[i:j]
bug = re.sub(r'（通常版 34EC54B1、60fps版 D0C9E654、251匹そろう版 F9A8D4E3、251匹そろう版 60fps 66FE4E2C。', f'（{CRC}。', bug)
bug = bug.replace('（例：ポケットモンスター クリスタル 追加機能.ips と、そのフォルダ名「通常版」）', f'（例：{NAME}.ips）').replace('（例：34EC54B1）', f'（例：{CRC}）')
assert CRC in bug and '34EC54B1' not in bug and '通常版' not in bug, bug[:3000]
o.append(bug)

# あらすじ
o.append(H2('あらすじ'))
o.append(P('マサラタウンに住む少年<b>サトシ</b>は、オーキドはかせからはじめてのポケモンをもらい、ライバルの<b>シゲル</b>と競いながらカントー地方の旅に出ます。'))
o.append(P('トキワのもり・おつきみやま・ハナダ・クチバ……と町をめぐってジムリーダーに勝ち、バッジを集めていきます。行く先々では、ロケット団の<b>ムサシとコジロウ</b>が待ちかまえています。'
           'タマムシのゲームコーナーの地下にあるロケット団のアジト、ポケモンタワーのゆうれい、ヤマブキのシルフカンパニーと、ロケット団のたくらみをくじきながら、8つのバッジをそろえて セキエイこうげんのポケモンリーグへ。'
           '四天王とチャンピオンになったシゲルに勝てば、殿堂入りです。'))
o.append(P('殿堂入りのあと、オーキドはかせから<b>船のチケット</b>をもらったサトシは、クチバから船に乗って ジョウト地方のワカバタウンへ。物語はカントーのチャンピオンになってから<b>3年後</b>です。'
           'ウツギはかせのもとで ジョウトのポケモンと出会い、新しいライバルや よみがえったロケット団、伝説のポケモンをめぐる ジョウトの冒険が始まります。'))
o.append(P('ジョウトでも殿堂入りすると、リニアが走りはじめ、3年ぶりのカントーのジムリーダーとの再戦、ウバメのもりのセレビィ、そしてシロガネやまで待つ<b>ヒビキ</b>との戦いが待っています。'))

# このパッチのオリジナル
o.append(H2('このパッチのオリジナル'))
k = 0
def OS(title, html):
    global k; k += 1; o.append(H3('%d. %s' % (k, title))); o.append(html)
OS('サトシになって マサラタウンから旅立つ',
   P('オープニングとタイトル画面は初代ポケモンシリーズ（ゲンガーとニドリーノ・ヒトカゲ）です。主人公の名前は自由に決められて、「サトシ」も選べます。ライバルはシゲルで、名前も自分で決められます。')
   + IMG('blog/ng/00040_t.png', 'blog/maps2/PalletTown.png'))
OS('カントーは初代ポケモンシリーズのストーリー',
   UL(['町・道路・ダンジョンは初代シリーズのマップです（トキワのもり・おつきみやま・サントアンヌ号・ロケット団のアジト・ポケモンタワー・シルフカンパニー・ふたごじま・ポケモンやしき・ハナダのどうくつ など）。',
       'ジムリーダー・トレーナー・四天王・チャンピオンも、初代シリーズと同じ手持ちとセリフです。',
       'ポケモンタワーでは、シルフスコープがないと「ゆうれい」が出てきます。',
       'シゲルが出てくるときは、赤と同じシゲルの曲（ライバルあらわる）が流れます。',
       'カントーの町や道路も、クリスタルと同じく朝・昼・夜で色が変わります。',
       'カントーで殿堂入りすると、初代シリーズの殿堂入りとスタッフロールが流れます。'])
   + IMG('blog/maps2/PewterCity.png', 'blog/maps2/CeruleanCity.png') + IMG('blog/maps2/CeladonCity.png', 'blog/maps2/LavenderTown.png'))
OS('ムサシとコジロウ',
   P('ロケット団の<b>ムサシとコジロウ</b>が、『ピカチュウ』のようにカントーの行く先々で勝負をしかけてきます。マップの上の絵とバトルの絵は「ポケットモンスターピカチュウフルカラー」と同じです。'
     'バトルの絵は2人を塗り分けていて、<b>コジロウは青紫の髪、ムサシは赤紫の髪</b>、2人とも肌色と白い服です（戦闘が始まるときと、勝ったあとに2人が出てくるとき）。')
   + P('ジョウトでも、ヤドンのいど・いかりのみずうみのアジト・ラジオとうのロケット団の場面に登場します（ラジオとうではソーナンスも）。')
   + IMG('blog/orig2/jj19.png'))
OS('カントーで151匹すべてゲットできる',
   P('カントーの野生・つり・もらうポケモンなどを見直して、<b>カントーだけで151匹すべて</b>ゲットできるようにしました。第二世代のポケモンはカントーには出ません。'
     'ピカチュウは赤・緑・青と同じ場所に出ます。'))
OS('フシギダネ・ヒトカゲ・ゼニガメがもらえる',
   P('『ピカチュウ』と同じ人・同じ話で、フシギダネ（ハナダシティの家の女の人）・ヒトカゲ（24ばんどうろ）・ゼニガメ（クチバシティのジュンサー）がもらえます。'))
OS('タマムシのゲームコーナーの景品',
   P('ポケモンの景品は『ピカチュウ』と同じです（ケーシィ・ロコン・プクリン、「つぎへ」でストライク・カイロス・ポリゴン）。') + IMG('t64/prize/00009_p4.png'))
OS('殿堂入りしたら船でジョウトへ',
   P('カントーで殿堂入りすると、オーキドはかせから船のチケットがもらえます。はじめての船はクチバからワカバタウンへ向かい、ジョウトの物語が始まります（2回目からはアサギシティ行きです）。'
     'ワカバタウンの家はクリスタルの主人公「ヒビキ」の家です。手持ちのポケモンは、カントーからそのまま連れて行けます。')
   + IMG('blog/maps2/NewBarkTown.png', 'blog/maps2/GoldenrodCity.png'))
OS('ジョウトでは第二世代のポケモンをすべてゲットできる',
   P('ジョウトの野生・つり・ずつき・いわくだき・むしとり大会・もらうポケモン・景品・交換は第二世代のポケモンだけにして、<b>ジョウトで第二世代のポケモンをすべて</b>ゲットできるようにしました。'
     '第一世代から進化するポケモン（クロバット・ハガネールなど）は、カントーから連れてきて進化させます。いかりのみずうみの赤いギャラドスはそのままです。')
   + IMG('blog/maps2/EcruteakCity.png'))
OS('ジョウトの御三家は3匹ともらえる', P('ウツギはかせのところで1匹えらぶと、のこりの2匹ももらえます。'))
OS('通信交換で進化するポケモンはレベル37で進化',
   P('ユンゲラー・ゴーリキー・ゴローン・ゴースト・ニョロゾ（ニョロトノ）・シードラ・イワーク・ストライク・ポリゴンは、レベル37になると進化します。ヤドンは おうじゃのしるし を持たせてレベル37以上でレベルが上がるとヤドキングに進化します。'))
OS('セレビィ', P('ジョウトで殿堂入りしたあと、ウバメのもりのほこらで<b>レベル70</b>のセレビィに会えます。つかまえなかったとき（負けた・たおした・にげた）は、つぎの殿堂入りのあとにまた会えます。'))
OS('ジョウトは3年後の物語',
   P('ジョウトの物語は、サトシがカントーのチャンピオンになってから3年後です。ワタル・四天王・シルバー・オーキドはかせなどのセリフを、「カントーのチャンピオンのサトシ」に合わせて作りなおしています。'))
OS('リニアが走る（ヤマブキシティに駅）',
   P('ジョウトで殿堂入りしたあと、コガネシティとヤマブキシティをむすぶリニアが走りはじめます。ヤマブキシティに駅の入口を作りました。'
     'リニアのていきけんは、クリスタルと同じく ヤマブキのモノマネむすめに「なくしたピッピにんぎょう」を届けるともらえます。'))
OS('カントーのジムリーダーと再戦',
   P('ジョウトで殿堂入りしたあと、カントーのジムリーダーに話しかけると再戦できます。クリスタルと同じく、セキチクジムはアンズ、トキワジムはシゲル、カツラはふたごじまにいます（クリスタルの再戦の手持ち）。'
     'ジムリーダーは3年ぶりに会うサトシに話しかけてきます。2回目からは「また しょうぶ しよう」という短いセリフになります。'))
OS('シロガネやまのヒビキ', P('ジョウトで殿堂入りしたあと、シロガネやまの奥では クリスタルの主人公「ヒビキ」が待っています。'))
OS('サファリゾーン（初代シリーズ）',
   P('セキチクシティの北のサファリゾーンは初代シリーズと同じです（500円でサファリボール30こ・500歩、ボール・エサ・いし・にげる）。ひみつの家でなみのりのひでんマシン、きんのいればで かいりきのひでんマシンがもらえます。'
     '中を歩いているあいだは、画面の下に残りの歩数とボールの数をいつも表示します。'))

# 追加した機能（手本から）
o.append(H2('追加した機能（「クリスタル 追加機能パッチ」から）'))
o.append(P('「クリスタル 追加機能パッチ」の機能（251匹そろう版をのぞく）が入っています。'))
for k2, n in enumerate(KEEP, 1):
    t, h = secs[n]
    o.append(H3('%d. %s' % (k2, t))); o.append(h)
o.append(BOX('<b>60fpsについて</b><br />このパッチは、フィールドを歩くときの動きを1ドットずつ（60fps）にしています。歩く・走る（Bダッシュ）・自転車・なみのり、外・建物の中のどれでもなめらかに動きます。ゲームの速さ・タイミングは元のままです。'))

# 遊び方（手本から、値と名前を この パッチに）
i = REF.index('>遊び方（パッチの当て方）</h2>'); i = REF.rindex('<h2', 0, i)
j = REF.index('>確認用の値（パッチを当てたあとのROM）</h2>'); j = REF.rindex('<h2', 0, j)
howto = REF[i:j]
howto = howto.replace('「ポケットモンスター クリスタル 追加機能パッチ.zip」', f'「{NAME}_リリース.zip」')
howto = re.sub(r'<pre style="([^"]*)">.*?</pre>', lambda m: f'<pre style="{m.group(1)}">{NAME}/\n└ {NAME}.ips</pre>', howto, flags=re.S)
m4 = re.search(r'<h3[^>]*>手順4　遊びたいパッチを選ぶ</h3>\s*<p[^>]*>.*?</p>\s*', howto, re.S); howto = howto[:m4.start()] + howto[m4.end():]
howto = howto.replace('手順5　', '手順4　').replace('手順6　', '手順5　').replace('手順7　', '手順6　')
howto = howto.replace('手順4で選んだ IPS ファイル', 'zip の中の IPS ファイル')
howto = howto.replace('パッチを当てたあとのROMの大きさは、元と同じ <b>2,097,152 バイト（2MB）</b>です。', 'パッチを当てたあとのROMの大きさは <b>4,194,304 バイト（4MB）</b>になります。')
howto = re.sub(r'ゲームボーイカラーに対応したエミュレーター（SameBoy、mGBA など）で遊べます。.*?</p>',
               'ゲームボーイカラーと 4MB の ROM（MBC30）に対応したエミュレーター（SameBoy・mGBA・BGB など。gambatte では動きません）で遊べます。物語が元の『クリスタル』とちがうので、元の『クリスタル』のセーブデータでは遊べません。「さいしょから はじめる」で始めてください。</p>', howto, flags=re.S)
howto = howto.replace('<div style="overflow-x:auto;"><tr>', '<div style="overflow-x:auto;"><table style="border-collapse:collapse;margin:8px 0 12px;font-size:15px;"><tr>')
for bad in ('通常版', '60fps版', '251匹', '2,097,152 バイト（2MB）</b>です'): assert bad not in howto, bad
o.append(howto)

o.append(H2('確認用の値（パッチを当てたあとのROM）'))
o.append(f'<div style="font-family:monospace;font-size:14px;word-break:break-all;overflow-wrap:anywhere;background:#f3fbfe;border:1px solid #8cc8e6;border-radius:4px;padding:6px 8px;margin:4px 0 10px;">CRC32：{CRC}<br />SHA-1：{SHA}<br />サイズ：4,194,304 バイト</div>')
o.append(H2('注意事項'))
o.append(UL(['バトルの計算のバグを直しているので、パッチを当てていないカートリッジ・ROMとの通信対戦では、結果がずれることがあります。',
             'エミュレーターの「ステートセーブ」は、パッチの版をまたいで使わないでください（画面がくずれたり止まったりすることがあります）。ゲームの中の「レポート」でのセーブは、そのまま使えます。',
             'パッチは自己責任で使ってください。元のROMは、必ずコピーを残しておいてください。']))
o.append('<div style="border:2px solid #c0392b;background:#fff3f0;border-radius:8px;padding:10px 14px;margin:12px 0;line-height:1.85;"><b>不具合を見つけたら</b><br />'
         'どの端末（パソコン・Android・iPhone・中華エミュレーター機など）とエミュレーターを使って、どの場所で、何をしたときに起きたかを、コメントで教えてください。できれば画面の写真や動画もあると助かります。</div>')
o.append(H2('更新履歴'))
TD = 'padding:6px 8px;border:1px solid #8cc8e6;'
o.append(f'<div style="overflow-x:auto;"><table style="border-collapse:collapse;margin:8px 0 12px;font-size:15px;"><tr><th style="{TD}background:#2b7bb9;color:#fff;">日付</th><th style="{TD}background:#2b7bb9;color:#fff;">内容</th></tr>'
         + ''.join(f'<tr><td style="{TD}white-space:nowrap;vertical-align:top;">{d}</td><td style="{TD}">Ver.{v}'
                   + ('　' + items[0] if len(items) == 1 else '<ul style="margin:4px 0 0;padding-left:1.4em;">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>')
                   + '</td></tr>' for d, v, items in HISTORY)
         + '</table></div>')
i = REF.index('>クレジット</h2>'); i = REF.rindex('<h2', 0, i)
cred = REF[i:REF.rindex('</div>')]
extra = ('<li>カントーのマップ・絵・セリフ・ムサシとコジロウ・151匹そろう版：ポケットモンスターピカチュウフルカラー</li>'
         '<li>オープニング・タイトル・殿堂入り：ポケットモンスター赤フルカラー</li>'
         '<li>シナリオの参考：Pokémon Ash Gray・Ash\'s Quest</li>'
         '<li>サファリゾーンのバトル：サファリゾーン入りのクリスタル改造ROM</li>'
         '<li>ゲームの作りの調査：pret/pokered・pret/pokeyellow</li>')
cred = cred.replace('</ul>', extra + '</ul>', 1)
o.append(cred)
o.append('</div>')
html = '\n'.join(o) + '\n'
for bad in ('日本語', '日本版', '海外版', '欧州版', '移植', '『赤』どおり'):
    assert bad not in html, bad
open(sys.argv[2], 'w', encoding='utf-8').write(html)
print(sys.argv[2], len(html), CRC)

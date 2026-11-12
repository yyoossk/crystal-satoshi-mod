; 1回しか もらえない わざマシンを タマムシデパート 3F で 買える … クリスタル（日本版）用の 値（本体は src/tmshop.asm）
; クリスタルも 売り場・景品・毎週の わざマシンは 金と 同じ（売る：02・08・10・11・17・18・33・37・41・48、
; 景品：14・15・25・29・32・38、毎週：21・27）なので 表も 金と 同じ。
INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（スクリプトの 命令の 番号は 英語版 金銀）
INCLUDE "src/charmap_jp.inc"
DEF TS_NO_INCLUDES EQU 1

DEF TS_CLERK        EQU $61b6      ; バンク$1a CeladonDeptStore3FClerkScript（6a 47 93 00 19 00 49 90）
DEF TS_CLERK_BANK   EQU $1a
DEF TS_MART_ID      EQU $19        ; MART_CELADON_3F
DEF TS_wScriptVar   EQU $c2dd
DEF TS_BANK         EQU $8f        ; 空いて いる バンク（通常版・60fps版・251版 とも）
DEF TS_ADDR         EQU $4000
; この MOD：タマムシデパートは 赤の マップ（phase41）で、クリスタルの 3F には 行けない。
; 赤の 3F の 店員（わざマシン18 を くれる 人）が、わざマシン18 を わたした あと・ジョウトの 殿堂入りの あとに この 店に なる
; （その つなぎは tools/build_phase64.py が 書く）。クリスタルの 3F の 店員は かえない。
DEF TS_NO_CLERK_PATCH EQU 1

INCLUDE "src/tmshop.asm"

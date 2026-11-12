; フィールドのボール・回復の機械・肌の色（src/fieldcolors.asm）の クリスタル日本版の値
; tools/fieldcolors_find.py（パッチを入れる前の ROM）で出した値 ＋ 空きの場所
DEF FC_OBJ_BANK            EQU $01
DEF FC_INIT_HOOK           EQU $5a38
DEF FC_ATTR_HOOK           EQU $5aaf    ; （FC_END_HOOK が ある ときは 使わない）
DEF FC_END_HOOK            EQU $5abb    ; InitSprite の さいごの ld a, c / ldh [hUsedSpriteIndex], a（79 e0 bd）
DEF FC_hUsedSpriteIndex    EQU $ffbd
DEF FC_wShadowOAM          EQU $c400
DEF FC_hCurSpriteOAMFlags  EQU $ffc2
DEF FC_FREE                EQU $7f00    ; バンク$01 の空き 50バイト（$7ea0〜$7eb2 は わざの上書き防止）
DEF FC_BALLGFX_BANK        EQU $31
DEF FC_BALLGFX             EQU $7380
DEF FC_SPRITES_BANK        EQU $05
DEF FC_SPRITES             EQU $4727
DEF FC_LABOBJ_BANK         EQU $1b
DEF FC_LABOBJ              EQU $7313
; この MOD：$3f（SPRITE_UNUSED_GUY）は MOD の サカキ（phase13）。MOD の 2つめの 人の 絵の 表（$67〜、バンク$05 の $7f34〜）の
; つぎの 番号 $79 を 研究所の ボールに する（表の さいごの $7fa0 に 1つ 足す。phase64 が たしかめる）
DEF FC_SPRITE_LAB_BALL      EQU $79
DEF FC_LABSPRITE_ENTRY      EQU $7fa0
DEF FC_LABGFX_BANK         EQU $90      ; 研究所のボールの絵 64バイト（新しいバンクの空き）
DEF FC_LABGFX              EQU $6000
DEF FC_NPCPALS_BANK        EQU $02
DEF FC_NPCPALS             EQU $7426
DEF FC_HEALPAL_BANK        EQU $04
DEF FC_HEALPAL             EQU $62db

; この MOD（phase69）：カントー（赤の マップ。タイルセット 40）の 段差を 赤と 同じに
;   赤の 段差は、段差の タイルの 1つ 手前から その 向きに 歩くと 段差を とびこえる（2マス）。
;   それ以外の 向きからは かべ。（第30弾は 段差の タイルに クリスタルの「とびおりる」の 当たりを つけただけで、
;   クリスタルの しくみでは その タイルに のって しまい、とびこえも しなかった）
;   クリスタルの TryStep（$20:$416B）の CheckLandPerms（$20:$439E）の あとで しらべる。ジョウトは そのまま。
DEF CheckLandPerms        EQU $439E
DEF DoStep                EQU $425F
DEF LedgeTable            EQU $421E     ; クリスタルの .ledge_table（とびおりる 向き → FACE_*）
DEF PlaySFX               EQU $3BB0
DEF wMapTileset           EQU $D1CA
DEF wWalkingTileCollision EQU $D03D
DEF wFacingDirection      EQU $D03A
DEF RED_OVERWORLD_TS      EQU 40
DEF SFX_JUMP_OVER_LEDGE   EQU $16
DEF STEP_LEDGE            EQU 3
DEF PLAYERMOVEMENT_JUMP   EQU 7

SECTION "p69 hook", ROMX[$4176], BANK[$20]
	call RedLedge

SECTION "p69 body", ROMX[P69_ADDR], BANK[$20]
RedLedge:
	call CheckLandPerms
	ret c
	ld a, [wMapTileset]
	cp RED_OVERWORLD_TS
	jr nz, .walk
	ld a, [wWalkingTileCollision]
	ld e, a
	and $F0
	cp $A0                      ; 段差
	jr nz, .walk
	ld a, e
	and 7
	ld e, a
	ld d, 0
	ld hl, LedgeTable
	add hl, de
	ld a, [wFacingDirection]
	and [hl]
	jr z, .wall
; 段差を とびこえる（クリスタルの .TryJump と 同じ）。TryStep には もどらない
	pop hl
	ld de, SFX_JUMP_OVER_LEDGE
	call PlaySFX
	ld a, STEP_LEDGE
	call DoStep
	ld a, PLAYERMOVEMENT_JUMP
	scf
	ret
.wall
	scf
	ret
.walk
	and a
	ret

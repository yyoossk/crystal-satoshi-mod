; この MOD（phase66）：ムサシとコジロウの 戦闘の 絵を ピカチュウ・フルカラーと 同じ 色に（2人を 別の パレットで）
;   ピカチュウ・フルカラーの $3a:$6b72 と 同じ：絵の 左3列（コジロウ）= 青紫の 髪、右4列（ムサシ）= 赤紫の 髪。
;   色も ピカチュウ・フルカラーの $3a:$6c8c・$6c94（白・肌色・髪・黒）。
;   _CGB_FinishBattleScreenLayout の おわり（$02:$4e73。もとは $90:$5e00 への farcall）を ここに。
;   トレーナー戦で、絵が トレーナー（wTempEnemyMonSpecies = 0）で、クラスが ロケットだん（ムサシとコジロウ、72）の とき だけ。
;   コジロウは BG パレット 5（あいての 状態の 色。あいての HUD が ない あいだ だけ なので 重ならない）、
;   ムサシは BG パレット 1（あいての 絵の 色）。パレット 6（こちらの 状態の 色）は 勝った あとも 出て いるので 使わない。
DEF wBattleMode          EQU $d25e
DEF wTempEnemyMonSpecies EQU $d235
DEF wOtherTrainerClass   EQU $d260
DEF TRAINER_JJ           EQU 72
DEF wTilemap             EQU $c4a0
DEF wAttrmap             EQU $cdcd
DEF wBGPals1             EQU $d000     ; WRAM バンク5
DEF CHAIN_BANK           EQU $90
DEF CHAIN_ADDR           EQU $5e00
DEF JJ_BANK              EQU $9c

SECTION "jj colors hook", ROMX[$4e73], BANK[$02]
	ld a, BANK(JJColors)
	ld hl, JJColors
	rst $08

SECTION "jj colors", ROMX[$4400], BANK[JJ_BANK]
JJColors:
	ld a, CHAIN_BANK
	ld hl, CHAIN_ADDR
	rst $08
	ld a, [wBattleMode]
	cp 2
	ret nz
	ld a, [wTempEnemyMonSpecies]
	and a
	ret nz
	ld a, [wOtherTrainerClass]
	cp TRAINER_JJ
	ret nz
; 戦闘の はじめ（絵が 12〜18列に 置いて ある）か、勝った あと（絵の 左6列が 14〜19列に すべりこむ）か
	ld hl, wAttrmap + 12
	ld b, 4                    ; ムサシの 列の 数
	ld a, [wTilemap + 13]
	cp 7
	jr z, .fill
	ld hl, wAttrmap + 14
	dec b
.fill
	ld c, 7
.row
	push hl
	push bc
	ld a, 5
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld a, 1
.musashi
	ld [hli], a
	dec b
	jr nz, .musashi
	pop bc
	pop hl
	ld de, 20
	add hl, de
	dec c
	jr nz, .row
.pals
	ldh a, [$ff70]
	push af
	ld a, 5
	ldh [$ff70], a
	ld hl, JJPals
	ld de, wBGPals1 + 5 * 8
	call .copy8
	ld de, wBGPals1 + 1 * 8
	call .copy8
	pop af
	ldh [$ff70], a
	ret

.copy8
	ld c, 8
.copy
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .copy
	ret

JJPals:   ; ピカチュウ・フルカラーの $3a:$6c8c（コジロウ）・$6c94（ムサシ）
	dw $7fff, $46ff, $6d8d, $0c63
	dw $7fff, $46ff, $3cdb, $0c63

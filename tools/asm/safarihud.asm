; この MOD（phase65）：サファリゾーンで 歩いて いる あいだも 画面の いちばん 下に のこりの 歩数と ボールを 出す
; 「クリスタル追加機能キット」の src/safari/safari.asm の SafariHUD を、MOD の サファリゾーン（phase28。赤の サファリ）に あわせた もの。
;   ・サファリゲーム中：wStatusFlags2（$d840）の ビット1、のこりの 歩数 $dc40（2バイト。上・下）、ボール $dc3f。
;   ・サファリの 中か：MOD の $6e:$7140（キャリー）。
;   ・PlaceMapNameSign（$2e:$4098。フィールドで 毎フレーム）の .disappear（$2e:$40bc）を この 処理への farcall に。
DEF wStatusFlags2         EQU $d840
DEF wSafariBallsRemaining EQU $dc3f
DEF wSafariTimeRemaining  EQU $dc40
DEF MOD_SAF_BANK          EQU $6e
DEF MOD_IN_SAFARI         EQU $7140
DEF SH_PlaceMapNameSign_Disappear EQU $40bc
DEF SH_hWY          EQU $ffd2
DEF SH_hLCDCPointer EQU $ffc6
DEF SH_hCGBPalUpdate EQU $ffe5
DEF SH_wBGPals1_7   EQU $d038     ; WRAM バンク5
DEF SH_wBGPals2_7   EQU $d0b8
DEF SH_WY           EQU $80
DEF SH_ROW0         EQU $9c00
DEF SH_ROW1         EQU $9c20
DEF SH_ATTR         EQU $87
DEF HUD_BANK        EQU $9c

SECTION "safari hud hook", ROMX[SH_PlaceMapNameSign_Disappear], BANK[$2e]
	ld a, BANK(SafariHUD)
	ld hl, SafariHUD
	rst $08
	ret

SECTION "safari hud", ROMX[$4000], BANK[HUD_BANK]
SafariHUD:
	xor a
	ldh [SH_hLCDCPointer], a
	ld a, [wStatusFlags2]
	bit 1, a                         ; サファリゲーム中（MOD phase28）
	jr z, .off
	ld a, MOD_SAF_BANK
	ld hl, MOD_IN_SAFARI
	rst $08                          ; キャリー ＝ サファリの 中（入口は ちがう）
	jr nc, .off
	call .Pal
	ldh a, [$ff4f]                   ; rVBK
	push af
	ldh a, [SH_hWY]
	cp SH_WY
	call nz, .Full
	call .Digits
	pop af
	ldh [$ff4f], a
	ld a, SH_WY
	jr .set
.off
	ld a, $90
.set
	ldh [$ff4a], a                   ; rWY
	ldh [SH_hWY], a
	ret

.Pal
	ldh a, [$ff70]                   ; rSVBK
	push af
	ld a, 5
	ldh [$ff70], a
	ld hl, SH_wBGPals2_7
	ld de, .Colors
	ld b, 8
.cmp
	ld a, [de]
	cp [hl]
	jr nz, .write
	inc de
	inc hl
	dec b
	jr nz, .cmp
	jr .pal_done
.write
	ld hl, SH_wBGPals1_7
	call .CopyPal
	ld hl, SH_wBGPals2_7
	call .CopyPal
	ld a, 1
	ldh [SH_hCGBPalUpdate], a
.pal_done
	pop af
	ldh [$ff70], a
	ret
.CopyPal
	ld de, .Colors
	ld b, 8
.copy
	ld a, [de]
	inc de
	ld [hli], a
	dec b
	jr nz, .copy
	ret
.Colors
	dw $7fff, $7fff, $35ad, $0000     ; 白・白・はい色・黒

.Full
	xor a
	ldh [$ff4f], a
	ld hl, SH_ROW0
	ld de, .Row0
	call .Put20
	ld hl, SH_ROW1
	ld de, .Row1
	call .Put20
	ld a, 1
	ldh [$ff4f], a
	ld hl, SH_ROW0
	call .Attr20
	ld hl, SH_ROW1
.Attr20
	ld b, 20
.attr_loop
	ld a, SH_ATTR
	call .Put
	dec b
	jr nz, .attr_loop
	ret
.Put20
	ld b, 20
.put_loop
	ld a, [de]
	inc de
	call .Put
	dec b
	jr nz, .put_loop
	ret

.Digits
	xor a
	ldh [$ff4f], a
	ld a, [wSafariTimeRemaining]
	ld h, a
	ld a, [wSafariTimeRemaining + 1]
	ld l, a
	ld c, 0
.hundreds
	ld a, l
	sub 100
	ld e, a
	ld a, h
	sbc 0
	jr c, .hundreds_done
	ld h, a
	ld l, e
	inc c
	jr .hundreds
.hundreds_done
	ld a, l
	call .Split                      ; d ＝ 10の くらい、e ＝ 1の くらい
	ld hl, SH_ROW1 + 4
	ld a, c
	and a
	ld a, $7f
	jr z, .h_blank
	ld a, c
	add $f6
.h_blank
	call .Put
	ld a, c
	or d
	ld a, $7f
	jr z, .t_blank
	ld a, d
	add $f6
.t_blank
	call .Put
	ld a, e
	add $f6
	call .Put
	ld a, [wSafariBallsRemaining]
	call .Split
	ld hl, SH_ROW1 + 14
	ld a, d
	and a
	ld a, $7f
	jr z, .b_blank
	ld a, d
	add $f6
.b_blank
	call .Put
	ld a, e
	add $f6
	; fallthrough

.Put                                 ; [hl+] ＝ a（Hブランク・Vブランク の ときに かく）
	push bc
	ld c, a
	di
.wait
	ldh a, [$ff41]                   ; rSTAT
	and %10                          ; モード 0（Hブランク）か 1（Vブランク）まで まつ
	jr nz, .wait
	ld [hl], c
	ei
	inc hl
	pop bc
	ret

.Split                               ; a（0〜99）→ d ＝ 10の くらい、e ＝ 1の くらい
	ld d, 0
.split_loop
	sub 10
	jr c, .split_done
	inc d
	jr .split_loop
.split_done
	add 10
	ld e, a
	ret

.Row0 ; ボ の ゛
	db $7f, $7f, $7f, $7f, $7f, $7f, $7f, $7f, $7f, $7f, $e5, $7f, $7f, $7f, $7f, $7f, $7f, $7f, $7f, $7f
.Row1 ; 「 あと nnnほ  ボール nnこ   」
	db $7f, $b1, $c4, $7f, $7f, $7f, $7f, $ce, $7f, $7f, $9c, $e3, $a6, $7f, $7f, $7f, $ba, $7f, $7f, $7f

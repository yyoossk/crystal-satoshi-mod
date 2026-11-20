; Phase 126: the lines that a "tackle" type battle effect (BattleBGEffect_SetLCDStatCustoms1 / 2, 32:4E6D / 32:4E83)
; shifts.  Crystal: the enemy's turn = lines $00-$35, the player's turn = lines $2F (or $2D)-$5D; the pictures overlap in
; tile row 6 (lines $30-$37: the enemy's feet, the top of a tall back picture), so a tall Pokémon (Nidoran♂, Mankey ...)
; moved the other side too.  Now the overlapping lines of the other side's picture are left out:
;   enemy's turn : the range ends above the first line of row 6 where the player's picture (columns 1-8) has a dot;
;   player's turn: the range starts below the last line of row 6 where the enemy's picture (columns 11-19) has a dot.
; (VRAM read in mode 0-2 only; VRAM bank from the attribute map.)

DEF wTilemap      EQU $C4A0
DEF wAttrmap      EQU $CDCD
DEF hLCDCPointer  EQU $FFC6
DEF hLYOverStart  EQU $FFC7
DEF hLYOverEnd    EQU $FFC8
DEF CheckTurn     EQU $4FC8          ; BGEffect_CheckBattleTurn (nz: the player's side)

SECTION "tackle split", ROMX[CODE_ADDR], BANK[$32]

TS_Customs1::
	ldh [hLCDCPointer], a
	ld e, $2f
	jr TS_Common
TS_Customs2::
	ldh [hLCDCPointer], a
	ld e, $2d
TS_Common:
	push de
	call CheckTurn
	pop de
	jr nz, .player
	; the enemy's turn: lines 0 .. min($36, first dot line of the player's row 6)
	ld hl, wTilemap + 6 * 20 + 1
	ld c, 8
	call TS_RowMask                   ; d = bit 7: line $30 ... bit 0: line $37
	ld e, $30
.first
	sla d
	jr c, .gotfirst
	inc e
	ld a, e
	cp $38
	jr c, .first
.gotfirst
	ld a, e
	cp $36
	jr c, .endok
	ld a, $36
.endok
	ld e, a
	ld d, 0
	jr .store
.player
	; the player's turn: lines max(default, last dot line of the enemy's row 6 + 1) .. $5E
	push de
	ld hl, wTilemap + 6 * 20 + 11
	ld c, 9
	call TS_RowMask
	pop bc                            ; c = the default start
	ld b, $38
.last
	ld a, d
	and a
	jr z, .none
	srl d
	jr c, .gotlast
	dec b
	jr .last
.none
	ld b, 0
.gotlast
	ld a, b
	cp c
	jr nc, .startok
	ld a, c
.startok
	ld d, a
	ld e, $5e
.store
	ld a, d
	ldh [hLYOverStart], a
	ld a, e
	ldh [hLYOverEnd], a
	ret

; hl = wTilemap address of the first tile, c = tiles -> d = the lines with a dot (bit 7 = the tiles' line 0)
TS_RowMask:
	ldh a, [$ff4f]
	push af
	ld d, 0
.tile
	push bc
	push hl
	ld e, [hl]                        ; tile number
	ld bc, wAttrmap - wTilemap
	add hl, bc
	ld a, [hl]
	and 8
	rrca
	rrca
	rrca
	ldh [$ff4f], a                    ; VRAM bank of the tile
	ld l, e
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl                        ; 16 × tile
	ldh a, [$ff40]
	bit 4, a
	jr nz, .low                       ; $8000 addressing
	ld a, e
	cp $80
	jr nc, .low                       ; $80-$FF: $8800-$8FFF
	ld a, h
	add $90
	ld h, a
	jr .addr
.low
	ld a, h
	add $80
	ld h, a
.addr
	ld bc, $0880                      ; b = 8 lines, c = the line's bit
.line
.wait
	ldh a, [$ff41]
	and 2
	jr nz, .wait                      ; mode 0 / 1 (then mode 2: VRAM still free for 80 dots)
	ld a, [hli]
	or [hl]
	inc hl
	jr z, .blank
	ld a, d
	or c
	ld d, a
.blank
	srl c
	dec b
	jr nz, .line
	pop hl
	inc hl
	pop bc
	dec c
	jr nz, .tile
	pop af
	ldh [$ff4f], a
	ret

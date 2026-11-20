; MBC5 version: no real-time clock.  The clock is the game time (wGameTime, counted while playing) minus a base
; kept in SRAM bank 0 ($AC81-$AC85, unused bytes after sRTCStatusFlags).  GetClock / SetClock (home) farcall these.
DEF rWBK EQU $FF70
DEF hRTCDayHi EQU $FF8D
DEF hRTCDayLo EQU $FF8E
DEF hRTCHours EQU $FF8F
DEF hRTCMinutes EQU $FF90
DEF hRTCSeconds EQU $FF91
DEF wGameTimeHours EQU $D4B7
DEF wGameTimeMinutes EQU $D4B9
DEF wGameTimeSeconds EQU $D4BA
DEF sBaseHoursHi EQU $AC81
DEF sBaseHoursLo EQU $AC82
DEF sBaseMinutes EQU $AC83
DEF sBaseSeconds EQU $AC84
DEF sBaseMark EQU $AC85
DEF MARK EQU $A5

SECTION "mbc5clock", ROMX[CODE_ADDR], BANK[CODE_BANK]

; hl = game hours, d = minutes, e = seconds
LoadGameTime:
	ldh a, [rWBK]
	push af
	ld a, 1
	ldh [rWBK], a
	ld a, [wGameTimeHours]
	ld h, a
	ld a, [wGameTimeHours + 1]
	ld l, a
	ld a, [wGameTimeMinutes]
	ld d, a
	ld a, [wGameTimeSeconds]
	ld e, a
	pop af
	ldh [rWBK], a
	ret

OpenSRAM0:
	ld a, $0A
	ld [$0000], a
	xor a
	ld [$4000], a
	ret

CloseSRAM0:
	xor a
	ld [$0000], a
	ret

SoftGetClock::
	call LoadGameTime
	call OpenSRAM0
	ld a, [sBaseMark]
	cp MARK
	jr nz, .nobase
	ld c, 0
	ld a, [sBaseSeconds]
	ld b, a
	ld a, e
	sub b
	jr nc, .s
	add 60
	inc c
.s
	ld e, a
	ld a, [sBaseMinutes]
	add c
	ld b, a
	ld c, 0
	ld a, d
	sub b
	jr nc, .m
	add 60
	inc c
.m
	ld d, a
	ld a, [sBaseHoursLo]
	add c
	ld c, a
	ld a, [sBaseHoursHi]
	adc 0
	ld b, a
	ld a, l
	sub c
	ld l, a
	ld a, h
	sbc b
	ld h, a
	jr nc, .nobase
	ld hl, 0
	ld de, 0
.nobase
	call CloseSRAM0
	ld bc, 0
.div
	ld a, h
	and a
	jr nz, .sub
	ld a, l
	cp 24
	jr c, .done
.sub
	ld a, l
	sub 24
	ld l, a
	ld a, h
	sbc 0
	ld h, a
	inc bc
	jr .div
.done
	ld a, l
	ldh [hRTCHours], a
	ld a, d
	ldh [hRTCMinutes], a
	ld a, e
	ldh [hRTCSeconds], a
	ld a, c
	ldh [hRTCDayLo], a
	ld a, b
	cp 2
	ld a, b
	jr c, .nocarry
	and 1
	or $80
	jr .dh
.nocarry
	and 1
.dh
	ldh [hRTCDayHi], a
	ret

SoftSetClock::
	call LoadGameTime
	ld c, 0
	ldh a, [hRTCSeconds]
	ld b, a
	ld a, e
	sub b
	jr nc, .s
	add 60
	inc c
.s
	ld e, a
	ldh a, [hRTCMinutes]
	add c
	ld b, a
	ld c, 0
	ld a, d
	sub b
	jr nc, .m
	add 60
	inc c
.m
	ld d, a
	push de
	push hl
	ld a, c
	push af
; bc = days * 24 + hours + borrow
	ldh a, [hRTCDayHi]
	and 1
	ld h, a
	ldh a, [hRTCDayLo]
	ld l, a
	add hl, hl
	add hl, hl
	add hl, hl
	ld b, h
	ld c, l
	add hl, hl
	add hl, bc
	ldh a, [hRTCHours]
	ld c, a
	ld b, 0
	add hl, bc
	pop af
	ld c, a
	add hl, bc
	ld b, h
	ld c, l
	pop hl
	ld a, l
	sub c
	ld l, a
	ld a, h
	sbc b
	ld h, a
	pop de
	jr nc, .ok
	ld hl, 0
	ld de, 0
.ok
	call OpenSRAM0
	ld a, h
	ld [sBaseHoursHi], a
	ld a, l
	ld [sBaseHoursLo], a
	ld a, d
	ld [sBaseMinutes], a
	ld a, e
	ld [sBaseSeconds], a
	ld a, MARK
	ld [sBaseMark], a
	jp CloseSRAM0

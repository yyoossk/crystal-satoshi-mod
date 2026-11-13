; この MOD（phase68）：オープニングと タイトルの 曲・効果音を、赤の 音の しくみで 鳴らす
;   赤（日本版）の バンク $1F（Audio Engine 3 と その 曲・効果音）を そのまま バンク RED_AUDIO_BANK に 写す
;   （build_phase68.py。音の RAM は $C000〜 → $C101〜 に ずらす。クリスタルの 音の RAM を かりる）。
;   クリスタルの _UpdateSound（$3A:$405C）の 頭で、$C100 = $A5 の あいだは 赤の Audio3_UpdateMusic を よぶ
;   （赤の VBlank と 同じく 先に rAUDVOL = $77）。
;   第53弾の Sfx・Music（バンク $36。build_phase68.py が さがす）は 赤の PlaySound に、タイトルの おわりの 鳴き声の 前で クリスタルの 音に もどす。

DEF hROMBank      EQU $FF9D
DEF InitSound     EQU $3ADB
DEF PlayMonCry    EQU $379E
DEF RED_ON        EQU $A5
DEF wMusicPlaying EQU $C100
DEF wAudioStart   EQU $C101
DEF wAudioEnd     EQU $C2C0
DEF rAUDVOL       EQU $FF24
; 赤（日本版）の バンク $1F の 中の 住所（RAM は ずらした あと）
DEF Audio3_UpdateMusic EQU $4417
DEF Audio3_PlaySound   EQU $4B8A
DEF wChannelSoundIDs   EQU $C127
DEF CHAN5 EQU 4
DEF CHAN6 EQU 5
DEF CHAN7 EQU 6
DEF CHAN8 EQU 7
DEF SFX_STOP_ALL_MUSIC EQU $FF
DEF MUSIC_TITLE_SCREEN EQU $C3
DEF MUSIC_INTRO_BATTLE EQU $DC
DEF SFX_INTRO_LUNGE    EQU $B8
DEF SFX_INTRO_HIP      EQU $B9
DEF SFX_INTRO_HOP      EQU $BA
DEF SFX_INTRO_RAISE    EQU $BB
DEF SFX_INTRO_CRASH    EQU $BC
DEF SFX_INTRO_WHOOSH   EQU $BD
DEF SFX_SHOOTING_STAR  EQU $C2

; ---------------------------------------------------------------- _UpdateSound の 頭
SECTION "p68 UpdateSound head", ROMX[$405C], BANK[$3A]
	jp RedUpdateHook
	nop
	nop

SECTION "p68 UpdateSound hook", ROMX[$7FC8], BANK[$3A]
RedUpdateHook:
	ld a, [wMusicPlaying]
	cp RED_ON
	jr z, .red
	and a
	ret z
	jp $4061
.red
	ld a, $77
	ldh [rAUDVOL], a
	ld a, RED_AUDIO_BANK
	ld hl, Audio3_UpdateMusic
	rst $08
	ret

; ---------------------------------------------------------------- 第53弾の Sfx・Music・鳴き声
SECTION "p68 Sfx", ROMX[SFX_ADDR], BANK[$36]
Phase53Sfx:  ; a = 第53弾の 番号（クリスタルの 曲・効果音の 番号）
	push hl
	push de
	push bc
	ld e, a
	ld a, BANK(RedSound)
	ld hl, RedSound
	rst $08
	pop bc
	pop de
	pop hl
	ret

SECTION "p68 Music", ROMX[MUSIC_ADDR], BANK[$36]
	jp Phase53Sfx

SECTION "p68 cry call", ROMX[CRY_CALL], BANK[$36]
	call CryWrap

SECTION "p68 cry wrap", ROMX[CRY_WRAP_ADDR], BANK[$36]
CryWrap:
	push af
	ld a, BANK(RedAudioOff)
	ld hl, RedAudioOff
	rst $08
	pop af
	jp PlayMonCry

; ---------------------------------------------------------------- 赤の 音の しくみへの 入り口
SECTION "p68 shim", ROMX[$43DB], BANK[RED_AUDIO_BANK]   ; 赤の ずかんの 評価の 音（ここでは 使わない）の 所
RedPlayShim:  ; e = 赤の 番号
	ld a, e
	jp Audio3_PlaySound

SECTION "p68 glue", ROMX[$4000], BANK[RED_GLUE_BANK]
RedSound:  ; e = 第53弾の 番号
	ld a, [wMusicPlaying]
	cp RED_ON
	jr z, .on
	push de
	xor a
	ld [wMusicPlaying], a
	call InitSound              ; クリスタルの 音を 止めて けす
	xor a
	ld [wMusicPlaying], a
	ld hl, wAudioStart
	ld bc, wAudioEnd - wAudioStart
.clear
	xor a
	ld [hli], a
	dec bc
	ld a, b
	or c
	jr nz, .clear
	ld a, RED_ON
	ld [wMusicPlaying], a
	ld e, SFX_STOP_ALL_MUSIC   ; 赤の はじめと 同じ
	call .play
	pop de
.on
	ld hl, .table
.find
	ld a, [hli]
	and a
	ret z                       ; ない 番号は 鳴らさない
	cp e
	ld a, [hli]
	ld d, a
	ld a, [hli]
	jr nz, .find
	and a
	jr z, .sfx
; 曲：赤の PlaySound（wNewSoundID が 0 で ない とき）と 同じく、効果音の チャンネルの 番号を けす
	xor a
	ld [wChannelSoundIDs + CHAN5], a
	ld [wChannelSoundIDs + CHAN6], a
	ld [wChannelSoundIDs + CHAN7], a
	ld [wChannelSoundIDs + CHAN8], a
.sfx
	ld e, d
.play
	ld a, BANK(RedPlayShim)
	ld hl, RedPlayShim
	rst $08
	ret

.table  ; 第53弾の 番号, 赤の 番号, 曲なら 1
	db MUS_TITLE_CR, MUSIC_TITLE_SCREEN, 1
	db MUS_INTRO_CR, MUSIC_INTRO_BATTLE, 1
	db $BE, SFX_SHOOTING_STAR, 0
	db $BF, SFX_INTRO_LUNGE, 0
	db $C0, SFX_INTRO_HIP, 0
	db $C1, SFX_INTRO_HOP, 0
	db $C2, SFX_INTRO_RAISE, 0
	db $C3, SFX_INTRO_CRASH, 0
	db $C4, SFX_INTRO_WHOOSH, 0
	db 0

RedAudioOff:  ; クリスタルの 音に もどす
	xor a
	ld [wMusicPlaying], a
	jp InitSound

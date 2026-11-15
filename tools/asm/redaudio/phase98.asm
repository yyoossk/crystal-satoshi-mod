; この MOD（phase98）：シゲルが 出てくる・去る ときの 曲を 赤の「ライバルあらわる」に（赤の 音の しくみ 1：赤の バンク 2）
;   赤（日本版）の バンク 2（Audio Engine 1 と 曲）を バンク RED_AUDIO1_BANK に 写す（build_phase98.py。音の RAM は $C101〜 に ずらす）。
;   スクリプトの playmusic $F0〜$F3 で 鳴らす（$F0 はじめから・$F1 Music_RivalAlternateStart・$F2 AlternateTempo・$F3 AlternateStartAndTempo）。
;   $C100 = RED1_ON の あいだ、_UpdateSound の かわりに 赤の Audio1_UpdateMusic。クリスタルの 曲（_PlayMusic）が 鳴る ときは
;   先に クリスタルの 音を 初期化して もどす。

DEF InitSound     EQU $3ADB
DEF RED_ON        EQU $A5
DEF RED1_ON       EQU $A6
DEF wMusicPlaying EQU $C100
DEF wAudioStart   EQU $C101
DEF wAudioEnd     EQU $C2C0
DEF rAUDVOL       EQU $FF24
DEF Audio3_UpdateMusic EQU $4417
DEF Audio1_UpdateMusic EQU $4000
DEF Audio1_PlaySound   EQU $4773
DEF wChannelSoundIDs   EQU $C127
DEF wChannelCommandPointers EQU $C107
DEF MUSIC_MEET_RIVAL   EQU $DE
DEF Ch1_AlternateTempo EQU $6016
DEF Ch1_AlternateStartAndTempo EQU $6098
DEF Ch1_AlternateStart EQU $609F
DEF Ch2_AlternateStart EQU $611A
DEF Ch3_AlternateStart EQU $61B2
DEF _InitSound    EQU $4000          ; バンク $3A
DEF MusicOff      EQU $4057          ; バンク $3A

; ---------------------------------------------------------------- _UpdateSound の 頭（第68弾の フックを 書きかえ）
SECTION "p98 UpdateSound hook", ROMX[$7FC8], BANK[$3A]
RedUpdateHook:
	ld a, [wMusicPlaying]
	cp RED_ON
	jr c, .crystal
	ld a, BANK(RedUpdate)
	ld hl, RedUpdate
	rst $08
	ret
.crystal
	and a
	ret z
	jp $4061

; ---------------------------------------------------------------- _PlayMusic の 頭（call MusicOff の 所）
SECTION "p98 PlayMusic head", ROMX[$4B30], BANK[$3A]
	call PlayMusicHook

SECTION "p98 PlayMusic hook", ROMX[$7FC8 + 19], BANK[$3A]
PlayMusicHook:  ; de = 曲
	ld a, [wMusicPlaying]
	cp RED_ON
	jr c, .notred
	push de
	call _InitSound              ; 赤の 音の あと：クリスタルの 音を 初期化
	pop de
	xor a
	ld [wMusicPlaying], a
.notred
	ld a, d
	and a
	jr nz, .normal
	ld a, e
	cp $F0
	jr c, .normal
	pop hl                      ; _PlayMusic の のこりは とばす
	ld a, BANK(RivalMusic)
	ld hl, RivalMusic
	rst $08
	ret
.normal
	jp MusicOff

; ---------------------------------------------------------------- 赤の バンク 2 の 中（つかわない 赤の 鳴き声 Cry00 の 所）
SECTION "p98 engine1 shim", ROMX[$78B5], BANK[RED_AUDIO1_BANK]
Red1Start:  ; e = $F0〜$F3
	push de
	ld a, $FF                   ; SFX_STOP_ALL_MUSIC（赤の はじめと 同じ）
	call Audio1_PlaySound
	xor a
	ld [wChannelSoundIDs + 4], a
	ld [wChannelSoundIDs + 5], a
	ld [wChannelSoundIDs + 6], a
	ld [wChannelSoundIDs + 7], a
	ld a, MUSIC_MEET_RIVAL
	call Audio1_PlaySound
	pop de
	ld a, e
	cp $F2
	jr z, .tempo
	cp $F0
	ret z
	; $F1 / $F3：Music_RivalAlternateStart
	ld hl, wChannelCommandPointers
	ld de, Ch1_AlternateStart
	call .over
	ld de, Ch2_AlternateStart
	call .over
	ld de, Ch3_AlternateStart
	call .over
	cp $F3
	ret nz
	ld hl, wChannelCommandPointers
	ld de, Ch1_AlternateStartAndTempo
	jr .over
.tempo
	ld hl, wChannelCommandPointers
	ld de, Ch1_AlternateTempo
.over
	push af
	ld a, e
	ld [hli], a
	ld a, d
	ld [hli], a
	pop af
	ret

; ---------------------------------------------------------------- 入り口（第68弾の つなぎの バンク）
SECTION "p98 glue", ROMX[$4100], BANK[RED_GLUE_BANK]
RedUpdate:
	ld a, $77
	ldh [rAUDVOL], a
	ld a, [wMusicPlaying]
	cp RED1_ON
	jr z, .one
	ld a, RED_AUDIO_BANK
	ld hl, Audio3_UpdateMusic
	rst $08
	ret
.one
	ld a, RED_AUDIO1_BANK
	ld hl, Audio1_UpdateMusic
	rst $08
	ret

RivalMusic:  ; e = $F0〜$F3（クリスタルの 音は 止まって いる）
	push de
	xor a
	ld [wMusicPlaying], a
	call InitSound
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
	ld a, RED1_ON
	ld [wMusicPlaying], a
	pop de
	ld a, RED_AUDIO1_BANK
	ld hl, Red1Start
	rst $08
	ret

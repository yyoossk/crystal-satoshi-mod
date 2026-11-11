; Phase 52: Red's Oak speech (the rival is named here: wGreensName, shown in every Kanto text as <GREEN>)
INCLUDE "jp.inc"

SECTION "Phase52", ROMX[CODE_ADDR], BANK[CODE_BANK]

RedOakSpeech::
	farcall_ $24, $469E                 ; InitClock (Crystal: the clock is still set first)
	call RotateFourPalettesLeft
	call ClearTilemap
	ld de, OAK_MUSIC
	call PlayMusic
	call RotateFourPalettesRight
	call RotateThreePalettesRight

; Prof. Oak
	ld a, POKEMON_PROF
	call ShowTrainerPic
	ld hl, OakText1
	call PrintText
	call RotateThreePalettesRight
	call ClearTilemap

; Nidorino
	ld a, NIDORINO
	ld [wCurSpecies], a
	ld [wCurPartySpecies], a
	call GetBaseData
	ld hl, $C4F6                        ; hlcoord 6, 4
	call PrepMonFrontpic
	xor a
	ld [wTempMonDVs], a
	ld [wTempMonDVs + 1], a
	ld b, SCGB_TRAINER_OR_MON_FRONTPIC_PALS
	call GetSGBLayout
	farcall_ $01, $62FC                 ; Intro_WipeInFrontpic
	ld hl, OakText2
	call PrintText
	call RotateThreePalettesRight
	call ClearTilemap

; the player
	call ShowPlayerPic
	ld hl, OakText3
	call PrintText
	farcall_ $01, $6208                 ; NamePlayer
	ld hl, OakText4
	call PrintText
	call RotateThreePalettesRight
	call ClearTilemap

; the rival
	ld a, BLUE_CLASS
	call ShowTrainerPic
	ld hl, OakText5
	call PrintText
	call NameRival
	ld hl, OakText6
	call PrintText
	call RotateThreePalettesRight
	call ClearTilemap

; the player again
	call ShowPlayerPic
	ld hl, OakText7
	jp PrintText

ShowTrainerPic:
	ld [wTrainerClass], a
	xor a
	ld [wCurPartySpecies], a
	farcall_ $01, $6316                 ; Intro_PrepTrainerPic
FadeInPic:
	ld b, SCGB_TRAINER_OR_MON_FRONTPIC_PALS
	call GetSGBLayout
	farcall_ $01, $62E4                 ; Intro_RotatePalettesLeftFrontpic
	ret

ShowPlayerPic:
	xor a
	ld [wCurPartySpecies], a
	farcall_ $22, $487D                 ; DrawIntroPlayerPic
	jr FadeInPic

NameRival:
	ld hl, RIVAL_NAMED_BYTE
	set RIVAL_NAMED_BIT, [hl]
	farcall_ $22, $426D                 ; MovePlayerPicRight
	ld hl, RivalNameMenuHeader
	call LoadMenuHeader
	call VerticalMenu
	ld a, [wMenuCursorY]
	dec a
	jr z, .new_name
	call CopyNameFromMenu
	call CloseWindow
	ld a, $50
	ld bc, 6
	ld hl, wGreensName
	call ByteFill
	ld hl, wGreensName
	ld de, wStringBuffer2
	call CopyName2
	farcall_ $02, $4C1D                 ; ApplyMonOrTrainerPals
	farcall_ $22, $4275                 ; MovePlayerPicLeft
	ret

.new_name
	ld b, 2                             ; NAME_RIVAL
	ld de, wGreensName
	farcall_ $04, $565B                 ; NamingScreen
	call RotateThreePalettesRight
	call ClearTilemap
	call LoadFontsExtra
	call WaitBGMap
	ld a, BLUE_CLASS
	ld [wTrainerClass], a
	xor a
	ld [wCurPartySpecies], a
	farcall_ $01, $6316                 ; Intro_PrepTrainerPic
	ld b, SCGB_TRAINER_OR_MON_FRONTPIC_PALS
	call GetSGBLayout
	call RotateThreePalettesLeft
	ld hl, wGreensName
	ld de, DefaultRivalName
	jp InitName

OakText2Cry:
	ld a, NIDORINO
	call PlayMonCry
	call WaitSFX
	ld hl, OakText2b
	ret

INCLUDE "phase52_data.inc"

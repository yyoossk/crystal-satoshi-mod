; ポケットモンスターピカチュウフルカラー 151匹そろう版 のつり（pokecrystal の fish.asm の形）
; ボロのつりざお: コイキング Lv5 だけ。いいつりざお: トサキント Lv10・ニョロモ Lv10 が半分ずつ（どこでも同じ）。
; すごいつりざお: マップごとに 4わく 25% ずつ（同じ中身のマップは 1つのグループにまとめた）。
; FishGroups の表に下の fishgroup を足し、constants/map_data_constants.asm に FISHGROUP_KANTO151_* を足して、
; 各マップ（data/maps/maps.asm の map の 8番め）を下の「マップ → グループ」のとおりにする。

; ---- FishGroups に足す（はじめの数は つれる率。クリスタルの ほかのグループと同じ 50% にした）
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super0
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super1
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super2
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super3
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super4
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super5
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super6
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super7
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super8
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super9
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super10
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super11
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super12
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super13
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super14
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super15
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super16
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super17
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super18
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super19
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super20
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super21
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super22
	fishgroup 50 percent + 1, .Kanto151_Old, .Kanto151_Good, .Kanto151_Super23

.Kanto151_Old:
	db  33 percent + 1, MAGIKARP,   5
	db  66 percent + 1, MAGIKARP,   5
	db 100 percent,     MAGIKARP,   5
.Kanto151_Good:
	db  25 percent,     GOLDEEN,   10
	db  50 percent,     POLIWAG,   10
	db  75 percent,     GOLDEEN,   10
	db 100 percent,     POLIWAG,   10
.Kanto151_Super0:
	db 25 percent,  STARYU,     10      ; ヒトデマン
	db 50 percent,  TENTACOOL,  10      ; メノクラゲ
	db 75 percent,  STARYU,     5       ; ヒトデマン
	db 100 percent, TENTACOOL,  20      ; メノクラゲ
.Kanto151_Super1:
	db 25 percent,  POLIWAG,    5       ; ニョロモ
	db 50 percent,  POLIWAG,    10      ; ニョロモ
	db 75 percent,  POLIWAG,    15      ; ニョロモ
	db 100 percent, POLIWAG,    10      ; ニョロモ
.Kanto151_Super2:
	db 25 percent,  GOLDEEN,    25      ; トサキント
	db 50 percent,  GOLDEEN,    30      ; トサキント
	db 75 percent,  SEAKING,    30      ; アズマオウ
	db 100 percent, SEAKING,    40      ; アズマオウ
.Kanto151_Super3:
	db 25 percent,  TENTACOOL,  15      ; メノクラゲ
	db 50 percent,  TENTACOOL,  20      ; メノクラゲ
	db 75 percent,  TENTACOOL,  10      ; メノクラゲ
	db 100 percent, HORSEA,     5       ; タッツー
.Kanto151_Super4:
	db 25 percent,  GOLDEEN,    5       ; トサキント
	db 50 percent,  GOLDEEN,    10      ; トサキント
	db 75 percent,  GOLDEEN,    15      ; トサキント
	db 100 percent, GOLDEEN,    20      ; トサキント
.Kanto151_Super5:
	db 25 percent,  MAGIKARP,   5       ; コイキング
	db 50 percent,  MAGIKARP,   10      ; コイキング
	db 75 percent,  MAGIKARP,   15      ; コイキング
	db 100 percent, GYARADOS,   15      ; ギャラドス
.Kanto151_Super6:
	db 25 percent,  STARYU,     15      ; ヒトデマン
	db 50 percent,  TENTACOOL,  15      ; メノクラゲ
	db 75 percent,  STARYU,     10      ; ヒトデマン
	db 100 percent, TENTACOOL,  30      ; メノクラゲ
.Kanto151_Super7:
	db 25 percent,  GOLDEEN,    20      ; トサキント
	db 50 percent,  GOLDEEN,    25      ; トサキント
	db 75 percent,  GOLDEEN,    30      ; トサキント
	db 100 percent, SEAKING,    30      ; アズマオウ
.Kanto151_Super8:
	db 25 percent,  KRABBY,     10      ; クラブ
	db 50 percent,  KRABBY,     15      ; クラブ
	db 75 percent,  KINGLER,    15      ; キングラー
	db 100 percent, KINGLER,    25      ; キングラー
.Kanto151_Super9:
	db 25 percent,  KRABBY,     15      ; クラブ
	db 50 percent,  KRABBY,     20      ; クラブ
	db 75 percent,  HORSEA,     10      ; タッツー
	db 100 percent, KINGLER,    25      ; キングラー
.Kanto151_Super10:
	db 25 percent,  HORSEA,     20      ; タッツー
	db 50 percent,  HORSEA,     25      ; タッツー
	db 75 percent,  SEADRA,     25      ; シードラ
	db 100 percent, SEADRA,     35      ; シードラ
.Kanto151_Super11:
	db 25 percent,  HORSEA,     15      ; タッツー
	db 50 percent,  HORSEA,     20      ; タッツー
	db 75 percent,  TENTACOOL,  10      ; メノクラゲ
	db 100 percent, SEADRA,     20      ; シードラ
.Kanto151_Super12:
	db 25 percent,  TENTACOOL,  5       ; メノクラゲ
	db 50 percent,  TENTACOOL,  15      ; メノクラゲ
	db 75 percent,  SHELLDER,   25      ; シェルダー
	db 100 percent, SHELLDER,   35      ; シェルダー
.Kanto151_Super13:
	db 25 percent,  TENTACOOL,  15      ; メノクラゲ
	db 50 percent,  SHELLDER,   20      ; シェルダー
	db 75 percent,  SHELLDER,   30      ; シェルダー
	db 100 percent, SHELLDER,   40      ; シェルダー
.Kanto151_Super14:
	db 25 percent,  TENTACOOL,  15      ; メノクラゲ
	db 50 percent,  STARYU,     20      ; ヒトデマン
	db 75 percent,  TENTACOOL,  30      ; メノクラゲ
	db 100 percent, TENTACRUEL, 30      ; ドククラゲ
.Kanto151_Super15:
	db 25 percent,  TENTACOOL,  20      ; メノクラゲ
	db 50 percent,  TENTACRUEL, 20      ; ドククラゲ
	db 75 percent,  STARYU,     30      ; ヒトデマン
	db 100 percent, TENTACRUEL, 40      ; ドククラゲ
.Kanto151_Super16:
	db 25 percent,  POLIWAG,    5       ; ニョロモ
	db 50 percent,  POLIWAG,    10      ; ニョロモ
	db 75 percent,  POLIWAG,    15      ; ニョロモ
	db 100 percent, POLIWHIRL,  15      ; ニョロゾ
.Kanto151_Super17:
	db 25 percent,  POLIWAG,    25      ; ニョロモ
	db 50 percent,  POLIWAG,    30      ; ニョロモ
	db 75 percent,  POLIWHIRL,  30      ; ニョロゾ
	db 100 percent, POLIWHIRL,  40      ; ニョロゾ
.Kanto151_Super18:
	db 25 percent,  TENTACOOL,  10      ; メノクラゲ
	db 50 percent,  TENTACOOL,  15      ; メノクラゲ
	db 75 percent,  STARYU,     15      ; ヒトデマン
	db 100 percent, SHELLDER,   10      ; シェルダー
.Kanto151_Super19:
	db 25 percent,  MAGIKARP,   5       ; コイキング
	db 50 percent,  MAGIKARP,   10      ; コイキング
	db 75 percent,  DRATINI,    10      ; ミニリュウ
	db 100 percent, DRAGONAIR,  15      ; ハクリュー
.Kanto151_Super20:
	db 25 percent,  MAGIKARP,   5       ; コイキング
	db 50 percent,  MAGIKARP,   10      ; コイキング
	db 75 percent,  MAGIKARP,   15      ; コイキング
	db 100 percent, DRATINI,    15      ; ミニリュウ
.Kanto151_Super21:
	db 25 percent,  KRABBY,     25      ; クラブ
	db 50 percent,  STARYU,     20      ; ヒトデマン
	db 75 percent,  KINGLER,    35      ; キングラー
	db 100 percent, STARYU,     40      ; ヒトデマン
.Kanto151_Super22:
	db 25 percent,  GOLDEEN,    25      ; トサキント
	db 50 percent,  SEAKING,    35      ; アズマオウ
	db 75 percent,  SEAKING,    45      ; アズマオウ
	db 100 percent, SEAKING,    55      ; アズマオウ
.Kanto151_Super23:
	db 25 percent,  GOLDEEN,    30      ; トサキント
	db 50 percent,  SEAKING,    40      ; アズマオウ
	db 75 percent,  SEAKING,    50      ; アズマオウ
	db 100 percent, SEAKING,    60      ; アズマオウ

; ---- マップ → グループ（FISHGROUP_KANTO151_<番号>。番号は上の .Kanto151_Super<番号>）
; PALLET_TOWN              FISHGROUP_KANTO151_0
; VIRIDIAN_CITY            FISHGROUP_KANTO151_1
; CERULEAN_CITY            FISHGROUP_KANTO151_2
; VERMILION_CITY           FISHGROUP_KANTO151_3
; CELADON_CITY             FISHGROUP_KANTO151_4
; FUCHSIA_CITY             FISHGROUP_KANTO151_5
; CINNABAR_ISLAND          FISHGROUP_KANTO151_6
; ROUTE_4                  FISHGROUP_KANTO151_7
; ROUTE_6                  FISHGROUP_KANTO151_4
; ROUTE_24                 FISHGROUP_KANTO151_7
; ROUTE_25                 FISHGROUP_KANTO151_8
; ROUTE_10                 FISHGROUP_KANTO151_9
; ROUTE_11                 FISHGROUP_KANTO151_3
; ROUTE_12                 FISHGROUP_KANTO151_10
; ROUTE_13                 FISHGROUP_KANTO151_11
; ROUTE_17                 FISHGROUP_KANTO151_12
; ROUTE_18                 FISHGROUP_KANTO151_13
; ROUTE_19                 FISHGROUP_KANTO151_14
; ROUTE_20                 FISHGROUP_KANTO151_15
; ROUTE_21                 FISHGROUP_KANTO151_14
; ROUTE_22                 FISHGROUP_KANTO151_16
; ROUTE_23                 FISHGROUP_KANTO151_17
; VERMILION_DOCK           FISHGROUP_KANTO151_18
; SAFARI_ZONE_CENTER       FISHGROUP_KANTO151_19
; SAFARI_ZONE_EAST         FISHGROUP_KANTO151_20
; SAFARI_ZONE_NORTH        FISHGROUP_KANTO151_20
; SAFARI_ZONE_WEST         FISHGROUP_KANTO151_20
; SEAFOAM_ISLANDS_B3F      FISHGROUP_KANTO151_21
; SEAFOAM_ISLANDS_B4F      FISHGROUP_KANTO151_21
; CERULEAN_CAVE_1F         FISHGROUP_KANTO151_22
; CERULEAN_CAVE_B1F        FISHGROUP_KANTO151_23

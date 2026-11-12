; ポケットモンスターピカチュウフルカラー 151匹そろう版 のカントーの野生（なみのり）
; pokecrystal の kanto_water.asm の形。元の 10わくを クリスタルの 3わく（60・30・10%）に分けなおしたもの。

KantoWaterWildMons151:

	def_water_wildmons ROUTE_6
	db 1 percent ; encounter rate
	db 15, PSYDUCK          ; コダック
	db 15, GOLDUCK          ; ゴルダック
	db 15, PSYDUCK          ; コダック
	end_water_wildmons

	def_water_wildmons ROUTE_12
	db 1 percent ; encounter rate
	db 15, SLOWPOKE         ; ヤドン
	db 15, SLOWBRO          ; ヤドラン
	db 15, SLOWPOKE         ; ヤドン
	end_water_wildmons

	def_water_wildmons ROUTE_13
	db 1 percent ; encounter rate
	db 15, SLOWPOKE         ; ヤドン
	db 15, SLOWBRO          ; ヤドラン
	db 15, SLOWPOKE         ; ヤドン
	end_water_wildmons

	def_water_wildmons ROUTE_19
	db 2 percent ; encounter rate
	db 5, TENTACOOL         ; メノクラゲ
	db 10, TENTACOOL        ; メノクラゲ
	db 15, TENTACOOL        ; メノクラゲ
	end_water_wildmons

	def_water_wildmons ROUTE_20
	db 2 percent ; encounter rate
	db 5, TENTACOOL         ; メノクラゲ
	db 10, TENTACOOL        ; メノクラゲ
	db 15, TENTACOOL        ; メノクラゲ
	end_water_wildmons

	def_water_wildmons ROUTE_21
	db 2 percent ; encounter rate
	db 5, TENTACOOL         ; メノクラゲ
	db 10, TENTACOOL        ; メノクラゲ
	db 15, TENTACOOL        ; メノクラゲ
	end_water_wildmons

	def_water_wildmons SEAFOAM_ISLANDS_B3F
	db 2 percent ; encounter rate
	db 25, TENTACOOL        ; メノクラゲ
	db 30, STARYU           ; ヒトデマン
	db 30, TENTACOOL        ; メノクラゲ
	end_water_wildmons

	def_water_wildmons SEAFOAM_ISLANDS_B4F
	db 2 percent ; encounter rate
	db 25, TENTACOOL        ; メノクラゲ
	db 30, STARYU           ; ヒトデマン
	db 30, TENTACOOL        ; メノクラゲ
	end_water_wildmons

	db -1 ; end

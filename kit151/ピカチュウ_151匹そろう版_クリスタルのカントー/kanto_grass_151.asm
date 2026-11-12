; ポケットモンスターピカチュウフルカラー 151匹そろう版 のカントーの野生（くさむら・どうくつ）
; pokecrystal の kanto_grass.asm の形。元のデータ（10わく）を クリスタルの 7わく（30・30・20・10・5・4・1%）に分けなおしたもの。
; 朝・昼・夜は同じ（151匹そろう版には時間がない）。8種類より多い所だけ、めずらしいポケモンを朝・昼・夜に分けて、どれかの時間に出るようにした。
; マップの名前は ピカチュウ（pokeyellow）のもの。この MOD のマップの名前にかえる。

KantoGrassWildMons151:

	def_grass_wildmons ROUTE_1
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 3, PIDGEY            ; ポッポ
	db 2, RATTATA           ; コラッタ
	db 4, PIDGEY            ; ポッポ
	db 2, PIDGEY            ; ポッポ
	db 5, PIDGEY            ; ポッポ
	db 6, PIDGEY            ; ポッポ
	db 7, PIDGEY            ; ポッポ
	; day
	db 3, PIDGEY            ; ポッポ
	db 2, RATTATA           ; コラッタ
	db 4, PIDGEY            ; ポッポ
	db 2, PIDGEY            ; ポッポ
	db 5, PIDGEY            ; ポッポ
	db 6, PIDGEY            ; ポッポ
	db 7, PIDGEY            ; ポッポ
	; nite
	db 3, PIDGEY            ; ポッポ
	db 2, RATTATA           ; コラッタ
	db 4, PIDGEY            ; ポッポ
	db 2, PIDGEY            ; ポッポ
	db 5, PIDGEY            ; ポッポ
	db 6, PIDGEY            ; ポッポ
	db 7, PIDGEY            ; ポッポ
	end_grass_wildmons

	def_grass_wildmons ROUTE_2
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 3, RATTATA           ; コラッタ
	db 3, PIDGEY            ; ポッポ
	db 4, NIDORAN_M         ; ニドラン♂
	db 4, NIDORAN_F         ; ニドラン♀
	db 3, WEEDLE            ; ビードル
	db 4, WEEDLE            ; ビードル
	db 4, RATTATA           ; コラッタ
	; day
	db 3, RATTATA           ; コラッタ
	db 3, PIDGEY            ; ポッポ
	db 4, NIDORAN_M         ; ニドラン♂
	db 4, NIDORAN_F         ; ニドラン♀
	db 3, WEEDLE            ; ビードル
	db 4, WEEDLE            ; ビードル
	db 4, RATTATA           ; コラッタ
	; nite
	db 3, RATTATA           ; コラッタ
	db 3, PIDGEY            ; ポッポ
	db 4, NIDORAN_M         ; ニドラン♂
	db 4, NIDORAN_F         ; ニドラン♀
	db 3, WEEDLE            ; ビードル
	db 4, WEEDLE            ; ビードル
	db 4, RATTATA           ; コラッタ
	end_grass_wildmons

	def_grass_wildmons ROUTE_3
	db 8 percent, 8 percent, 8 percent ; encounter rates: morn/day/nite
	; morn
	db 8, SPEAROW           ; オニスズメ
	db 9, MANKEY            ; マンキー
	db 8, SANDSHREW         ; サンド
	db 10, RATTATA          ; コラッタ
	db 9, SPEAROW           ; オニスズメ
	db 10, SPEAROW          ; オニスズメ
	db 11, SPEAROW          ; オニスズメ
	; day
	db 8, SPEAROW           ; オニスズメ
	db 9, MANKEY            ; マンキー
	db 8, SANDSHREW         ; サンド
	db 10, RATTATA          ; コラッタ
	db 9, SPEAROW           ; オニスズメ
	db 10, SPEAROW          ; オニスズメ
	db 11, SPEAROW          ; オニスズメ
	; nite
	db 8, SPEAROW           ; オニスズメ
	db 9, MANKEY            ; マンキー
	db 8, SANDSHREW         ; サンド
	db 10, RATTATA          ; コラッタ
	db 9, SPEAROW           ; オニスズメ
	db 10, SPEAROW          ; オニスズメ
	db 11, SPEAROW          ; オニスズメ
	end_grass_wildmons

	def_grass_wildmons ROUTE_4
	db 8 percent, 8 percent, 8 percent ; encounter rates: morn/day/nite
	; morn
	db 8, SPEAROW           ; オニスズメ
	db 6, EKANS             ; アーボ
	db 9, MANKEY            ; マンキー
	db 8, SANDSHREW         ; サンド
	db 12, RATTATA          ; コラッタ
	db 9, SPEAROW           ; オニスズメ
	db 8, SPEAROW           ; オニスズメ
	; day
	db 8, SPEAROW           ; オニスズメ
	db 6, EKANS             ; アーボ
	db 9, MANKEY            ; マンキー
	db 8, SANDSHREW         ; サンド
	db 12, RATTATA          ; コラッタ
	db 9, SPEAROW           ; オニスズメ
	db 8, SPEAROW           ; オニスズメ
	; nite
	db 8, SPEAROW           ; オニスズメ
	db 6, EKANS             ; アーボ
	db 9, MANKEY            ; マンキー
	db 8, SANDSHREW         ; サンド
	db 12, RATTATA          ; コラッタ
	db 9, SPEAROW           ; オニスズメ
	db 8, SPEAROW           ; オニスズメ
	end_grass_wildmons

	def_grass_wildmons ROUTE_5
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 15, PIDGEY           ; ポッポ
	db 10, MEOWTH           ; ニャース
	db 14, RATTATA          ; コラッタ
	db 7, ABRA              ; ケーシィ
	db 17, PIDGEOTTO        ; ピジョン
	db 3, JIGGLYPUFF        ; プリン
	db 7, ABRA              ; ケーシィ
	; day
	db 15, PIDGEY           ; ポッポ
	db 10, MEOWTH           ; ニャース
	db 14, RATTATA          ; コラッタ
	db 7, ABRA              ; ケーシィ
	db 17, PIDGEOTTO        ; ピジョン
	db 3, JIGGLYPUFF        ; プリン
	db 7, ABRA              ; ケーシィ
	; nite
	db 15, PIDGEY           ; ポッポ
	db 10, MEOWTH           ; ニャース
	db 14, RATTATA          ; コラッタ
	db 7, ABRA              ; ケーシィ
	db 17, PIDGEOTTO        ; ピジョン
	db 3, JIGGLYPUFF        ; プリン
	db 7, ABRA              ; ケーシィ
	end_grass_wildmons

	def_grass_wildmons ROUTE_6
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 15, PIDGEY           ; ポッポ
	db 10, MEOWTH           ; ニャース
	db 14, RATTATA          ; コラッタ
	db 7, ABRA              ; ケーシィ
	db 17, PIDGEOTTO        ; ピジョン
	db 3, JIGGLYPUFF        ; プリン
	db 7, ABRA              ; ケーシィ
	; day
	db 15, PIDGEY           ; ポッポ
	db 10, MEOWTH           ; ニャース
	db 14, RATTATA          ; コラッタ
	db 7, ABRA              ; ケーシィ
	db 17, PIDGEOTTO        ; ピジョン
	db 3, JIGGLYPUFF        ; プリン
	db 7, ABRA              ; ケーシィ
	; nite
	db 15, PIDGEY           ; ポッポ
	db 10, MEOWTH           ; ニャース
	db 14, RATTATA          ; コラッタ
	db 7, ABRA              ; ケーシィ
	db 17, PIDGEOTTO        ; ピジョン
	db 3, JIGGLYPUFF        ; プリン
	db 7, ABRA              ; ケーシィ
	end_grass_wildmons

	def_grass_wildmons ROUTE_7
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 20, PIDGEY           ; ポッポ
	db 17, MEOWTH           ; ニャース
	db 15, ABRA             ; ケーシィ
	db 24, PIDGEOTTO        ; ピジョン
	db 18, VULPIX           ; ロコン
	db 22, PIDGEY           ; ポッポ
	db 20, PIDGEY           ; ポッポ
	; day
	db 20, PIDGEY           ; ポッポ
	db 17, MEOWTH           ; ニャース
	db 15, ABRA             ; ケーシィ
	db 24, PIDGEOTTO        ; ピジョン
	db 18, VULPIX           ; ロコン
	db 22, PIDGEY           ; ポッポ
	db 20, PIDGEY           ; ポッポ
	; nite
	db 20, PIDGEY           ; ポッポ
	db 17, MEOWTH           ; ニャース
	db 15, ABRA             ; ケーシィ
	db 24, PIDGEOTTO        ; ピジョン
	db 18, VULPIX           ; ロコン
	db 22, PIDGEY           ; ポッポ
	db 20, PIDGEY           ; ポッポ
	end_grass_wildmons

	def_grass_wildmons ROUTE_8
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 20, PIDGEY           ; ポッポ
	db 18, MEOWTH           ; ニャース
	db 15, ABRA             ; ケーシィ
	db 17, EKANS            ; アーボ
	db 24, PIDGEOTTO        ; ピジョン
	db 18, VULPIX           ; ロコン
	db 20, KADABRA          ; ユンゲラー
	; day
	db 20, PIDGEY           ; ポッポ
	db 18, MEOWTH           ; ニャース
	db 15, ABRA             ; ケーシィ
	db 17, EKANS            ; アーボ
	db 24, PIDGEOTTO        ; ピジョン
	db 18, VULPIX           ; ロコン
	db 20, KADABRA          ; ユンゲラー
	; nite
	db 20, PIDGEY           ; ポッポ
	db 18, MEOWTH           ; ニャース
	db 15, ABRA             ; ケーシィ
	db 17, EKANS            ; アーボ
	db 24, PIDGEOTTO        ; ピジョン
	db 18, VULPIX           ; ロコン
	db 20, KADABRA          ; ユンゲラー
	end_grass_wildmons

	def_grass_wildmons ROUTE_9
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 16, NIDORAN_F        ; ニドラン♀
	db 16, NIDORAN_M        ; ニドラン♂
	db 18, RATTATA          ; コラッタ
	db 17, EKANS            ; アーボ
	db 17, SPEAROW          ; オニスズメ
	db 18, NIDORINO         ; ニドリーノ
	db 19, FEAROW           ; オニドリル
	; day
	db 16, NIDORAN_F        ; ニドラン♀
	db 16, NIDORAN_M        ; ニドラン♂
	db 18, RATTATA          ; コラッタ
	db 17, EKANS            ; アーボ
	db 17, SPEAROW          ; オニスズメ
	db 18, NIDORINA         ; ニドリーナ
	db 18, NIDORINO         ; ニドリーノ
	; nite
	db 16, NIDORAN_F        ; ニドラン♀
	db 16, NIDORAN_M        ; ニドラン♂
	db 18, RATTATA          ; コラッタ
	db 17, EKANS            ; アーボ
	db 17, SPEAROW          ; オニスズメ
	db 18, NIDORINO         ; ニドリーノ
	db 20, RATICATE         ; ラッタ
	end_grass_wildmons

	def_grass_wildmons ROUTE_10
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 16, MAGNEMITE        ; コイル
	db 18, RATTATA          ; コラッタ
	db 17, EKANS            ; アーボ
	db 17, NIDORAN_M        ; ニドラン♂
	db 17, NIDORAN_F        ; ニドラン♀
	db 20, RATICATE         ; ラッタ
	db 18, MACHOP           ; ワンリキー
	; day
	db 16, MAGNEMITE        ; コイル
	db 18, RATTATA          ; コラッタ
	db 17, EKANS            ; アーボ
	db 17, NIDORAN_M        ; ニドラン♂
	db 17, NIDORAN_F        ; ニドラン♀
	db 20, RATICATE         ; ラッタ
	db 18, MACHOP           ; ワンリキー
	; nite
	db 16, MAGNEMITE        ; コイル
	db 18, RATTATA          ; コラッタ
	db 17, EKANS            ; アーボ
	db 17, NIDORAN_M        ; ニドラン♂
	db 17, NIDORAN_F        ; ニドラン♀
	db 20, RATICATE         ; ラッタ
	db 18, MACHOP           ; ワンリキー
	end_grass_wildmons

	def_grass_wildmons ROUTE_11
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 15, RATTATA          ; コラッタ
	db 14, EKANS            ; アーボ
	db 15, DROWZEE          ; スリープ
	db 18, PIDGEY           ; ポッポ
	db 20, PIDGEOTTO        ; ピジョン
	db 17, RATICATE         ; ラッタ
	db 18, PIDGEY           ; ポッポ
	; day
	db 15, RATTATA          ; コラッタ
	db 14, EKANS            ; アーボ
	db 15, DROWZEE          ; スリープ
	db 18, PIDGEY           ; ポッポ
	db 20, PIDGEOTTO        ; ピジョン
	db 17, RATICATE         ; ラッタ
	db 18, PIDGEY           ; ポッポ
	; nite
	db 15, RATTATA          ; コラッタ
	db 14, EKANS            ; アーボ
	db 15, DROWZEE          ; スリープ
	db 18, PIDGEY           ; ポッポ
	db 20, PIDGEOTTO        ; ピジョン
	db 17, RATICATE         ; ラッタ
	db 18, PIDGEY           ; ポッポ
	end_grass_wildmons

	def_grass_wildmons ROUTE_12
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 25, ODDISH           ; ナゾノクサ
	db 25, BELLSPROUT       ; マダツボミ
	db 28, PIDGEY           ; ポッポ
	db 28, PIDGEOTTO        ; ピジョン
	db 29, GLOOM            ; クサイハナ
	db 29, WEEPINBELL       ; ウツドン
	db 26, FARFETCH_D       ; カモネギ
	; day
	db 25, ODDISH           ; ナゾノクサ
	db 25, BELLSPROUT       ; マダツボミ
	db 28, PIDGEY           ; ポッポ
	db 28, PIDGEOTTO        ; ピジョン
	db 29, GLOOM            ; クサイハナ
	db 29, WEEPINBELL       ; ウツドン
	db 26, FARFETCH_D       ; カモネギ
	; nite
	db 25, ODDISH           ; ナゾノクサ
	db 25, BELLSPROUT       ; マダツボミ
	db 28, PIDGEY           ; ポッポ
	db 28, PIDGEOTTO        ; ピジョン
	db 29, GLOOM            ; クサイハナ
	db 29, WEEPINBELL       ; ウツドン
	db 26, FARFETCH_D       ; カモネギ
	end_grass_wildmons

	def_grass_wildmons ROUTE_13
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 25, ODDISH           ; ナゾノクサ
	db 25, BELLSPROUT       ; マダツボミ
	db 28, PIDGEOTTO        ; ピジョン
	db 28, PIDGEY           ; ポッポ
	db 29, GLOOM            ; クサイハナ
	db 29, WEEPINBELL       ; ウツドン
	db 26, FARFETCH_D       ; カモネギ
	; day
	db 25, ODDISH           ; ナゾノクサ
	db 25, BELLSPROUT       ; マダツボミ
	db 28, PIDGEOTTO        ; ピジョン
	db 28, PIDGEY           ; ポッポ
	db 29, GLOOM            ; クサイハナ
	db 29, WEEPINBELL       ; ウツドン
	db 26, FARFETCH_D       ; カモネギ
	; nite
	db 25, ODDISH           ; ナゾノクサ
	db 25, BELLSPROUT       ; マダツボミ
	db 28, PIDGEOTTO        ; ピジョン
	db 28, PIDGEY           ; ポッポ
	db 29, GLOOM            ; クサイハナ
	db 29, WEEPINBELL       ; ウツドン
	db 26, FARFETCH_D       ; カモネギ
	end_grass_wildmons

	def_grass_wildmons ROUTE_14
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 26, ODDISH           ; ナゾノクサ
	db 26, BELLSPROUT       ; マダツボミ
	db 24, VENONAT          ; コンパン
	db 30, PIDGEOTTO        ; ピジョン
	db 30, GLOOM            ; クサイハナ
	db 30, WEEPINBELL       ; ウツドン
	db 30, VENOMOTH         ; モルフォン
	; day
	db 26, ODDISH           ; ナゾノクサ
	db 26, BELLSPROUT       ; マダツボミ
	db 24, VENONAT          ; コンパン
	db 30, PIDGEOTTO        ; ピジョン
	db 30, GLOOM            ; クサイハナ
	db 30, WEEPINBELL       ; ウツドン
	db 30, VENOMOTH         ; モルフォン
	; nite
	db 26, ODDISH           ; ナゾノクサ
	db 26, BELLSPROUT       ; マダツボミ
	db 24, VENONAT          ; コンパン
	db 30, PIDGEOTTO        ; ピジョン
	db 30, GLOOM            ; クサイハナ
	db 30, WEEPINBELL       ; ウツドン
	db 30, VENOMOTH         ; モルフォン
	end_grass_wildmons

	def_grass_wildmons ROUTE_15
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 26, ODDISH           ; ナゾノクサ
	db 26, BELLSPROUT       ; マダツボミ
	db 24, VENONAT          ; コンパン
	db 32, PIDGEOTTO        ; ピジョン
	db 30, GLOOM            ; クサイハナ
	db 30, WEEPINBELL       ; ウツドン
	db 30, VENOMOTH         ; モルフォン
	; day
	db 26, ODDISH           ; ナゾノクサ
	db 26, BELLSPROUT       ; マダツボミ
	db 24, VENONAT          ; コンパン
	db 32, PIDGEOTTO        ; ピジョン
	db 30, GLOOM            ; クサイハナ
	db 30, WEEPINBELL       ; ウツドン
	db 30, VENOMOTH         ; モルフォン
	; nite
	db 26, ODDISH           ; ナゾノクサ
	db 26, BELLSPROUT       ; マダツボミ
	db 24, VENONAT          ; コンパン
	db 32, PIDGEOTTO        ; ピジョン
	db 30, GLOOM            ; クサイハナ
	db 30, WEEPINBELL       ; ウツドン
	db 30, VENOMOTH         ; モルフォン
	end_grass_wildmons

	def_grass_wildmons ROUTE_16
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 22, DODUO            ; ドードー
	db 22, SPEAROW          ; オニスズメ
	db 23, RATTATA          ; コラッタ
	db 24, FEAROW           ; オニドリル
	db 25, RATICATE         ; ラッタ
	db 24, DODUO            ; ドードー
	db 26, DODUO            ; ドードー
	; day
	db 22, DODUO            ; ドードー
	db 22, SPEAROW          ; オニスズメ
	db 23, RATTATA          ; コラッタ
	db 24, FEAROW           ; オニドリル
	db 25, RATICATE         ; ラッタ
	db 24, DODUO            ; ドードー
	db 26, DODUO            ; ドードー
	; nite
	db 22, DODUO            ; ドードー
	db 22, SPEAROW          ; オニスズメ
	db 23, RATTATA          ; コラッタ
	db 24, FEAROW           ; オニドリル
	db 25, RATICATE         ; ラッタ
	db 24, DODUO            ; ドードー
	db 26, DODUO            ; ドードー
	end_grass_wildmons

	def_grass_wildmons ROUTE_17
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 26, DODUO            ; ドードー
	db 27, FEAROW           ; オニドリル
	db 28, PONYTA           ; ポニータ
	db 29, DODRIO           ; ドードリオ
	db 27, DODUO            ; ドードー
	db 28, DODUO            ; ドードー
	db 26, DODUO            ; ドードー
	; day
	db 26, DODUO            ; ドードー
	db 27, FEAROW           ; オニドリル
	db 28, PONYTA           ; ポニータ
	db 29, DODRIO           ; ドードリオ
	db 27, DODUO            ; ドードー
	db 28, DODUO            ; ドードー
	db 26, DODUO            ; ドードー
	; nite
	db 26, DODUO            ; ドードー
	db 27, FEAROW           ; オニドリル
	db 28, PONYTA           ; ポニータ
	db 29, DODRIO           ; ドードリオ
	db 27, DODUO            ; ドードー
	db 28, DODUO            ; ドードー
	db 26, DODUO            ; ドードー
	end_grass_wildmons

	def_grass_wildmons ROUTE_18
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 22, DODUO            ; ドードー
	db 22, SPEAROW          ; オニスズメ
	db 23, RATTATA          ; コラッタ
	db 24, FEAROW           ; オニドリル
	db 25, RATICATE         ; ラッタ
	db 24, DODUO            ; ドードー
	db 26, DODUO            ; ドードー
	; day
	db 22, DODUO            ; ドードー
	db 22, SPEAROW          ; オニスズメ
	db 23, RATTATA          ; コラッタ
	db 24, FEAROW           ; オニドリル
	db 25, RATICATE         ; ラッタ
	db 24, DODUO            ; ドードー
	db 26, DODUO            ; ドードー
	; nite
	db 22, DODUO            ; ドードー
	db 22, SPEAROW          ; オニスズメ
	db 23, RATTATA          ; コラッタ
	db 24, FEAROW           ; オニドリル
	db 25, RATICATE         ; ラッタ
	db 24, DODUO            ; ドードー
	db 26, DODUO            ; ドードー
	end_grass_wildmons

	def_grass_wildmons ROUTE_21
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 15, PIDGEY           ; ポッポ
	db 13, RATTATA          ; コラッタ
	db 17, PIDGEOTTO        ; ピジョン
	db 17, MR__MIME         ; バリヤード
	db 13, PIDGEY           ; ポッポ
	db 11, PIDGEY           ; ポッポ
	db 17, PIDGEY           ; ポッポ
	; day
	db 15, PIDGEY           ; ポッポ
	db 13, RATTATA          ; コラッタ
	db 17, PIDGEOTTO        ; ピジョン
	db 17, MR__MIME         ; バリヤード
	db 13, PIDGEY           ; ポッポ
	db 11, PIDGEY           ; ポッポ
	db 17, PIDGEY           ; ポッポ
	; nite
	db 15, PIDGEY           ; ポッポ
	db 13, RATTATA          ; コラッタ
	db 17, PIDGEOTTO        ; ピジョン
	db 17, MR__MIME         ; バリヤード
	db 13, PIDGEY           ; ポッポ
	db 11, PIDGEY           ; ポッポ
	db 17, PIDGEY           ; ポッポ
	end_grass_wildmons

	def_grass_wildmons ROUTE_22
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 2, NIDORAN_M         ; ニドラン♂
	db 2, NIDORAN_F         ; ニドラン♀
	db 3, MANKEY            ; マンキー
	db 3, RATTATA           ; コラッタ
	db 2, SPEAROW           ; オニスズメ
	db 4, SPEAROW           ; オニスズメ
	db 6, SPEAROW           ; オニスズメ
	; day
	db 2, NIDORAN_M         ; ニドラン♂
	db 2, NIDORAN_F         ; ニドラン♀
	db 3, MANKEY            ; マンキー
	db 3, RATTATA           ; コラッタ
	db 2, SPEAROW           ; オニスズメ
	db 4, SPEAROW           ; オニスズメ
	db 6, SPEAROW           ; オニスズメ
	; nite
	db 2, NIDORAN_M         ; ニドラン♂
	db 2, NIDORAN_F         ; ニドラン♀
	db 3, MANKEY            ; マンキー
	db 3, RATTATA           ; コラッタ
	db 2, SPEAROW           ; オニスズメ
	db 4, SPEAROW           ; オニスズメ
	db 6, SPEAROW           ; オニスズメ
	end_grass_wildmons

	def_grass_wildmons ROUTE_23
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 41, NIDORINA         ; ニドリーナ
	db 36, EKANS            ; アーボ
	db 36, MANKEY           ; マンキー
	db 44, NIDORINO         ; ニドリーノ
	db 40, FEAROW           ; オニドリル
	db 41, ARBOK            ; アーボック
	db 41, PRIMEAPE         ; オコリザル
	; day
	db 41, NIDORINA         ; ニドリーナ
	db 36, EKANS            ; アーボ
	db 36, MANKEY           ; マンキー
	db 44, NIDORINO         ; ニドリーノ
	db 40, FEAROW           ; オニドリル
	db 41, ARBOK            ; アーボック
	db 41, PRIMEAPE         ; オコリザル
	; nite
	db 41, NIDORINA         ; ニドリーナ
	db 36, EKANS            ; アーボ
	db 36, MANKEY           ; マンキー
	db 44, NIDORINO         ; ニドリーノ
	db 40, FEAROW           ; オニドリル
	db 41, ARBOK            ; アーボック
	db 41, PRIMEAPE         ; オコリザル
	end_grass_wildmons

	def_grass_wildmons ROUTE_24
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 13, PIDGEY           ; ポッポ
	db 12, WEEDLE           ; ビードル
	db 12, KAKUNA           ; コクーン
	db 14, ODDISH           ; ナゾノクサ
	db 14, BELLSPROUT       ; マダツボミ
	db 13, VENONAT          ; コンパン
	db 17, PIDGEOTTO        ; ピジョン
	; day
	db 13, PIDGEY           ; ポッポ
	db 12, WEEDLE           ; ビードル
	db 12, KAKUNA           ; コクーン
	db 14, ODDISH           ; ナゾノクサ
	db 14, BELLSPROUT       ; マダツボミ
	db 13, VENONAT          ; コンパン
	db 17, PIDGEOTTO        ; ピジョン
	; nite
	db 13, PIDGEY           ; ポッポ
	db 12, WEEDLE           ; ビードル
	db 12, KAKUNA           ; コクーン
	db 14, ODDISH           ; ナゾノクサ
	db 14, BELLSPROUT       ; マダツボミ
	db 13, VENONAT          ; コンパン
	db 17, PIDGEOTTO        ; ピジョン
	end_grass_wildmons

	def_grass_wildmons ROUTE_25
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 13, PIDGEY           ; ポッポ
	db 12, KAKUNA           ; コクーン
	db 12, WEEDLE           ; ビードル
	db 14, ODDISH           ; ナゾノクサ
	db 14, BELLSPROUT       ; マダツボミ
	db 13, VENONAT          ; コンパン
	db 17, PIDGEOTTO        ; ピジョン
	; day
	db 13, PIDGEY           ; ポッポ
	db 12, KAKUNA           ; コクーン
	db 12, WEEDLE           ; ビードル
	db 14, ODDISH           ; ナゾノクサ
	db 14, BELLSPROUT       ; マダツボミ
	db 13, VENONAT          ; コンパン
	db 17, PIDGEOTTO        ; ピジョン
	; nite
	db 13, PIDGEY           ; ポッポ
	db 12, KAKUNA           ; コクーン
	db 12, WEEDLE           ; ビードル
	db 14, ODDISH           ; ナゾノクサ
	db 14, BELLSPROUT       ; マダツボミ
	db 13, VENONAT          ; コンパン
	db 17, PIDGEOTTO        ; ピジョン
	end_grass_wildmons

	def_grass_wildmons VIRIDIAN_FOREST
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 4, WEEDLE            ; ビードル
	db 5, KAKUNA            ; コクーン
	db 6, CATERPIE          ; キャタピー
	db 6, METAPOD           ; トランセル
	db 8, PIDGEY            ; ポッポ
	db 9, PIDGEOTTO         ; ピジョン
	db 3, WEEDLE            ; ビードル
	; day
	db 4, WEEDLE            ; ビードル
	db 5, KAKUNA            ; コクーン
	db 6, CATERPIE          ; キャタピー
	db 6, METAPOD           ; トランセル
	db 8, PIDGEY            ; ポッポ
	db 9, PIDGEOTTO         ; ピジョン
	db 3, WEEDLE            ; ビードル
	; nite
	db 4, WEEDLE            ; ビードル
	db 5, KAKUNA            ; コクーン
	db 6, CATERPIE          ; キャタピー
	db 6, METAPOD           ; トランセル
	db 8, PIDGEY            ; ポッポ
	db 9, PIDGEOTTO         ; ピジョン
	db 3, WEEDLE            ; ビードル
	end_grass_wildmons

	def_grass_wildmons MT_MOON_1F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 8, ZUBAT             ; ズバット
	db 10, GEODUDE          ; イシツブテ
	db 12, SANDSHREW        ; サンド
	db 11, CLEFAIRY         ; ピッピ
	db 9, ZUBAT             ; ズバット
	db 6, ZUBAT             ; ズバット
	db 7, ZUBAT             ; ズバット
	; day
	db 8, ZUBAT             ; ズバット
	db 10, GEODUDE          ; イシツブテ
	db 12, SANDSHREW        ; サンド
	db 11, CLEFAIRY         ; ピッピ
	db 9, ZUBAT             ; ズバット
	db 6, ZUBAT             ; ズバット
	db 7, ZUBAT             ; ズバット
	; nite
	db 8, ZUBAT             ; ズバット
	db 10, GEODUDE          ; イシツブテ
	db 12, SANDSHREW        ; サンド
	db 11, CLEFAIRY         ; ピッピ
	db 9, ZUBAT             ; ズバット
	db 6, ZUBAT             ; ズバット
	db 7, ZUBAT             ; ズバット
	end_grass_wildmons

	def_grass_wildmons MT_MOON_B1F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 8, ZUBAT             ; ズバット
	db 10, GEODUDE          ; イシツブテ
	db 9, PARAS             ; パラス
	db 10, CLEFAIRY         ; ピッピ
	db 9, ZUBAT             ; ズバット
	db 10, ZUBAT            ; ズバット
	db 11, ZUBAT            ; ズバット
	; day
	db 8, ZUBAT             ; ズバット
	db 10, GEODUDE          ; イシツブテ
	db 9, PARAS             ; パラス
	db 10, CLEFAIRY         ; ピッピ
	db 9, ZUBAT             ; ズバット
	db 10, ZUBAT            ; ズバット
	db 11, ZUBAT            ; ズバット
	; nite
	db 8, ZUBAT             ; ズバット
	db 10, GEODUDE          ; イシツブテ
	db 9, PARAS             ; パラス
	db 10, CLEFAIRY         ; ピッピ
	db 9, ZUBAT             ; ズバット
	db 10, ZUBAT            ; ズバット
	db 11, ZUBAT            ; ズバット
	end_grass_wildmons

	def_grass_wildmons MT_MOON_B2F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 10, ZUBAT            ; ズバット
	db 11, GEODUDE          ; イシツブテ
	db 13, PARAS            ; パラス
	db 9, CLEFAIRY          ; ピッピ
	db 11, ZUBAT            ; ズバット
	db 12, ZUBAT            ; ズバット
	db 13, ZUBAT            ; ズバット
	; day
	db 10, ZUBAT            ; ズバット
	db 11, GEODUDE          ; イシツブテ
	db 13, PARAS            ; パラス
	db 9, CLEFAIRY          ; ピッピ
	db 11, ZUBAT            ; ズバット
	db 12, ZUBAT            ; ズバット
	db 13, ZUBAT            ; ズバット
	; nite
	db 10, ZUBAT            ; ズバット
	db 11, GEODUDE          ; イシツブテ
	db 13, PARAS            ; パラス
	db 9, CLEFAIRY          ; ピッピ
	db 11, ZUBAT            ; ズバット
	db 12, ZUBAT            ; ズバット
	db 13, ZUBAT            ; ズバット
	end_grass_wildmons

	def_grass_wildmons ROCK_TUNNEL_1F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 15, ZUBAT            ; ズバット
	db 16, GEODUDE          ; イシツブテ
	db 17, MACHOP           ; ワンリキー
	db 17, ZUBAT            ; ズバット
	db 19, ZUBAT            ; ズバット
	db 18, GEODUDE          ; イシツブテ
	db 20, GEODUDE          ; イシツブテ
	; day
	db 15, ZUBAT            ; ズバット
	db 16, GEODUDE          ; イシツブテ
	db 17, MACHOP           ; ワンリキー
	db 17, ZUBAT            ; ズバット
	db 19, ZUBAT            ; ズバット
	db 18, GEODUDE          ; イシツブテ
	db 20, GEODUDE          ; イシツブテ
	; nite
	db 15, ZUBAT            ; ズバット
	db 16, GEODUDE          ; イシツブテ
	db 17, MACHOP           ; ワンリキー
	db 17, ZUBAT            ; ズバット
	db 19, ZUBAT            ; ズバット
	db 18, GEODUDE          ; イシツブテ
	db 20, GEODUDE          ; イシツブテ
	end_grass_wildmons

	def_grass_wildmons POWER_PLANT
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 30, MAGNEMITE        ; コイル
	db 33, MAGNETON         ; レアコイル
	db 33, VOLTORB          ; ビリリダマ
	db 33, GRIMER           ; ベトベター
	db 33, RAICHU           ; ライチュウ
	db 33, ELECTABUZZ       ; エレブー
	db 37, MUK              ; ベトベトン
	; day
	db 30, MAGNEMITE        ; コイル
	db 33, MAGNETON         ; レアコイル
	db 33, VOLTORB          ; ビリリダマ
	db 33, GRIMER           ; ベトベター
	db 33, RAICHU           ; ライチュウ
	db 33, ELECTABUZZ       ; エレブー
	db 37, MUK              ; ベトベトン
	; nite
	db 30, MAGNEMITE        ; コイル
	db 33, MAGNETON         ; レアコイル
	db 33, VOLTORB          ; ビリリダマ
	db 33, GRIMER           ; ベトベター
	db 33, RAICHU           ; ライチュウ
	db 33, ELECTABUZZ       ; エレブー
	db 37, MUK              ; ベトベトン
	end_grass_wildmons

	def_grass_wildmons VICTORY_ROAD_1F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 26, GEODUDE          ; イシツブテ
	db 39, ZUBAT            ; ズバット
	db 43, ONIX             ; イワーク
	db 41, GRAVELER         ; ゴローン
	db 31, GEODUDE          ; イシツブテ
	db 36, GEODUDE          ; イシツブテ
	db 41, GEODUDE          ; イシツブテ
	; day
	db 26, GEODUDE          ; イシツブテ
	db 39, ZUBAT            ; ズバット
	db 43, ONIX             ; イワーク
	db 41, GRAVELER         ; ゴローン
	db 31, GEODUDE          ; イシツブテ
	db 36, GEODUDE          ; イシツブテ
	db 41, GEODUDE          ; イシツブテ
	; nite
	db 26, GEODUDE          ; イシツブテ
	db 39, ZUBAT            ; ズバット
	db 43, ONIX             ; イワーク
	db 41, GRAVELER         ; ゴローン
	db 31, GEODUDE          ; イシツブテ
	db 36, GEODUDE          ; イシツブテ
	db 41, GEODUDE          ; イシツブテ
	end_grass_wildmons

	def_grass_wildmons POKEMON_TOWER_3F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 20, GASTLY           ; ゴース
	db 20, HAUNTER          ; ゴースト
	db 21, GASTLY           ; ゴース
	db 22, GASTLY           ; ゴース
	db 19, GASTLY           ; ゴース
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	; day
	db 20, GASTLY           ; ゴース
	db 20, HAUNTER          ; ゴースト
	db 21, GASTLY           ; ゴース
	db 22, GASTLY           ; ゴース
	db 19, GASTLY           ; ゴース
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	; nite
	db 20, GASTLY           ; ゴース
	db 20, HAUNTER          ; ゴースト
	db 21, GASTLY           ; ゴース
	db 22, GASTLY           ; ゴース
	db 19, GASTLY           ; ゴース
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	end_grass_wildmons

	def_grass_wildmons POKEMON_TOWER_4F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 20, GASTLY           ; ゴース
	db 20, HAUNTER          ; ゴースト
	db 21, GASTLY           ; ゴース
	db 22, GASTLY           ; ゴース
	db 19, GASTLY           ; ゴース
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	; day
	db 20, GASTLY           ; ゴース
	db 20, HAUNTER          ; ゴースト
	db 21, GASTLY           ; ゴース
	db 22, GASTLY           ; ゴース
	db 19, GASTLY           ; ゴース
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	; nite
	db 20, GASTLY           ; ゴース
	db 20, HAUNTER          ; ゴースト
	db 21, GASTLY           ; ゴース
	db 22, GASTLY           ; ゴース
	db 19, GASTLY           ; ゴース
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	end_grass_wildmons

	def_grass_wildmons POKEMON_TOWER_5F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 22, GASTLY           ; ゴース
	db 20, CUBONE           ; カラカラ
	db 22, HAUNTER          ; ゴースト
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	db 21, GASTLY           ; ゴース
	db 25, GASTLY           ; ゴース
	; day
	db 22, GASTLY           ; ゴース
	db 20, CUBONE           ; カラカラ
	db 22, HAUNTER          ; ゴースト
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	db 21, GASTLY           ; ゴース
	db 25, GASTLY           ; ゴース
	; nite
	db 22, GASTLY           ; ゴース
	db 20, CUBONE           ; カラカラ
	db 22, HAUNTER          ; ゴースト
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	db 21, GASTLY           ; ゴース
	db 25, GASTLY           ; ゴース
	end_grass_wildmons

	def_grass_wildmons POKEMON_TOWER_6F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 22, GASTLY           ; ゴース
	db 22, CUBONE           ; カラカラ
	db 22, HAUNTER          ; ゴースト
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	db 21, GASTLY           ; ゴース
	db 25, GASTLY           ; ゴース
	; day
	db 22, GASTLY           ; ゴース
	db 22, CUBONE           ; カラカラ
	db 22, HAUNTER          ; ゴースト
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	db 21, GASTLY           ; ゴース
	db 25, GASTLY           ; ゴース
	; nite
	db 22, GASTLY           ; ゴース
	db 22, CUBONE           ; カラカラ
	db 22, HAUNTER          ; ゴースト
	db 23, GASTLY           ; ゴース
	db 24, GASTLY           ; ゴース
	db 21, GASTLY           ; ゴース
	db 25, GASTLY           ; ゴース
	end_grass_wildmons

	def_grass_wildmons POKEMON_TOWER_7F
	db 8 percent, 8 percent, 8 percent ; encounter rates: morn/day/nite
	; morn
	db 24, GASTLY           ; ゴース
	db 24, CUBONE           ; カラカラ
	db 24, HAUNTER          ; ゴースト
	db 25, GASTLY           ; ゴース
	db 26, GASTLY           ; ゴース
	db 23, GASTLY           ; ゴース
	db 27, GASTLY           ; ゴース
	; day
	db 24, GASTLY           ; ゴース
	db 24, CUBONE           ; カラカラ
	db 24, HAUNTER          ; ゴースト
	db 25, GASTLY           ; ゴース
	db 26, GASTLY           ; ゴース
	db 23, GASTLY           ; ゴース
	db 27, GASTLY           ; ゴース
	; nite
	db 24, GASTLY           ; ゴース
	db 24, CUBONE           ; カラカラ
	db 24, HAUNTER          ; ゴースト
	db 25, GASTLY           ; ゴース
	db 26, GASTLY           ; ゴース
	db 23, GASTLY           ; ゴース
	db 27, GASTLY           ; ゴース
	end_grass_wildmons

	def_grass_wildmons SEAFOAM_ISLANDS_B1F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 27, ZUBAT            ; ズバット
	db 26, KRABBY           ; クラブ
	db 27, GOLBAT           ; ゴルバット
	db 29, SLOWPOKE         ; ヤドン
	db 28, KINGLER          ; キングラー
	db 22, SEEL             ; パウワウ
	db 36, ZUBAT            ; ズバット
	; day
	db 27, ZUBAT            ; ズバット
	db 26, KRABBY           ; クラブ
	db 27, GOLBAT           ; ゴルバット
	db 29, SLOWPOKE         ; ヤドン
	db 28, KINGLER          ; キングラー
	db 22, SEEL             ; パウワウ
	db 36, ZUBAT            ; ズバット
	; nite
	db 27, ZUBAT            ; ズバット
	db 26, KRABBY           ; クラブ
	db 27, GOLBAT           ; ゴルバット
	db 29, SLOWPOKE         ; ヤドン
	db 28, KINGLER          ; キングラー
	db 22, SEEL             ; パウワウ
	db 36, ZUBAT            ; ズバット
	end_grass_wildmons

	def_grass_wildmons SEAFOAM_ISLANDS_B2F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 27, ZUBAT            ; ズバット
	db 27, KRABBY           ; クラブ
	db 27, GOLBAT           ; ゴルバット
	db 28, KINGLER          ; キングラー
	db 24, SEEL             ; パウワウ
	db 31, SLOWPOKE         ; ヤドン
	db 37, JYNX             ; ルージュラ
	; day
	db 27, ZUBAT            ; ズバット
	db 27, KRABBY           ; クラブ
	db 27, GOLBAT           ; ゴルバット
	db 28, KINGLER          ; キングラー
	db 24, SEEL             ; パウワウ
	db 31, SLOWPOKE         ; ヤドン
	db 37, JYNX             ; ルージュラ
	; nite
	db 27, ZUBAT            ; ズバット
	db 27, KRABBY           ; クラブ
	db 27, GOLBAT           ; ゴルバット
	db 28, KINGLER          ; キングラー
	db 24, SEEL             ; パウワウ
	db 31, SLOWPOKE         ; ヤドン
	db 37, JYNX             ; ルージュラ
	end_grass_wildmons

	def_grass_wildmons SEAFOAM_ISLANDS_B3F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 36, ZUBAT            ; ズバット
	db 27, GOLBAT           ; ゴルバット
	db 29, KRABBY           ; クラブ
	db 26, SEEL             ; パウワウ
	db 30, KINGLER          ; キングラー
	db 28, DEWGONG          ; ジュゴン
	db 30, SEEL             ; パウワウ
	; day
	db 36, ZUBAT            ; ズバット
	db 27, GOLBAT           ; ゴルバット
	db 29, KRABBY           ; クラブ
	db 26, SEEL             ; パウワウ
	db 30, KINGLER          ; キングラー
	db 28, DEWGONG          ; ジュゴン
	db 30, SEEL             ; パウワウ
	; nite
	db 36, ZUBAT            ; ズバット
	db 27, GOLBAT           ; ゴルバット
	db 29, KRABBY           ; クラブ
	db 26, SEEL             ; パウワウ
	db 30, KINGLER          ; キングラー
	db 28, DEWGONG          ; ジュゴン
	db 30, SEEL             ; パウワウ
	end_grass_wildmons

	def_grass_wildmons SEAFOAM_ISLANDS_B4F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 36, GOLBAT           ; ゴルバット
	db 36, ZUBAT            ; ズバット
	db 28, SEEL             ; パウワウ
	db 30, KRABBY           ; クラブ
	db 32, KINGLER          ; キングラー
	db 39, JYNX             ; ルージュラ
	db 34, DEWGONG          ; ジュゴン
	; day
	db 36, GOLBAT           ; ゴルバット
	db 36, ZUBAT            ; ズバット
	db 28, SEEL             ; パウワウ
	db 30, KRABBY           ; クラブ
	db 32, KINGLER          ; キングラー
	db 39, JYNX             ; ルージュラ
	db 34, DEWGONG          ; ジュゴン
	; nite
	db 36, GOLBAT           ; ゴルバット
	db 36, ZUBAT            ; ズバット
	db 28, SEEL             ; パウワウ
	db 30, KRABBY           ; クラブ
	db 32, KINGLER          ; キングラー
	db 39, JYNX             ; ルージュラ
	db 34, DEWGONG          ; ジュゴン
	end_grass_wildmons

	def_grass_wildmons POKEMON_MANSION_1F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 30, KOFFING          ; ドガース
	db 23, GRIMER           ; ベトベター
	db 26, GROWLITHE        ; ガーディ
	db 34, VULPIX           ; ロコン
	db 37, RATICATE         ; ラッタ
	db 37, WEEZING          ; マタドガス
	db 32, KOFFING          ; ドガース
	; day
	db 30, KOFFING          ; ドガース
	db 23, GRIMER           ; ベトベター
	db 26, GROWLITHE        ; ガーディ
	db 34, VULPIX           ; ロコン
	db 37, RATICATE         ; ラッタ
	db 37, WEEZING          ; マタドガス
	db 32, KOFFING          ; ドガース
	; nite
	db 30, KOFFING          ; ドガース
	db 23, GRIMER           ; ベトベター
	db 26, GROWLITHE        ; ガーディ
	db 34, VULPIX           ; ロコン
	db 37, RATICATE         ; ラッタ
	db 37, WEEZING          ; マタドガス
	db 32, KOFFING          ; ドガース
	end_grass_wildmons

	def_grass_wildmons SEAFOAM_ISLANDS_1F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 18, ZUBAT            ; ズバット
	db 25, KRABBY           ; クラブ
	db 28, SLOWPOKE         ; ヤドン
	db 27, GOLBAT           ; ゴルバット
	db 27, ZUBAT            ; ズバット
	db 36, ZUBAT            ; ズバット
	db 9, ZUBAT             ; ズバット
	; day
	db 18, ZUBAT            ; ズバット
	db 25, KRABBY           ; クラブ
	db 28, SLOWPOKE         ; ヤドン
	db 27, GOLBAT           ; ゴルバット
	db 27, ZUBAT            ; ズバット
	db 36, ZUBAT            ; ズバット
	db 9, ZUBAT             ; ズバット
	; nite
	db 18, ZUBAT            ; ズバット
	db 25, KRABBY           ; クラブ
	db 28, SLOWPOKE         ; ヤドン
	db 27, GOLBAT           ; ゴルバット
	db 27, ZUBAT            ; ズバット
	db 36, ZUBAT            ; ズバット
	db 9, ZUBAT             ; ズバット
	end_grass_wildmons

	def_grass_wildmons VICTORY_ROAD_2F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 31, GEODUDE          ; イシツブテ
	db 44, ZUBAT            ; ズバット
	db 39, GOLBAT           ; ゴルバット
	db 44, GRAVELER         ; ゴローン
	db 45, ONIX             ; イワーク
	db 39, MACHOKE          ; ゴーリキー
	db 36, GEODUDE          ; イシツブテ
	; day
	db 31, GEODUDE          ; イシツブテ
	db 44, ZUBAT            ; ズバット
	db 39, GOLBAT           ; ゴルバット
	db 44, GRAVELER         ; ゴローン
	db 45, ONIX             ; イワーク
	db 39, MACHOKE          ; ゴーリキー
	db 36, GEODUDE          ; イシツブテ
	; nite
	db 31, GEODUDE          ; イシツブテ
	db 44, ZUBAT            ; ズバット
	db 39, GOLBAT           ; ゴルバット
	db 44, GRAVELER         ; ゴローン
	db 45, ONIX             ; イワーク
	db 39, MACHOKE          ; ゴーリキー
	db 36, GEODUDE          ; イシツブテ
	end_grass_wildmons

	def_grass_wildmons DIGLETTS_CAVE
	db 8 percent, 8 percent, 8 percent ; encounter rates: morn/day/nite
	; morn
	db 18, DIGLETT          ; ディグダ
	db 29, DUGTRIO          ; ダグトリオ
	db 19, DIGLETT          ; ディグダ
	db 17, DIGLETT          ; ディグダ
	db 15, DIGLETT          ; ディグダ
	db 16, DIGLETT          ; ディグダ
	db 20, DIGLETT          ; ディグダ
	; day
	db 18, DIGLETT          ; ディグダ
	db 29, DUGTRIO          ; ダグトリオ
	db 19, DIGLETT          ; ディグダ
	db 17, DIGLETT          ; ディグダ
	db 15, DIGLETT          ; ディグダ
	db 16, DIGLETT          ; ディグダ
	db 20, DIGLETT          ; ディグダ
	; nite
	db 18, DIGLETT          ; ディグダ
	db 29, DUGTRIO          ; ダグトリオ
	db 19, DIGLETT          ; ディグダ
	db 17, DIGLETT          ; ディグダ
	db 15, DIGLETT          ; ディグダ
	db 16, DIGLETT          ; ディグダ
	db 20, DIGLETT          ; ディグダ
	end_grass_wildmons

	def_grass_wildmons VICTORY_ROAD_3F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 36, GEODUDE          ; イシツブテ
	db 44, GOLBAT           ; ゴルバット
	db 41, GRAVELER         ; ゴローン
	db 49, ONIX             ; イワーク
	db 42, MACHOKE          ; ゴーリキー
	db 41, GEODUDE          ; イシツブテ
	db 46, GEODUDE          ; イシツブテ
	; day
	db 36, GEODUDE          ; イシツブテ
	db 44, GOLBAT           ; ゴルバット
	db 41, GRAVELER         ; ゴローン
	db 49, ONIX             ; イワーク
	db 42, MACHOKE          ; ゴーリキー
	db 41, GEODUDE          ; イシツブテ
	db 46, GEODUDE          ; イシツブテ
	; nite
	db 36, GEODUDE          ; イシツブテ
	db 44, GOLBAT           ; ゴルバット
	db 41, GRAVELER         ; ゴローン
	db 49, ONIX             ; イワーク
	db 42, MACHOKE          ; ゴーリキー
	db 41, GEODUDE          ; イシツブテ
	db 46, GEODUDE          ; イシツブテ
	end_grass_wildmons

	def_grass_wildmons POKEMON_MANSION_2F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 34, KOFFING          ; ドガース
	db 32, VULPIX           ; ロコン
	db 29, GRIMER           ; ベトベター
	db 40, RATICATE         ; ラッタ
	db 39, WEEZING          ; マタドガス
	db 38, MUK              ; ベトベトン
	db 30, KOFFING          ; ドガース
	; day
	db 34, KOFFING          ; ドガース
	db 32, VULPIX           ; ロコン
	db 29, GRIMER           ; ベトベター
	db 40, RATICATE         ; ラッタ
	db 39, WEEZING          ; マタドガス
	db 38, MUK              ; ベトベトン
	db 30, KOFFING          ; ドガース
	; nite
	db 34, KOFFING          ; ドガース
	db 32, VULPIX           ; ロコン
	db 29, GRIMER           ; ベトベター
	db 40, RATICATE         ; ラッタ
	db 39, WEEZING          ; マタドガス
	db 38, MUK              ; ベトベトン
	db 30, KOFFING          ; ドガース
	end_grass_wildmons

	def_grass_wildmons POKEMON_MANSION_3F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 35, KOFFING          ; ドガース
	db 33, VULPIX           ; ロコン
	db 40, WEEZING          ; マタドガス
	db 35, GRIMER           ; ベトベター
	db 34, MAGMAR           ; ブーバー
	db 38, MUK              ; ベトベトン
	db 34, KOFFING          ; ドガース
	; day
	db 35, KOFFING          ; ドガース
	db 33, VULPIX           ; ロコン
	db 40, WEEZING          ; マタドガス
	db 35, GRIMER           ; ベトベター
	db 34, MAGMAR           ; ブーバー
	db 38, MUK              ; ベトベトン
	db 34, KOFFING          ; ドガース
	; nite
	db 35, KOFFING          ; ドガース
	db 33, VULPIX           ; ロコン
	db 40, WEEZING          ; マタドガス
	db 35, GRIMER           ; ベトベター
	db 34, MAGMAR           ; ブーバー
	db 38, MUK              ; ベトベトン
	db 34, KOFFING          ; ドガース
	end_grass_wildmons

	def_grass_wildmons POKEMON_MANSION_B1F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 33, KOFFING          ; ドガース
	db 38, GRIMER           ; ベトベター
	db 35, VULPIX           ; ロコン
	db 40, WEEZING          ; マタドガス
	db 40, RATICATE         ; ラッタ
	db 41, MUK              ; ベトベトン
	db 24, DITTO            ; メタモン
	; day
	db 33, KOFFING          ; ドガース
	db 38, GRIMER           ; ベトベター
	db 35, VULPIX           ; ロコン
	db 40, WEEZING          ; マタドガス
	db 40, RATICATE         ; ラッタ
	db 41, MUK              ; ベトベトン
	db 38, MAGMAR           ; ブーバー
	; nite
	db 33, KOFFING          ; ドガース
	db 38, GRIMER           ; ベトベター
	db 35, VULPIX           ; ロコン
	db 40, WEEZING          ; マタドガス
	db 40, RATICATE         ; ラッタ
	db 41, MUK              ; ベトベトン
	db 24, DITTO            ; メタモン
	end_grass_wildmons

	def_grass_wildmons SAFARI_ZONE_EAST
	db 12 percent, 12 percent, 12 percent ; encounter rates: morn/day/nite
	; morn
	db 21, NIDORAN_M        ; ニドラン♂
	db 29, NIDORAN_F        ; ニドラン♀
	db 22, EXEGGCUTE        ; タマタマ
	db 21, TAUROS           ; ケンタロス
	db 32, NIDORINA         ; ニドリーナ
	db 19, CUBONE           ; カラカラ
	db 15, SCYTHER          ; ストライク
	; day
	db 21, NIDORAN_M        ; ニドラン♂
	db 29, NIDORAN_F        ; ニドラン♀
	db 22, EXEGGCUTE        ; タマタマ
	db 21, TAUROS           ; ケンタロス
	db 32, NIDORINA         ; ニドリーナ
	db 19, CUBONE           ; カラカラ
	db 24, MAROWAK          ; ガラガラ
	; nite
	db 21, NIDORAN_M        ; ニドラン♂
	db 29, NIDORAN_F        ; ニドラン♀
	db 22, EXEGGCUTE        ; タマタマ
	db 21, TAUROS           ; ケンタロス
	db 32, NIDORINA         ; ニドリーナ
	db 19, CUBONE           ; カラカラ
	db 21, CHANSEY          ; ラッキー
	end_grass_wildmons

	def_grass_wildmons SAFARI_ZONE_NORTH
	db 12 percent, 12 percent, 12 percent ; encounter rates: morn/day/nite
	; morn
	db 36, NIDORAN_M        ; ニドラン♂
	db 14, NIDORAN_F        ; ニドラン♀
	db 20, EXEGGCUTE        ; タマタマ
	db 28, KANGASKHAN       ; ガルーラ
	db 25, RHYHORN          ; サイホーン
	db 23, NIDORINA         ; ニドリーナ
	db 15, PINSIR           ; カイロス
	; day
	db 36, NIDORAN_M        ; ニドラン♂
	db 14, NIDORAN_F        ; ニドラン♀
	db 20, EXEGGCUTE        ; タマタマ
	db 28, KANGASKHAN       ; ガルーラ
	db 25, RHYHORN          ; サイホーン
	db 23, NIDORINA         ; ニドリーナ
	db 16, CUBONE           ; カラカラ
	; nite
	db 36, NIDORAN_M        ; ニドラン♂
	db 14, NIDORAN_F        ; ニドラン♀
	db 20, EXEGGCUTE        ; タマタマ
	db 28, KANGASKHAN       ; ガルーラ
	db 25, RHYHORN          ; サイホーン
	db 23, NIDORINA         ; ニドリーナ
	db 25, SCYTHER          ; ストライク
	end_grass_wildmons

	def_grass_wildmons SAFARI_ZONE_WEST
	db 12 percent, 12 percent, 12 percent ; encounter rates: morn/day/nite
	; morn
	db 29, NIDORAN_M        ; ニドラン♂
	db 21, NIDORAN_F        ; ニドラン♀
	db 22, EXEGGCUTE        ; タマタマ
	db 21, TAUROS           ; ケンタロス
	db 32, NIDORINO         ; ニドリーノ
	db 19, CUBONE           ; カラカラ
	db 27, TANGELA          ; モンジャラ
	; day
	db 29, NIDORAN_M        ; ニドラン♂
	db 21, NIDORAN_F        ; ニドラン♀
	db 22, EXEGGCUTE        ; タマタマ
	db 21, TAUROS           ; ケンタロス
	db 32, NIDORINO         ; ニドリーノ
	db 19, CUBONE           ; カラカラ
	db 24, MAROWAK          ; ガラガラ
	; nite
	db 29, NIDORAN_M        ; ニドラン♂
	db 21, NIDORAN_F        ; ニドラン♀
	db 22, EXEGGCUTE        ; タマタマ
	db 21, TAUROS           ; ケンタロス
	db 32, NIDORINO         ; ニドリーノ
	db 19, CUBONE           ; カラカラ
	db 25, PINSIR           ; カイロス
	end_grass_wildmons

	def_grass_wildmons SAFARI_ZONE_CENTER
	db 12 percent, 12 percent, 12 percent ; encounter rates: morn/day/nite
	; morn
	db 14, NIDORAN_M        ; ニドラン♂
	db 36, NIDORAN_F        ; ニドラン♀
	db 24, EXEGGCUTE        ; タマタマ
	db 27, PARASECT         ; パラセクト
	db 20, RHYHORN          ; サイホーン
	db 23, NIDORINO         ; ニドリーノ
	db 7, CHANSEY           ; ラッキー
	; day
	db 14, NIDORAN_M        ; ニドラン♂
	db 36, NIDORAN_F        ; ニドラン♀
	db 24, EXEGGCUTE        ; タマタマ
	db 27, PARASECT         ; パラセクト
	db 20, RHYHORN          ; サイホーン
	db 23, NIDORINO         ; ニドリーノ
	db 27, PARAS            ; パラス
	; nite
	db 14, NIDORAN_M        ; ニドラン♂
	db 36, NIDORAN_F        ; ニドラン♀
	db 24, EXEGGCUTE        ; タマタマ
	db 27, PARASECT         ; パラセクト
	db 20, RHYHORN          ; サイホーン
	db 23, NIDORINO         ; ニドリーノ
	db 22, TANGELA          ; モンジャラ
	end_grass_wildmons

	def_grass_wildmons CERULEAN_CAVE_2F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 52, GOLBAT           ; ゴルバット
	db 50, GRAVELER         ; ゴローン
	db 56, SANDSLASH        ; サンドパン
	db 50, RHYHORN          ; サイホーン
	db 60, DITTO            ; メタモン
	db 58, GLOOM            ; クサイハナ
	db 58, WEEPINBELL       ; ウツドン
	; day
	db 52, GOLBAT           ; ゴルバット
	db 50, GRAVELER         ; ゴローン
	db 56, SANDSLASH        ; サンドパン
	db 50, RHYHORN          ; サイホーン
	db 60, DITTO            ; メタモン
	db 58, GLOOM            ; クサイハナ
	db 60, RHYDON           ; サイドン
	; nite
	db 52, GOLBAT           ; ゴルバット
	db 50, GRAVELER         ; ゴローン
	db 56, SANDSLASH        ; サンドパン
	db 50, RHYHORN          ; サイホーン
	db 60, DITTO            ; メタモン
	db 58, GLOOM            ; クサイハナ
	db 58, WEEPINBELL       ; ウツドン
	end_grass_wildmons

	def_grass_wildmons CERULEAN_CAVE_B1F
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 54, GOLBAT           ; ゴルバット
	db 55, GRAVELER         ; ゴローン
	db 52, RHYHORN          ; サイホーン
	db 62, RHYDON           ; サイドン
	db 64, RAICHU           ; ライチュウ
	db 57, ARBOK            ; アーボック
	db 65, DITTO            ; メタモン
	; day
	db 54, GOLBAT           ; ゴルバット
	db 55, GRAVELER         ; ゴローン
	db 52, RHYHORN          ; サイホーン
	db 62, RHYDON           ; サイドン
	db 64, RAICHU           ; ライチュウ
	db 57, ARBOK            ; アーボック
	db 55, LICKITUNG        ; ベロリンガ
	; nite
	db 54, GOLBAT           ; ゴルバット
	db 55, GRAVELER         ; ゴローン
	db 52, RHYHORN          ; サイホーン
	db 62, RHYDON           ; サイドン
	db 64, RAICHU           ; ライチュウ
	db 57, ARBOK            ; アーボック
	db 65, DITTO            ; メタモン
	end_grass_wildmons

	def_grass_wildmons CERULEAN_CAVE_1F
	db 4 percent, 4 percent, 4 percent ; encounter rates: morn/day/nite
	; morn
	db 50, GOLBAT           ; ゴルバット
	db 45, GRAVELER         ; ゴローン
	db 55, GLOOM            ; クサイハナ
	db 55, WEEPINBELL       ; ウツドン
	db 52, ARBOK            ; アーボック
	db 54, VENOMOTH         ; モルフォン
	db 53, RAICHU           ; ライチュウ
	; day
	db 50, GOLBAT           ; ゴルバット
	db 45, GRAVELER         ; ゴローン
	db 55, GLOOM            ; クサイハナ
	db 55, WEEPINBELL       ; ウツドン
	db 52, ARBOK            ; アーボック
	db 54, PARASECT         ; パラセクト
	db 54, VENOMOTH         ; モルフォン
	; nite
	db 50, GOLBAT           ; ゴルバット
	db 45, GRAVELER         ; ゴローン
	db 55, GLOOM            ; クサイハナ
	db 55, WEEPINBELL       ; ウツドン
	db 52, ARBOK            ; アーボック
	db 54, VENOMOTH         ; モルフォン
	db 55, DITTO            ; メタモン
	end_grass_wildmons

	def_grass_wildmons ROCK_TUNNEL_B1F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 20, ZUBAT            ; ズバット
	db 17, GEODUDE          ; イシツブテ
	db 18, MACHOP           ; ワンリキー
	db 14, ONIX             ; イワーク
	db 21, ZUBAT            ; ズバット
	db 22, ZUBAT            ; ズバット
	db 20, ZUBAT            ; ズバット
	; day
	db 20, ZUBAT            ; ズバット
	db 17, GEODUDE          ; イシツブテ
	db 18, MACHOP           ; ワンリキー
	db 14, ONIX             ; イワーク
	db 21, ZUBAT            ; ズバット
	db 22, ZUBAT            ; ズバット
	db 20, ZUBAT            ; ズバット
	; nite
	db 20, ZUBAT            ; ズバット
	db 17, GEODUDE          ; イシツブテ
	db 18, MACHOP           ; ワンリキー
	db 14, ONIX             ; イワーク
	db 21, ZUBAT            ; ズバット
	db 22, ZUBAT            ; ズバット
	db 20, ZUBAT            ; ズバット
	end_grass_wildmons

	db -1 ; end

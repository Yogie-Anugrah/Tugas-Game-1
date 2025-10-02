# script.rpy — Clair Obscur: Expedition 33 — Ashes of the Manor (VN Spinoff)
# Ren'Py 8.4.1 — HUD + Timed Menu + Countdown Bar + Asset Integration

# ==== CHARACTERS ====
define a  = Character("Alicia", what_prefix="“", what_suffix="”")
define v  = Character("Verso",  what_prefix="“", what_suffix="”")
define r  = Character("Renoir", what_prefix="“", what_suffix="”")
define al = Character("Aline",  what_prefix="“", what_suffix="”")
define n  = Character(None)

# ==== IMAGE DEFINITIONS ====
# Backgrounds
image bg grandhall normal      = "images/Scene/bg_grandHall_Normal.png"
image bg grandhall burn        = "images/Scene/bg_grandHall_Burn.png"
image bg grandhall afterburn   = "images/Scene/bg_grandHall_After_Burn.png"
image bg grandhall             = "images/Scene/bg_grandHall.png"
image bg galery                = "images/Scene/bg_galery.png"
image bg kitchen normal        = "images/Scene/bg_kitchen_normal.png"
image bg kitchen burn          = "images/Scene/bg_kitchen_burn.png"
image bg library               = "images/Scene/bg_library.jpg"
image bg boiler                = "images/Scene/bg_boiler-room.png"
image bg studio normal         = "images/Scene/bg_music_studio_normal.png"
image bg studio burn           = "images/Scene/bg_music_studio_burn.png"
image bg escape balcon         = "images/Scene/bg_escape-balcon.png"

# Sprites
image alicia       = "images/Chara/Alicia(2).png"
image alicia emo   = "images/Chara/Alicia-Dramatic.png"
image alicia true  = "images/Chara/Alicia-True_Ending.png"
image verso        = "images/Chara/Verso(2).png"
image verso fire   = "images/Chara/Verso-Fire.png"
image aline        = "images/Chara/Aliene.png"
image aline alt    = "images/Chara/Aline(2).png"
image renoir       = "images/Chara/Renoir(2).png"
image renoir alt   = "images/Chara/Renoir(2).png"

# ==== POSITIONS / TRANSFORMS ====
transform leftpos:
    xalign 0.15
    yalign 1.0
transform centerpos:
    xalign 0.50
    yalign 1.0
transform rightpos:
    xalign 0.85
    yalign 1.0

# ==== AUDIO CHANNELS ====
init python:
    # channel tambahan untuk ambience loop (jalan bareng BGM)
    renpy.music.register_channel("ambience", "sfx", True)

# ==== GLOBAL STATE ====
default Heat = 0
default VoiceHP = 3
default TRUST_VERSO = 0
default VENT_LOCK = False
default TANK_ON = False
default LETTER_READ = False
default COAT_USED = False
default loops_completed = 0

default visited_gallery = False
default visited_kitchen = False
default visited_library = False
default visited_boiler = False
default saw_studio = False

default saved_aline = False
default saved_renoir = False
default saved_staff = False

# ==== STYLE (HUD/TIMER) ====
style hud_frame:
    background "#0008"
    xpadding 10
    ypadding 10
    xalign 0.98
    yalign 0.04

style hud_text:
    size 20
    color "#fff"

# frame timer dipakai oleh timed_menu; posisi diatur di screen-nya
style timer_frame:
    background "#0008"
    xpadding 8
    ypadding 8

# ==== HUD ====
screen hud():
    zorder 100
    frame style "hud_frame":
        vbox:
            spacing 6
            hbox:
                spacing 18
                vbox:
                    text "HEAT [Heat]/100" style "hud_text"
                    bar value VariableValue("Heat", 100) xmaximum 360
                vbox:
                    text "VOICE [VoiceHP]/3" style "hud_text"
                    bar value VariableValue("VoiceHP", 3) xmaximum 360
                vbox:
                    text "TRUST [TRUST_VERSO]" style "hud_text"
                    bar value VariableValue("TRUST_VERSO", 2) xmaximum 360

# ==== (Opsional) Countdown overlay sederhana ====
screen choice_timer(seconds=10.0, timeout_label="timeout"):
    default remaining = seconds
    timer 0.1 repeat True action SetScreenVariable("remaining", max(0.0, remaining - 0.1))
    timer seconds action Jump(timeout_label)
    frame style "timer_frame":
        has vbox
        text "⏱  Time left: [int(remaining+0.5)]s" size 24
        bar value StaticValue(remaining, seconds) xmaximum 520

# ==== TIMED MENU (timer + choices jadi satu) ====
screen timed_menu(seconds=10.0, timeout_label="timeout", items=[], prompt_text=None):
    zorder 150
    modal True

    default remaining = seconds
    timer 0.1 repeat True action SetScreenVariable("remaining", max(0.0, remaining - 0.1))
    timer seconds action Jump(timeout_label)

    vbox:
        xalign 0.5
        yalign 0.75      # taruh di bawah agar aman dari HUD
        spacing 12

        if prompt_text:
            frame:
                padding (8, 8)
                text prompt_text size 24

        frame style "timer_frame":
            has vbox
            text "⏱  Time left: [int(remaining+0.5)]s" size 22
            bar value StaticValue(remaining, seconds) xmaximum 640

        vbox:
            spacing 8
            for caption, action in items:
                textbutton caption action action xminimum 900

# ==== HELPERS ====
label inc_heat(amount=0):
    $ Heat = max(0, min(100, Heat + amount))
    return
label dec_voice(amount=1):
    $ VoiceHP = max(0, VoiceHP - amount)
    return

# ==== GAME START ====
label start:
    show screen hud

    # Prolog
    scene bg grandhall burn
    with fade
    play music "audio/bgm/Prolog.mp3" fadein 1.5
    play ambience "audio/sfx/Prolog-sfx.wav" loop

    n "{b}In medias res—Koridor Timur, The Manor.{/b}"
    n "Sirene meraung. Asap memagut tenggorokan. Lampu gantung retak."
    show alicia at centerpos
    with dissolve
    a "Panas... bau terpupus. Verso—di mana kau?"
    $ Heat += 5

    # Timed menu prolog
    $ _menu_items = [
        ("Ke studio musik (mencari Verso)", Jump("scene_studio_first")),
        ("Ke dapur (ambil pemadam)", Jump("scene_kitchen_false_start")),
        ("Telepon Ayah (Renoir)", Jump("scene_call_renoir")),
    ]
    $ _prompt = "{i}Ke mana dulu?{/i}\nHeat: [Heat]  Voice: [VoiceHP]  Trust: [TRUST_VERSO]"
    call screen timed_menu(seconds=15.0, timeout_label="prolog_timeout", items=_menu_items, prompt_text=_prompt)

label prolog_timeout:
    n "{i}Kau terpaku beberapa detik terlalu lama... Api merambat dari arah galeri.{/i}"
    $ Heat += 8
    jump hub_1

# ==== PROLOG BRANCHES ====
label scene_studio_first:
    scene bg studio burn
    with dissolve
    play ambience "audio/sfx/Prolog-sfx-2.wav" loop
    show verso fire at rightpos
    n "Studio musik remang. Sebagian piano hangus, partitur terbuka bertajuk 'For Those Who Come After'."
    a "(Nada-nada ini selalu memanggilku...)"
    $ TRUST_VERSO += 1
    $ Heat += 3
    n "Dari balik dinding, dengung api—bukan dari dapur."
    jump hub_1

label scene_kitchen_false_start:
    scene bg kitchen burn
    with dissolve
    show alicia emo at leftpos
    n "Dapur. Api kompor membesar."
    a "Pe—ma—dam!"
    $ VoiceHP = max(0, VoiceHP - 1)
    $ Heat = max(0, Heat - 5)
    n "Api kompor padam."
    n "{i}Retakan seperti kanvas menjalari layar...{/i}"
    n "Dari arah galeri, jilatan api {b}menyala lagi{/b}—lebih parah."
    $ Heat += 10
    jump hub_1

label scene_call_renoir:
    scene bg library
    with dissolve
    show renoir at rightpos
    n "Sambungan telepon berderak. Statis menyayat telinga."
    r "Ali—ci— ... ja—ngan ... ve—nt ... ba—wah ..."
    a "(Vent bawah tanah... tutup?)"
    $ Heat += 3
    jump hub_1

# ==== HUB (MAP) ====
label hub_1:
    if Heat >= 60:
        jump setpiece_1

    scene bg grandhall burn
    with fade
    show alicia at centerpos
    n "{b}Grand Hall{/b}. Empat arah terbuka di tengah asap.\nHeat: [Heat]  Voice: [VoiceHP]  Trust: [TRUST_VERSO]"
    menu:
        "Pergi ke Galeri Aline":
            jump scene_gallery_loop1
        "Pergi ke Dapur / Valve Atap":
            jump scene_kitchen_valve
        "Pergi ke Perpustakaan":
            jump scene_library_loop2
        "Pergi ke Ruang Boiler":
            jump scene_boiler_loop3
        "Pergi ke Studio Musik (opsional)":
            jump scene_studio_optional
        "Lanjut (cari sumber api)":
            jump setpiece_1

# ==== LOOPS / MITIGATIONS ====
label scene_gallery_loop1:
    scene bg galery
    with dissolve
    play ambience "audio/sfx/Loop_Galeri_Level.flac" loop
    if not visited_gallery:
        show aline at leftpos
        n "{b}Galeri Aline{/b}. Pigmen retak, bingkai menghitam."
        al "Jika warna bisa menghidupkan kembali... apa salahnya, Ren?"
        show renoir at rightpos
        r  "Yang hidup tak boleh digantikan lukisan."
        a  "(Vent bawah tanah... harus kututup.)"
        menu:
            "Tutup intake udara bawah tanah (vent)":
                $ VENT_LOCK = True
                $ loops_completed += 1
                $ visited_gallery = True
                $ Heat = max(0, Heat - 10)
                a "(Maaf, Ibu.)"
            "Abaikan (berisiko)":
                $ visited_gallery = True
                $ Heat += 5
        stop ambience fadeout 1.0
        jump hub_1
    else:
        n "Galeri kembali diliputi asap tipis."
        stop ambience fadeout 1.0
        jump hub_1

label scene_kitchen_valve:
    scene bg kitchen normal
    with dissolve
    if not visited_kitchen:
        n "{b}Dapur{/b}. Valve suplai air atap terpasang rapuh."
        if LETTER_READ:
            n "Kunci teknik dari perpustakaan pas di lubang valve."
            menu:
                "Buka valve sekarang (aktifkan sprinkle atap)":
                    $ TANK_ON = True
                    $ visited_kitchen = True
                    $ Heat = max(0, Heat - 8)
                    n "Air mengalir. Tetesan rintik membasahi langit-langit."
                "Tunda":
                    $ visited_kitchen = True
                    $ Heat += 3
        else:
            menu:
                "Paksa putar valve (sulit)":
                    $ success = (TRUST_VERSO >= 1)
                    if success:
                        $ TANK_ON = True
                        $ visited_kitchen = True
                        $ Heat = max(0, Heat - 6)
                        n "Dengan tenaga putus asa, valve berputar. Air mengalir."
                    else:
                        n "Valve macet. Sepertinya butuh kunci teknik dari perpustakaan."
                        $ visited_kitchen = True
                        $ Heat += 4
                "Panggil staf (memaksa bicara)":
                    $ VoiceHP = max(0, VoiceHP - 1)
                    if VoiceHP >= 1:
                        n "Beberapa staf merespons, siap membantu jalur evakuasi."
                        $ saved_staff = True
                        $ Heat = max(0, Heat - 2)
                    else:
                        n "Suaramu habis. Tenggorokan perih."
                        $ Heat += 2
    else:
        n "Valve atap sudah kau cek."
    jump hub_1

label scene_library_loop2:
    play music "audio/bgm/Loop_Perpustakaan.mp3" fadein 1.0
    play ambience "audio/sfx/Loop_Perpustakaan_Level-sfx.ogg" loop
    scene bg library
    with dissolve
    if not visited_library:
        show renoir at rightpos
        n "{b}Perpustakaan{/b}. Di balik buku perdebatan seni, ada surat terselip."
        r "Jika kubiarkan kau tinggal, kanvas memakan waktumu. Jika kuminta pulang, kau membenciku."
        r "Aku akan tinggalkan lampu menyala—kalau kau pilih pulang."
        $ LETTER_READ = True
        $ loops_completed += 1
        $ visited_library = True
        n "Kau juga menemukan {i}kunci teknik{/i}."
    else:
        n "Rak buku berderit. Surat sudah kau baca."
    stop ambience fadeout 1.0
    play music "audio/bgm/Main_Music.mp3" fadein 1.0
    jump hub_1

label scene_boiler_loop3:
    play music "audio/bgm/Loop_Boiler_Room_Level.mp3" fadein 0.8
    play ambience "audio/sfx/Loop_Boiler_Room_Level.wav" loop
    scene bg boiler
    with dissolve
    if not visited_boiler:
        n "{b}Ruang Boiler{/b}. Panas berdesis. Di tangga, {i}jam saku Verso{/i} terjatuh."
        show verso fire at rightpos
        v "Kalau ada bahaya, aku duluan."
        show alicia at leftpos
        a "Janji pegang tanganku."
        $ loops_completed += 1
        $ visited_boiler = True
        menu:
            "Kurangi tekanan boiler":
                $ Heat = max(0, Heat - 8)
                n "Tekanan turun, dentum mereda."
            "Alihkan pasokan air ke sayap timur":
                $ TANK_ON = True
                $ Heat = max(0, Heat - 4)
                n "Katup beralih. Sayap timur akan lebih basah."
        menu:
            "Ambil mantel basah di jemuran (perlindungan)":
                $ COAT_USED = True
                n "Kau menyambar mantel—dingin dan berat oleh air."
            "Biarkan saja":
                pass
    else:
        n "Boiler mendesis lebih jinak."
    stop ambience fadeout 1.0
    play music "audio/bgm/Main_Music.mp3" fadein 0.8
    jump hub_1

label scene_studio_optional:
    scene bg studio normal
    with dissolve
    if not saw_studio:
        show verso at rightpos
        $ TRUST_VERSO += 1
        $ saw_studio = True
        n "Nada yang patah menyisakan janji."
    else:
        n "Keheningan menempel di tuts."
    if VENT_LOCK and TANK_ON:
        $ Heat = max(0, Heat - 2)
    jump hub_1

# ==== SET-PIECE 1 ====
label setpiece_1:
    scene bg grandhall burn
    with dissolve
    play sound "audio/sfx/Klimax-sfx.ogg"
    n "{b}Jebol dari arah Galeri.{/b} Api bukan dari dapur—{i}false start{/i} terbongkar."
    if VoiceHP > 0:
        menu:
            "Paksa panggil Ayah (mengorbankan suara)":
                $ VoiceHP = max(0, VoiceHP - 1)
                show renoir at rightpos
                n "Renoir muncul dari kepulan asap, membantu menggeser lemari."
                $ Heat = max(0, Heat - 5)
            "Tetap diam dan cari penyangga":
                if TRUST_VERSO >= 1:
                    n "Kau mengingat trik Verso menahan beban dengan patung."
                    $ Heat = max(0, Heat - 3)
                else:
                    n "Kau ragu—api merayap."
                    $ Heat += 3
    else:
        n "Tenggorokanmu perih. Hanya isyarat tangan yang tersisa."
        $ Heat += 2
    jump setpiece_2

# ==== SET-PIECE 2 ====
label setpiece_2:
    scene bg grandhall burn
    with dissolve
    play sound "audio/sfx/Klimax-sfx-2.wav"
    n "{b}Pilih dua prioritas penyelamatan.{/b}"
    $ picks = 0
    while picks < 2:
        menu:
            "Selamatkan Aline":
                if not saved_aline:
                    $ saved_aline = True
                    $ picks += 1
                    show aline at leftpos
                    n "Aline menutup lorong api dengan kain basah raksasa; pigmen menyobek."
                    $ Heat += 5
                    $ Heat = max(0, Heat - 10)
                else:
                    n "Aline sudah bersama kalian."
            "Selamatkan Renoir":
                if not saved_renoir:
                    $ saved_renoir = True
                    $ picks += 1
                    show renoir at rightpos
                    n "Renoir menarik lemari berat, membuka jalan alternatif."
                    $ Heat = max(0, Heat - 4)
                else:
                    n "Renoir sudah selamat."
            "Selamatkan Staf / siapkan balkon timur":
                if not saved_staff:
                    $ saved_staff = True
                    $ picks += 1
                    n "Para staf menyiapkan jalur ke balkon timur."
                    $ Heat = max(0, Heat - 2)
                else:
                    n "Jalur balkon sudah disiapkan."
    jump climax_stairs

# ==== KLIMAKS ====
label climax_stairs:
    scene bg grandhall burn
    with fade
    play sound "audio/sfx/Klimax-sfx-3.wav"
    n "{b}Tangga utama{/b}. Langit-langit runtuh, pilar terbakar. Jalan keluar menyempit."
    show verso fire at rightpos
    v "Aku tahan balok ini. Kau lari!"
    if COAT_USED:
        n "Mantel basah di tanganmu meneteskan air."
    if TRUST_VERSO >= 1:
        show alicia emo at leftpos
        a "Ver—so, jangan {i}(nafas berat){/i}..."
    else:
        a "(Aku harus memilih sekarang.)"

    # Timed menu pada klimaks
    $ _menu_items2 = [
        ("Panggil Ayah/Ibu, angkat bersama!", Jump("branch_good_check")),
        ("Aku yang tahan, kau lari! (paksa bicara)", [ SetVariable("VoiceHP", max(0, VoiceHP - 1)), Jump("branch_bad_check") ]),
        ("Tukar mantel—kau di depanku (percaya Verso)", Jump("branch_true_check")),
    ]
    $ _prompt2 = "{b}Pilih cepat!{/b} Jalan keluar menyempit."
    call screen timed_menu(seconds=8.0, timeout_label="branch_bad_check", items=_menu_items2, prompt_text=_prompt2)

# ==== BRANCH CHECKS ====
label branch_good_check:
    if (saved_renoir or saved_aline) and VENT_LOCK and TANK_ON:
        jump ending_good
    else:
        jump ending_bad

label branch_bad_check:
    if VoiceHP <= 0 or (not VENT_LOCK and not TANK_ON):
        jump ending_bad
    else:
        jump ending_bad

label branch_true_check:
    if loops_completed >= 3 and (VENT_LOCK or TANK_ON) and TRUST_VERSO >= 1 and COAT_USED:
        jump ending_true
    else:
        jump ending_bad

# ==== ENDINGS ====
label ending_good:
    stop ambience fadeout 1.0
    stop music fadeout 1.0
    scene bg escape balcon
    with fade
    play music "audio/bgm/Good_Ending.wav"
    n "{b}GOOD END — Hearth Unscorched{/b}"
    show alicia at leftpos
    show verso at rightpos
    n "Renoir dan—jika sempat—Aline, mengangkat balok bersama Verso. Jalur ke balkon timur terbuka; sprinkle atap mereda."
    n "Manor rapuh, namun {i}tidak{/i} habis."
    a "(Aku masih bisa berbisik...)"
    n "— Warna tak lagi memakan nyawa."
    hide screen hud
    return

label ending_bad:
    stop ambience fadeout 1.0
    stop music fadeout 1.0
    scene bg grandhall afterburn
    with fade
    play music "audio/bgm/Bad_Ending.mp3"
    n "{b}BAD END — Ashes Together{/b}"
    n "Tangga runtuh menutup jalan. Api melahap Grand Hall."
    n "Jam saku Verso jatuh—jarum berhenti."
    n "Dalam abu, tak ada lagi janji; hanya bingkai kosong."
    hide screen hud
    return

label ending_true:
    stop ambience fadeout 1.0
    stop music fadeout 1.0
    scene bg grandhall afterburn
    with fade
    play music "audio/bgm/Main_Music.mp3" fadein 1.0
    n "{b}TRUE END — For Those Who Come After{/b}"
    show alicia true at centerpos
    n "Verso menahan balok menyala. Mantel basah melindungi langkahmu. Ledakan kecil dari vent mengguncang."
    n "Rumah habis dilalap api. Verso tiada."
    a "(Aku menarik napas—tanpa suara. Namamu tinggal di sela jeda.)"
    show aline alt at leftpos
    show renoir alt at rightpos
    n "Aline menatap kosong; Renoir menggenggam jam retak."
    hide screen hud
    return

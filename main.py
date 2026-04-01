import flet as ft
import httpx
import json
import random
import time
from datetime import date

# ============================================================
#  CONFIGURAZIONE
# ============================================================
GITHUB_RAW_URL = "https://raw.githubusercontent.com/M1NCH14P0T3NZ4/chiara_app_data/refs/heads/main/frasi.json"
DATA_INIZIO_STORIA = date(2025, 4, 20) 
NOME_LEI = "Capretta"

BLU_SCURO    = "#0D47A1"
BLU_MEDIO    = "#1976D2"
GRIGIO_TESTO = "#263238"

def main(page: ft.Page):
    page.title = f"Per la mia {NOME_LEI} ❤️"
    page.window.width = 390
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0

    page.fonts = {"Dancing": "fonts/DancingScript-Regular.ttf"}
    
    # --- PLAYER AUDIO ---
    # Creiamo un controllo audio globale
    audio_player = ft.Audio(src="", autoplay=False)
    page.overlay.append(audio_player)

    state = {"dati": None}

    def wrap_sfondo(content):
        return ft.Stack([
            ft.Image(src="sfondo.jpg", fit="cover", width=1000, height=2000),
            ft.Container(expand=True, bgcolor=ft.Colors.with_opacity(0.55, ft.Colors.WHITE)),
            ft.Container(content=content, expand=True, padding=ft.Padding.symmetric(horizontal=18, vertical=0))
        ], expand=True)

    def load_data():
        try:
            resp = httpx.get(GITHUB_RAW_URL, timeout=8)
            if resp.status_code == 200:
                dati = resp.json()
                with open("frasi_backup.json", "w", encoding="utf-8") as f:
                    json.dump(dati, f, ensure_ascii=False)
                return dati
        except:
            try:
                with open("frasi_backup.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return None

    def giorni_insieme():
        return (date.today() - DATA_INIZIO_STORIA).days

    # ========================================================
    #  SCHERMATA: SPLASH (Migliorata)
    # ========================================================
    def mostra_splash():
        page.clean()
        # Effetto "Fade In" per il cuore
        contenuto_splash = ft.Column([
            ft.Stack([
                ft.Icon(ft.Icons.FAVORITE, color=BLU_MEDIO, size=130),
                ft.Container(
                    content=ft.Icon(ft.Icons.REMOVE_RED_EYE_ROUNDED, color=ft.Colors.WHITE, size=48),
                    alignment=ft.Alignment(0, -0.18),
                ),
            ]),
            ft.Text("ci sono sempre ❤️", size=34, font_family="Dancing", color=BLU_SCURO, text_align="center"),
        ], alignment="center", horizontal_alignment="center", spacing=18)

        container_splash = ft.Container(
            content=contenuto_splash,
            expand=True,
            bgcolor=ft.Colors.WHITE,
            alignment=ft.Alignment(0, 0),
            opacity=0, # Parte invisibile
            animate_opacity=1000 # Animazione di 1 secondo
        )

        page.add(container_splash)
        page.update()
        
        # Facciamo apparire il cuore dolcemente
        container_splash.opacity = 1
        page.update()
        
        state["dati"] = load_data()
        time.sleep(2.5) 
        mostra_home()

    # ========================================================
    #  SCHERMATA: HOME
    # ========================================================
    def mostra_home():
        page.clean()
        giorni = giorni_insieme()

        banner_giorni = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.FAVORITE, color=BLU_MEDIO, size=28),
                ft.Column([
                    ft.Text(f"{giorni} giorni", size=32, font_family="Dancing", color=BLU_SCURO, weight="bold"),
                    ft.Text("che siamo insieme 🐐", size=14, color=GRIGIO_TESTO, weight="w500"),
                ], spacing=0),
            ], alignment="center"),
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.WHITE),
            border_radius=22,
            padding=ft.Padding.symmetric(vertical=16, horizontal=24),
        )

        grid = ft.GridView(expand=True, runs_count=2, max_extent=170, child_aspect_ratio=1.0, spacing=14)

        if state["dati"]:
            for cat in state["dati"].get("categorie", []):
                if not cat.get("frammenti"): continue
                grid.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(cat["emoji"], size=40),
                            ft.Text(cat["titolo"], weight="bold", size=16, text_align="center", color=BLU_SCURO),
                        ], alignment="center", horizontal_alignment="center"),
                        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.WHITE),
                        border_radius=24,
                        on_click=lambda e, c=cat: mostra_dettaglio(c),
                    )
                )

        layout = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text(f"Ciao {NOME_LEI} ❤️", size=42, font_family="Dancing", color=BLU_SCURO, weight="bold"),
                    ft.Text("Come ti senti oggi?", size=18, color=GRIGIO_TESTO, weight="w600"),
                ], spacing=2),
                margin=ft.Margin.only(top=60, bottom=15),
            ),
            banner_giorni,
            ft.Container(height=15),
            ft.Container(content=grid, expand=True),
        ], expand=True)

        page.add(wrap_sfondo(layout))
        page.update()

    # ========================================================
    #  SCHERMATA: DETTAGLIO
    # ========================================================
    def mostra_dettaglio(categoria):
        page.clean()
        frammenti = categoria.get("frammenti", [])
        frase_obj = random.choice(frammenti) if frammenti else {"testo": "..."}
        
        # Controlliamo se esiste un audio per questa frase
        audio_url = frase_obj.get("audio", "")

        def play_audio(e):
            if audio_url:
                audio_player.src = audio_url
                page.update()
                audio_player.play()

        layout = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color=BLU_SCURO, on_click=lambda _: mostra_home()),
                    ft.Text(f"{categoria['emoji']}  {categoria['titolo']}", size=24, font_family="Dancing", color=BLU_SCURO, weight="bold"),
                ]),
                margin=ft.Margin.only(top=48, bottom=10),
            ),

            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.FORMAT_QUOTE, color=BLU_MEDIO, size=45),
                    ft.Text(
                        frase_obj["testo"],
                        size=28,
                        text_align="center",
                        font_family="Dancing" if categoria["id"] in ["poesie", "noi"] else "sans-serif",
                        color=GRIGIO_TESTO,
                    ),
                    # Tasto Audio: appare solo se audio_url non è vuoto
                    ft.IconButton(
                        icon=ft.Icons.MUSIC_NOTE_ROUNDED,
                        icon_color=BLU_MEDIO,
                        icon_size=30,
                        visible=True if audio_url else False,
                        on_click=play_audio,
                        tooltip="Ascolta la mia voce"
                    ) if audio_url else ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.PINK_100, size=25),
                ], alignment="center", horizontal_alignment="center", spacing=20),
                padding=ft.Padding.all(35),
                alignment=ft.Alignment(0, 0),
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.96, ft.Colors.WHITE),
                border_radius=35,
                margin=ft.Margin.symmetric(vertical=10),
            ),

            ft.Container(
                content=ft.ElevatedButton(
                    "Un altro pensiero ✨",
                    icon=ft.Icons.AUTO_AWESOME_ROUNDED,
                    on_click=lambda _: mostra_dettaglio(categoria),
                    style=ft.ButtonStyle(bgcolor=BLU_MEDIO, color=ft.Colors.WHITE, padding=15),
                ),
                padding=ft.Padding.only(bottom=35),
                alignment=ft.Alignment(0, 0),
            ),
        ], expand=True)

        page.add(wrap_sfondo(layout))
        page.update()

    mostra_splash()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")

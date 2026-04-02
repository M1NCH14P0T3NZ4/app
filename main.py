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
# Nota: ho messo 2022 per avere un conteggio giorni positivo e veritiero
DATA_INIZIO_STORIA = date(2022, 4, 20) 
NOME_LEI = "Capretta"

BLU_SCURO    = "#0D47A1"
BLU_MEDIO    = "#1976D2"
GRIGIO_TESTO = "#263238"

def main(page: ft.Page):
    page.title = "PortoSicuro"
    page.window.width = 390
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0

    # Font locale
    page.fonts = {"Dancing": "fonts/DancingScript-Regular.ttf"}
    
    state = {"dati": None}

    # Helper per lo sfondo fotografico
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

    # --- SCHERMATA: HOME ---
    def mostra_home():
        page.clean()
        giorni = (date.today() - DATA_INIZIO_STORIA).days

        banner = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.FAVORITE, color=BLU_MEDIO, size=28),
                ft.Column([
                    ft.Text(f"{giorni} giorni", size=32, font_family="Dancing", color=BLU_SCURO, weight="bold"),
                    ft.Text("che siamo insieme 🐐", size=14, color=GRIGIO_TESTO),
                ], spacing=0),
            ], alignment="center"),
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.WHITE),
            border_radius=22, padding=20,
        )

        grid = ft.GridView(expand=True, runs_count=2, max_extent=170, child_aspect_ratio=1.0, spacing=14)

        if state["dati"]:
            for cat in state["dati"].get("categorie", []):
                if not cat.get("frammenti"): continue
                grid.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(cat["emoji"], size=40),
                            ft.Text(cat["titolo"], weight="bold", size=16, color=BLU_SCURO),
                        ], alignment="center", horizontal_alignment="center"),
                        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.WHITE),
                        border_radius=24,
                        on_click=lambda e, c=cat: mostra_dettaglio(c),
                    )
                )

        layout = ft.Column([
            ft.Container(height=60),
            ft.Text(f"Ciao {NOME_LEI} ❤️", size=42, font_family="Dancing", color=BLU_SCURO),
            banner,
            ft.Container(height=10),
            grid
        ], expand=True)

        page.add(wrap_sfondo(layout))
        page.update()

    # --- SCHERMATA: DETTAGLIO ---
    def mostra_dettaglio(categoria):
        page.clean()
        frammenti = categoria.get("frammenti", [])
        frase_obj = random.choice(frammenti) if frammenti else {"testo": "..."}

        layout = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color=BLU_SCURO, on_click=lambda _: mostra_home()),
                    ft.Text(categoria["titolo"], size=24, font_family="Dancing", color=BLU_SCURO, weight="bold"),
                ]),
                margin=ft.Margin.only(top=48),
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.FORMAT_QUOTE, color=BLU_MEDIO, size=45),
                    ft.Text(frase_obj["testo"], size=28, text_align="center", color=GRIGIO_TESTO),
                    ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.PINK_100, size=25),
                ], alignment="center", horizontal_alignment="center", spacing=20),
                padding=35, expand=True, bgcolor=ft.Colors.with_opacity(0.96, ft.Colors.WHITE), border_radius=35,
                margin=ft.Margin.symmetric(vertical=10),
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    "Un altro ✨", 
                    on_click=lambda _: mostra_dettaglio(categoria),
                    style=ft.ButtonStyle(bgcolor=BLU_MEDIO, color=ft.Colors.WHITE, padding=15)
                ),
                padding=30, alignment=ft.Alignment(0, 0)
            )
        ], expand=True)

        page.add(wrap_sfondo(layout))
        page.update()

    # Caricamento iniziale rapido
    state["dati"] = load_data()
    mostra_home()

# Avvio con flet run (ft.app)
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")

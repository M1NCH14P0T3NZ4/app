import flet as ft
import httpx
import json
import random
import os
import base64
from datetime import date

# ============================================================
#  CONFIGURAZIONE
# ============================================================
GITHUB_RAW_URL = "https://raw.githubusercontent.com/M1NCH14P0T3NZ4/chiara_app_data/refs/heads/main/frasi.json"
DATA_INIZIO_STORIA = date(2025, 4, 20) 
NOME_LEI = "Capretta"

# Cartella locale per le foto
STORAGE_DIR = "ricordi_cache"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

BLU_SCURO    = "#0D47A1"
BLU_MEDIO    = "#1976D2"
GRIGIO_TESTO = "#263238"

# Pixel trasparente "di sicurezza" per inizializzare l'immagine senza errori
DUMMY_IMG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

def main(page: ft.Page):
    page.title = "PortoSicuro"
    page.window.width = 390
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.fonts = {"Dancing": "fonts/DancingScript-Regular.ttf"}
    
    state = {"dati": None}

    # --------------------------------------------------------
    #  LOGICA CACHE (Download una volta sola)
    # --------------------------------------------------------
    def sync_foto():
        if not state["dati"] or "galleria" not in state["dati"]:
            return
        
        for url in state["dati"]["galleria"]:
            filename = url.split("/")[-1]
            local_path = os.path.join(STORAGE_DIR, filename)
            
            if not os.path.exists(local_path):
                try:
                    resp = httpx.get(url, timeout=20)
                    if resp.status_code == 200:
                        with open(local_path, "wb") as f:
                            f.write(resp.content)
                        print(f"Scaricata con successo: {filename}")
                except Exception as e:
                    print(f"Errore download {filename}: {e}")

    # --------------------------------------------------------
    #  HELPERS GRAFICI
    # --------------------------------------------------------
    def wrap_sfondo(content):
        return ft.Stack([
            ft.Image(src="sfondo.jpg", fit="cover", width=1000, height=2000),
            ft.Container(expand=True, bgcolor=ft.Colors.with_opacity(0.55, ft.Colors.WHITE)),
            ft.Container(content=content, expand=True, padding=ft.Padding.symmetric(horizontal=18, vertical=0))
        ], expand=True)

    def load_data():
        try:
            resp = httpx.get(GITHUB_RAW_URL, timeout=10)
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

    # --- SCHERMATA: GALLERIA (FIXATA PER 0.82.2) ---
    def mostra_galleria():
        page.clean()
        
        galleria_scorrimento = ft.ListView(expand=True, spacing=30, padding=10)
        
        # Titolo della Galleria
        layout_galleria = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color=BLU_SCURO, on_click=lambda _: mostra_home()),
                    ft.Text("I Nostri Ricordi ✨", size=28, font_family="Dancing", color=BLU_SCURO, weight="bold"),
                ]),
                margin=ft.Margin.only(top=48, bottom=10),
                bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
                border_radius=20, padding=5
            ),
            galleria_scorrimento
        ], expand=True)

        page.add(wrap_sfondo(layout_galleria))
        page.update()

        # Leggiamo i file scaricati
        file_locali = [f for f in os.listdir(STORAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        file_locali.sort() # Ordine alfabetico

        if not file_locali:
            galleria_scorrimento.controls.append(
                ft.Container(
                    content=ft.Text("Sto preparando le foto...\nTorna qui tra un istante! ❤️", 
                                    text_align="center", color=GRIGIO_TESTO),
                    padding=50
                )
            )
            page.update()
        else:
            for nome_file in file_locali:
                percorso_completo = os.path.join(STORAGE_DIR, nome_file)
                
                try:
                    # Trasformiamo la foto locale in una stringa utilizzabile
                    with open(percorso_completo, "rb") as f:
                        b64_img = base64.b64encode(f.read()).decode("utf-8")
                    
                    # Usiamo il Data URI come 'src' per evitare validazioni fallite
                    data_uri = f"data:image/jpeg;base64,{b64_img}"
                    
                    galleria_scorrimento.controls.append(
                        ft.Container(
                            content=ft.Image(
                                src=data_uri, # Passiamo tutto qui!
                                fit="contain",
                                height=500,
                                border_radius=15
                            ),
                            bgcolor=ft.Colors.TRANSPARENT,
                            alignment=ft.Alignment(0, 0),
                            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK)),
                        )
                    )
                except:
                    continue
            page.update()

    # --- SCHERMATA: HOME ---
    def mostra_home():
        page.clean()
        giorni = (date.today() - DATA_INIZIO_STORIA).days

        banner_giorni = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.FAVORITE, color=BLU_MEDIO, size=28),
                ft.Column([
                    ft.Text(f"{giorni} giorni", size=32, font_family="Dancing", color=BLU_SCURO, weight="bold"),
                    ft.Text("che siamo insieme 🐐 (clicca ✨)", size=12, color=GRIGIO_TESTO, weight="w600"),
                ], spacing=0),
            ], alignment="center"),
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.WHITE),
            border_radius=22, padding=20,
            on_click=lambda _: mostra_galleria(),
        )

        grid = ft.GridView(expand=True, runs_count=2, max_extent=170, child_aspect_ratio=1.0, spacing=14, run_spacing=14)

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

        layout_home = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text(f"Ciao {NOME_LEI} ❤️", size=42, font_family="Dancing", color=BLU_SCURO, weight="bold"),
                    ft.Text("Come ti senti oggi?", size=18, color=GRIGIO_TESTO, weight="w600"),
                ], spacing=2),
                margin=ft.Margin.only(top=60, bottom=15),
            ),
            banner_giorni,
            ft.Container(height=15),
            grid
        ], expand=True)

        page.add(wrap_sfondo(layout_home))
        page.update()

    # --- SCHERMATA: DETTAGLIO ---
    def mostra_dettaglio(categoria):
        page.clean()
        frammenti = categoria.get("frammenti", [])
        frase_obj = random.choice(frammenti) if frammenti else {"testo": "..."}

        layout_dettaglio = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color=BLU_SCURO, on_click=lambda _: mostra_home()),
                    ft.Text(categoria["titolo"], size=24, font_family="Dancing", color=BLU_SCURO, weight="bold"),
                ]),
                margin=ft.Margin.only(top=48),
                bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
                border_radius=20, padding=5
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.FORMAT_QUOTE, color=BLU_MEDIO, size=45),
                    ft.Text(frase_obj["testo"], size=28, text_align="center", color=GRIGIO_TESTO, weight="w500"),
                    ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.PINK_100, size=25),
                ], alignment="center", horizontal_alignment="center", spacing=20),
                padding=35, expand=True, bgcolor=ft.Colors.with_opacity(0.96, ft.Colors.WHITE), border_radius=35,
                margin=ft.Margin.symmetric(vertical=10),
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    "Un altro pensiero ✨", 
                    on_click=lambda _: mostra_dettaglio(categoria),
                    style=ft.ButtonStyle(bgcolor=BLU_MEDIO, color=ft.Colors.WHITE, padding=15)
                ),
                padding=30, alignment=ft.Alignment(0, 0)
            )
        ], expand=True)

        page.add(wrap_sfondo(layout_dettaglio))
        page.update()

    # --- AVVIO APP ---
    state["dati"] = load_data()
    mostra_home()
    # Scarica le foto in background per la prossima volta che aprirà la galleria
    sync_foto()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")

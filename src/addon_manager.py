# src/addon_manager.py
import math
from io import BytesIO

import requests
from PIL import Image, ImageTk

OWM_WEATHER = "http://api.openweathermap.org/data/2.5/weather"
OWM_FORECAST = "http://api.openweathermap.org/data/2.5/forecast"
OWM_ICON = "http://openweathermap.org/img/wn/{code}@2x.png"


class AddOnManager:
    """
    Gère l’affichage des couches additionnelles (météo, etc.)
    """

    def __init__(self, canvas, screen_width, weather_config):
        """
        :param canvas: instance de tkinter.Canvas
        :param screen_width: largeur de la fenêtre (px)
        :param weather_config: dict avec "municipality" et "api_key"
        """
        self.canvas = canvas
        self.screen_width = screen_width
        self.municipality = weather_config.get("municipality", "")
        self.api_key = weather_config.get("api_key", "")
        self.lat = weather_config.get("lat", None)
        self.lon = weather_config.get("lon", None)

        # cache image pour éviter GC de Tkinter
        self._precip_icon = None

    def display_weather(self):
        """
        Affiche en haut à droite:
          - Température actuelle
          - Icône météo (toujours affichée)
          - % de précipitations uniquement si pop > 0
        """
        if not self.municipality or not self.api_key:
            return

        try:
            # --- Température ---
            params = {"q": self.municipality, "units": "metric", "appid": self.api_key}
            resp = requests.get(OWM_WEATHER, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            temp = math.floor(float(data["main"]["temp"]) + 0.5)
            temp_text = f"{temp:.0f}°C"

            # --- Prévisions ---
            p_fc = params.copy()
            p_fc["cnt"] = 1
            resp_fc = requests.get(OWM_FORECAST, params=p_fc, timeout=5)
            resp_fc.raise_for_status()
            fc = resp_fc.json()
            slot = (fc.get("list") or [{}])[0]

            pop = float(slot.get("pop", 0.0)) * 100.0  # %
            w0 = (slot.get("weather") or [{}])[0]
            icon_code = w0.get("icon", "01d")
            icon_url = OWM_ICON.format(code=icon_code)

            precip_text = f"{pop:.0f}%" if pop > 0 else None
            precip_icon_url = icon_url

        except Exception:
            temp_text = "--°C"
            precip_text = None
            precip_icon_url = OWM_ICON.format(code="01d")

        # --- Dessin ---
        x, y = self.screen_width - 10, 10
        self.canvas.delete("weather_block")

        # Température
        self.canvas.create_text(
            x, y,
            text=temp_text,
            font=("Helvetica", 32),
            anchor="ne",
            tags=("weather_block",),
        )

        # Icône météo (toujours affichée)
        if precip_icon_url:
            try:
                ic = requests.get(precip_icon_url, timeout=5)
                ic.raise_for_status()
                if ic.headers.get("Content-Type", "").startswith("image"):
                    img = Image.open(BytesIO(ic.content))
                    self._precip_icon = ImageTk.PhotoImage(img)
                    self.canvas.create_image(
                        x - 50, y + 30,
                        image=self._precip_icon,
                        anchor="n",
                        tags=("weather_block",),
                    )
            except Exception:
                pass

        # Texte des précipitations uniquement si pop > 0
        if precip_text:
            self.canvas.create_text(
                x - 50, y + 120,
                text=precip_text,
                font=("Helvetica", 16),
                anchor="n",
                tags=("weather_block",),
            )

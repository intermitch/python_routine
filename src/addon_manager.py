# src/addon_manager.py
import math
import time
import requests

class AddOnManager:
    """
    Gère l’affichage des couches additionnelles (météo, etc.)
    """
    def __init__(self, canvas, screen_width, weather_config):
        """
        :param canvas: instance de tkinter.Canvas
        :param screen_width: largeur de la fenêtre (en pixels)
        :param weather_config: dict issu du JSON de scénario
               doit contenir au minimum "municipality" et "api_key",
               et éventuellement "lat" et "lon" pour WeatherSource.
        """
        self.canvas = canvas
        self.screen_width = screen_width
        self.municipality   = weather_config.get("municipality", "")
        self.api_key        = weather_config.get("api_key", "")
        self.lat            = weather_config.get("lat", None)
        self.lon            = weather_config.get("lon", None)

    def display_weather(self):
        """
        Récupère la température et la probabilité de précipitation
        et les affiche en haut à droite du canvas.
        """
        if not self.municipality or not self.api_key:
            return

        try:
            # — TEMPÉRATURE via OpenWeatherMap
            params = {
                "q": self.municipality,
                "units": "metric",
                "appid": self.api_key
            }
            resp = requests.get(
                "http://api.openweathermap.org/data/2.5/weather",
                params=params, timeout=5
            )
            resp.raise_for_status()
            data = resp.json()
            temp = math.floor(data["main"]["temp"] + 0.5)
            temp_text = f"{self.municipality} : {temp:.0f}°C"

            # — PRÉCIPITATIONS via OpenWeatherMap forecast
            #    (ou remplacez le bloc ci‑dessous par un appel WeatherSource si vous préférez)
            params_fc = params.copy()
            params_fc["cnt"] = 1
            resp_fc = requests.get(
                "http://api.openweathermap.org/data/2.5/forecast",
                params=params_fc, timeout=5
            )
            resp_fc.raise_for_status()
            list0 = resp_fc.json()["list"][0]
            pop  = list0.get("pop", 0) * 100
            ptype = list0["weather"][0]["main"].lower()
            precip_text = f"{pop:.0f}% de {ptype}"

        except Exception:
            temp_text   = "Météo N/A"
            precip_text = ""

        # Affichage sur le canvas
        x, y = self.screen_width - 10, 10
        # Température
        self.canvas.create_text(
            x, y,
            text=temp_text,
            font=("Helvetica", 32),
            anchor="ne"
        )
        # Précipitations juste en dessous
        if precip_text:
            self.canvas.create_text(
                x, y + 36,
                text=precip_text,
                font=("Helvetica", 16),
                anchor="ne"
            )

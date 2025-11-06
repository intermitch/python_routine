# src/addon_manager.py
import math
import os
from pathlib import Path
import json
from datetime import datetime

import requests
from PIL import Image, ImageTk

# Dossier du script courant
BASE_DIR = Path(__file__).resolve().parent
ICON_MAP_PATH = BASE_DIR.parent / "images" / "addon" / "weather_icon_map.json"

with open(ICON_MAP_PATH, "r", encoding="utf-8") as f:
    ICON_MAP = json.load(f)

OWM_WEATHER = "http://api.openweathermap.org/data/2.5/weather"
OWM_FORECAST = "http://api.openweathermap.org/data/2.5/forecast"


class AddOnManager:
    """
    Gère l'affichage des couches additionnelles (météo, etc.)
    """

    def __init__(self, canvas, screen_width, weather_config):
        self.canvas = canvas
        self.screen_width = screen_width
        self.municipality = weather_config.get("municipality", "")
        self.api_key = weather_config.get("api_key", "")
        self.lat = weather_config.get("lat", None)
        self.lon = weather_config.get("lon", None)

        # cache images pour éviter GC de Tkinter
        self._weather_icons = []

    def _get_dominant_weather(self, forecast_list, start_idx, count=1):
        """
        Détermine les conditions météo dominantes sur plusieurs créneaux
        Priorise: neige > pluie > nuages > clair
        """
        has_snow = False
        has_rain = False
        has_clouds = False
        icon_code = "01d"
        max_pop = 0
        total_rain = 0
        total_snow = 0

        for i in range(start_idx, min(start_idx + count, len(forecast_list))):
            slot = forecast_list[i]
            pop = float(slot.get("pop", 0.0))
            max_pop = max(max_pop, pop)

            # Agréger pluie et neige
            rain = slot.get("rain", {})
            snow = slot.get("snow", {})
            rain_3h = rain.get("3h", 0)
            snow_3h = snow.get("3h", 0)
            total_rain += rain_3h
            total_snow += snow_3h

            # Analyser les conditions météo
            weather_list = slot.get("weather", [])
            for w in weather_list:
                weather_id = w.get("id", 800)
                icon = w.get("icon", "01d")

                # Neige (600-622)
                if 600 <= weather_id < 623 or snow_3h > 0:
                    has_snow = True
                    icon_code = icon
                # Pluie (200-531, 300-321, 500-531)
                elif (200 <= weather_id < 600 or rain_3h > 0) and not has_snow:
                    has_rain = True
                    icon_code = icon
                # Nuages (801-804)
                elif 801 <= weather_id <= 804 and not has_rain and not has_snow:
                    has_clouds = True
                    icon_code = icon
                # Clair (800)
                elif weather_id == 800 and not has_clouds and not has_rain and not has_snow:
                    icon_code = icon

        return icon_code, max_pop * 100.0, total_rain, total_snow

    def display_weather(self):
        """
        Affiche 4 cartes météo en haut à droite avec période, icône dominante,
        température, température ressentie et probabilité de précipitations agrégées
        """
        if not self.municipality or not self.api_key:
            return

        try:
            # --- Prévisions (récupérer plus de créneaux) ---
            params = {"q": self.municipality, "units": "metric", "appid": self.api_key}
            params["cnt"] = 16
            resp_fc = requests.get(OWM_FORECAST, params=params, timeout=5)
            resp_fc.raise_for_status()
            fc = resp_fc.json()
            forecast_list = fc.get("list", [])

            periods = []
            seen_periods = set()
            processed_indices = set()

            for idx, slot in enumerate(forecast_list):
                if len(periods) >= 4 or idx in processed_indices:
                    continue

                dt = slot.get("dt", 0)
                dt_obj = datetime.fromtimestamp(dt)
                hour = dt_obj.hour

                # Déterminer la période
                if 6 <= hour < 12:
                    period = "Matin"
                elif 12 <= hour < 18:
                    period = "Après-midi"
                elif 18 <= hour < 24:
                    period = "Soir"
                else:
                    period = "Nuit"

                # Éviter les doublons de période
                if period in seen_periods:
                    continue

                seen_periods.add(period)
                processed_indices.add(idx)

                # Calculer les données pour toute la période (jusqu'à 3 créneaux de 3h = 9h max)
                slots_in_period = 1
                next_idx = idx + 1
                while next_idx < len(forecast_list) and slots_in_period < 3:
                    next_dt = datetime.fromtimestamp(forecast_list[next_idx].get("dt", 0))
                    next_hour = next_dt.hour

                    # Vérifier si toujours dans la même période
                    if period == "Matin" and 6 <= next_hour < 12:
                        slots_in_period += 1
                        processed_indices.add(next_idx)
                    elif period == "Après-midi" and 12 <= next_hour < 18:
                        slots_in_period += 1
                        processed_indices.add(next_idx)
                    elif period == "Soir" and 18 <= next_hour < 24:
                        slots_in_period += 1
                        processed_indices.add(next_idx)
                    elif period == "Nuit" and (next_hour < 6 or next_hour >= 24):
                        slots_in_period += 1
                        processed_indices.add(next_idx)
                    else:
                        break
                    next_idx += 1

                # Température et ressentie du premier créneau
                temp = math.floor(float(slot["main"]["temp"]) + 0.5)
                feels_like = math.floor(float(slot["main"]["feels_like"]) + 0.5)

                # Conditions dominantes sur la période
                icon_code, pop, rain, snow = self._get_dominant_weather(forecast_list, idx, slots_in_period)

                periods.append({
                    "period": period,
                    "temp": temp,
                    "feels_like": feels_like,
                    "pop": pop,
                    "rain": rain,
                    "snow": snow,
                    "icon_code": icon_code
                })

        except Exception as e:
            print(f"Erreur météo: {e}")
            periods = []

        # --- Dessin ---
        self.canvas.delete("weather_block")
        self._weather_icons = []

        if not periods:
            return

        # Dimensions des cartes
        card_width = 100
        card_height = 140
        card_spacing = 10
        start_x = self.screen_width - (card_width * len(periods) + card_spacing * (len(periods) - 1)) - 10
        start_y = 10

        for i, data in enumerate(periods):
            x = start_x + i * (card_width + card_spacing)
            y = start_y

            # Fond de carte
            self.canvas.create_rectangle(
                x, y, x + card_width, y + card_height,
                fill="#3a4f5f",
                outline="",
                tags=("weather_block",)
            )

            # Période
            self.canvas.create_text(
                x + card_width // 2, y + 15,
                text=data["period"],
                font=("Helvetica", 12, "bold"),
                fill="white",
                anchor="n",
                tags=("weather_block",)
            )

            # Icône météo dominante
            icon_file = ICON_MAP.get(data["icon_code"], ICON_MAP.get("01d"))
            if icon_file:
                icon_path = os.path.join("images/addon/weather", icon_file)
                try:
                    img = Image.open(icon_path)
                    img = img.resize((50, 50), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self._weather_icons.append(photo)
                    self.canvas.create_image(
                        x + card_width // 2, y + 30,
                        image=photo,
                        anchor="n",
                        tags=("weather_block",)
                    )
                except Exception as e:
                    print(f"Erreur chargement icône {icon_path}: {e}")

            # Température
            self.canvas.create_text(
                x + card_width // 2, y + 85,
                text=f"{data['temp']:.0f}°",
                font=("Helvetica", 16, "bold"),
                fill="white",
                anchor="n",
                tags=("weather_block",)
            )

            # Température ressentie
            self.canvas.create_text(
                x + card_width // 2, y + 105,
                text=f"T. ress {data['feels_like']:+.0f}",
                font=("Helvetica", 9),
                fill="white",
                anchor="n",
                tags=("weather_block",)
            )

            # Probabilité de précipitations (afficher seulement si > 0)
            if data['pop'] > 0:
                self.canvas.create_text(
                    x + 10, y + 125,
                    text="☁",
                    font=("Helvetica", 10),
                    fill="white",
                    anchor="w",
                    tags=("weather_block",)
                )
                self.canvas.create_text(
                    x + 25, y + 125,
                    text=f"{data['pop']:.0f}%",
                    font=("Helvetica", 10),
                    fill="white",
                    anchor="w",
                    tags=("weather_block",)
                )
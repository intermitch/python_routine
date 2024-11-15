import os
import json
from pathlib import Path


# Charger les événements, le titre, l'heure de début et de fin depuis le fichier JSON
def load_data(file_path):
    # Chemin vers la racine du projet
    project_root = Path(__file__).resolve().parents[1]
    with open(file_path, "r", encoding="utf-8") as f:  # Utiliser l'encodage UTF-8
        data = json.load(f)
    # Ajouter le chemin complet pour chaque icône
    events_data = data.get("events", [])
    for event in events_data:
        event["icon_path"] = os.path.join(project_root, "images", event["icon"])
    # Ajouter le chemin complet pour chaque icône
    indicators_data = data.get("indicators", [])
    for indicator in indicators_data:
        indicator["icon_path"] = os.path.join(project_root, "images", indicator["icon"])
    # Extraire le titre, l'heure de début et de fin
    title = data.get("title", "Titre")
    start_hour = data.get("start_hour", "00:00")
    end_hour = data.get("end_hour", "23:59")
    return title, start_hour, end_hour, events_data, indicators_data

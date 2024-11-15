import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
import datetime
import argparse
import json
from pathlib import Path

#from libs import data

# Vérifier si un fichier d'événements a été fourni en argument
if len(sys.argv) < 2:
    print("Usage: python monFichier.py <events_file.json>")
    sys.exit(1)

# Configurer le parser
parser = argparse.ArgumentParser(description="Script pour gérer le mode plein écran.")
parser.add_argument(
    "filename",
    type=str,
    help="Nom du fichier à traiter."
)
parser.add_argument(
    "--nofullscreen",
    action="store_false",  # Si présent, la valeur sera False
    dest="fullscreen",  # La variable résultante sera `args.fullscreen`
    help="Désactiver le mode plein écran."
)
# Définir `fullscreen` comme activé par défaut
parser.set_defaults(fullscreen=True)
# Parser les arguments
args = parser.parse_args()

# Chemin du dossier du script
scenario_dir = os.path.join(os.path.dirname(__file__), "scenario")
events_file = os.path.join(scenario_dir, sys.argv[1] + ".json")


# Charger les événements, le titre, l'heure de début et de fin depuis le fichier JSON
def load_data(file_path):
    # Chemin vers la racine du projet
    project_root = Path(__file__).resolve().parents[0]
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

# Charger les données
title, start_hour, end_hour, events, indicators = load_data(events_file)

# Créer start_time et end_time avec la date actuelle
today = datetime.datetime.now().date()
start_time = datetime.datetime.combine(today, datetime.datetime.strptime(start_hour, "%H:%M").time())
end_time = datetime.datetime.combine(today, datetime.datetime.strptime(end_hour, "%H:%M").time())
total_minutes = int((end_time - start_time).total_seconds() / 60)

# Initialiser la fenêtre Tkinter en plein écran
root = tk.Tk()
root.title("Ligne du temps en plein écran")
if args.fullscreen:
    root.attributes("-fullscreen", True)

# Obtenir les dimensions de l'écran
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Dimensions de la ligne du temps
canvas_width = screen_width * 0.8
canvas_height = 100
canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="white")
canvas.pack()

# Calcul de position de la barre de progression au centre de l'écran
bar_y = screen_height // 2
bar_start_x = (screen_width - canvas_width) // 2
bar_end_x = bar_start_x + canvas_width

# Calculer l'échelle (pixels par minute)
pixels_per_minute = canvas_width / total_minutes

# Afficher le titre en haut, centré, avec une hauteur de 100 pixels
title_text = canvas.create_text(
    screen_width // 2, 50, text=title, font=("Helvetica", 48), anchor="center"
)

# Liste pour conserver les références des icônes des événements, leurs positions et leurs cadres rouges
event_icons = []
event_positions = []
event_frames = []

# Dessiner la ligne de temps principale
timeline_line = canvas.create_line(bar_start_x, bar_y, bar_end_x, bar_y, fill="black", width=5)
canvas.create_text(bar_start_x, bar_y + 20, text=start_hour, anchor="e")
canvas.create_text(bar_end_x, bar_y + 20, text=end_hour, anchor="w")

# Fonction pour ajouter un événement avec une icône et une heure sous l'icône
def add_event_icon(event_time_str, icon_path):
    event_time = datetime.datetime.combine(today, datetime.datetime.strptime(event_time_str, "%H:%M").time())

    if start_time <= event_time <= end_time:
        # Calculer la position x de l'événement sur la ligne de temps
        elapsed_minutes = (event_time - start_time).total_seconds() / 60
        x_position = bar_start_x + elapsed_minutes * pixels_per_minute

        # Charger l'icône de l'événement
        event_icon_image = Image.open(icon_path)
        event_icon_image = event_icon_image.resize((50, 50), Image.LANCZOS)
        event_icon = ImageTk.PhotoImage(event_icon_image)

        # Afficher l'icône de l'événement sur la ligne de temps
        icon_id = canvas.create_image(x_position, bar_y-80, image=event_icon, anchor="center")
        event_icons.append(event_icon)  # Pour éviter le garbage collection
        event_positions.append((x_position, event_time))

        # Afficher l'heure sous l'icône de l'événement
        if event_id%2 == 0:
            pos_y_mod = 0
        else:
            pos_y_mod = 20
        print(pos_y_mod)
        canvas.create_text(x_position, bar_y + 50-pos_y_mod, text=event_time_str, anchor="n")

# Ajouter chaque événement défini dans la liste `events`
event_id=1
for event in events:
    add_event_icon(event["time"], event["icon_path"])
    event_id+=1

# Charger l'icône en tant qu'indicateur de temps actuel

def add_indicator_icon(indicators):
    icon_image = Image.open(os.path.join(os.path.dirname(__file__), indicators[0]["icon_path"]))
    icon_image = icon_image.resize((80, 80), Image.LANCZOS)
    icon = ImageTk.PhotoImage(icon_image)
    # Attacher `icon` à l'objet canvas
    if not hasattr(canvas, "image_references"):
        canvas.image_references = []  # Créer une liste d'images si elle n'existe pas
    canvas.image_references.append(icon)
    return canvas.create_image(bar_start_x, bar_y, image=icon, anchor="center")

def update_indicator_icon(canvas_item, new_image_path):
    # Charger et redimensionner la nouvelle image
    icon_image = Image.open(new_image_path)
    icon_image = icon_image.resize((80, 80), Image.LANCZOS)
    new_icon = ImageTk.PhotoImage(icon_image)

    # Attacher la nouvelle image au canvas pour éviter le garbage collection
    if not hasattr(canvas, "image_references"):
        canvas.image_references = []
    canvas.image_references.append(new_icon)

    # Mettre à jour l'image du canvas_item
    canvas.itemconfig(canvas_item, image=new_icon)

#crée l'indicator de début
icon_indicator = add_indicator_icon(indicators)

# Afficher l'heure actuelle au centre en bas de l'écran
current_time_text = canvas.create_text(
    screen_width // 2, screen_height - 50, text="", font=("Helvetica", 48), anchor="center"
)

# Fonction pour mettre à jour la position de l'indicateur de l'heure actuelle et gérer l'encadrement des événements
def update_indicator():
    now = datetime.datetime.now()
    now_time = datetime.datetime.combine(today, now.time())

    # Mettre à jour l'affichage de l'heure actuelle
    canvas.itemconfig(current_time_text, text=now.strftime("%H:%M:%S"))


    #Modification de l'indicateur
    resultats = [indicator for indicator in reversed(indicators) if
                 datetime.datetime.combine(today, datetime.datetime.strptime(indicator["time"], "%H:%M").time()) <= now_time]

    update_indicator_icon(icon_indicator, resultats[0]["icon_path"])

    if start_time <= now_time <= end_time:
        elapsed_minutes = (now_time - start_time).total_seconds() / 60
        x_position = bar_start_x + elapsed_minutes * pixels_per_minute
        canvas.coords(icon_indicator, x_position, bar_y)

        for i, (event_x, event_time) in enumerate(event_positions):
            time_difference = abs((now_time - event_time).total_seconds() / 60)
            if time_difference <= 2:
                if len(event_frames) <= i or not event_frames[i]:
                    frame = canvas.create_rectangle(
                        event_x - 30, bar_y - 30 - 80, event_x + 30, bar_y + 30 - 80, outline="red", width=2
                    )
                    if len(event_frames) > i:
                        event_frames[i] = frame
                    else:
                        event_frames.append(frame)
            else:
                if len(event_frames) > i and event_frames[i]:
                    canvas.delete(event_frames[i])
                    event_frames[i] = None


    root.after(1000, update_indicator)

# Bouton pour quitter le mode plein écran
def exit_fullscreen(event):
    root.attributes("-fullscreen", False)
    root.destroy()

# Associer la touche "Échap" pour quitter le plein écran
root.bind("<Escape>", exit_fullscreen)

# Démarrer la mise à jour de l'indicateur de l'heure actuelle
update_indicator()

# Lancer la boucle principale
root.mainloop()

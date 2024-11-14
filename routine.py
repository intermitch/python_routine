import os
import sys
import json
import tkinter as tk
from PIL import Image, ImageTk
import datetime

# Vérifier si un fichier d'événements a été fourni en argument
if len(sys.argv) < 2:
    print("Usage: python monFichier.py <events_file.json>")
    sys.exit(1)

# Chemin du dossier du script
script_dir = os.path.dirname(__file__)
scenario_dir = os.path.join(script_dir, "scenario")
events_file = os.path.join(scenario_dir, sys.argv[1] + ".json")

# Charger les événements, le titre, l'heure de début et de fin depuis le fichier JSON
def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:  # Utiliser l'encodage UTF-8
        data = json.load(f)
    # Ajouter le chemin complet pour chaque icône
    events_data = data.get("events", [])
    for event in events_data:
        event["icon_path"] = os.path.join(script_dir, "images", event["icon"])
    # Extraire le titre, l'heure de début et de fin
    title = data.get("title", "Titre")
    start_hour = data.get("start_hour", "00:00")
    end_hour = data.get("end_hour", "23:59")
    return title, start_hour, end_hour, events_data

# Charger les données
title, start_hour, end_hour, events = load_data(events_file)

# Créer start_time et end_time avec la date actuelle
today = datetime.datetime.now().date()
start_time = datetime.datetime.combine(today, datetime.datetime.strptime(start_hour, "%H:%M").time())
end_time = datetime.datetime.combine(today, datetime.datetime.strptime(end_hour, "%H:%M").time())
total_minutes = int((end_time - start_time).total_seconds() / 60)

# Initialiser la fenêtre Tkinter en plein écran
root = tk.Tk()
root.title("Ligne du temps en plein écran")
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
        canvas.create_text(x_position, bar_y + 50, text=event_time_str, anchor="n")

# Ajouter chaque événement défini dans la liste `events`
for event in events:
    add_event_icon(event["time"], event["icon_path"])

# Charger l'icône en tant qu'indicateur de temps actuel
icon_image = Image.open(os.path.join(script_dir, "./images/petite_fille.png"))
icon_image = icon_image.resize((80, 80), Image.LANCZOS)
icon = ImageTk.PhotoImage(icon_image)
icon_indicator = canvas.create_image(bar_start_x, bar_y, image=icon, anchor="center")

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
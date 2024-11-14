import os
import tkinter as tk
from PIL import Image, ImageTk
import datetime

# Variables pour le choix de l'heure de début et de l'heure de fin
start_hour =     "18:30"    #6:30
end_hour =       "20:00"    #8:00
# Définir les événements avec les heures et les icônes associées
events = [
    {"time": "18:50", "icon_path": os.path.join("images", "reveil.png")},           #6:50
    {"time": "19:00", "icon_path": os.path.join("images", "dejeuner.png")},         #7:00
    {"time": "19:15", "icon_path": os.path.join("images", "dent.png")},      #7:15
    {"time": "19:30", "icon_path": os.path.join("images", "mitaine.png")},          #7:30
    {"time": "19:40", "icon_path": os.path.join("images", "bus.webp")},             #7:40
]

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
canvas_width = screen_width * 0.8  # 80% de la largeur de l'écran
canvas_height = 100
canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="white")
canvas.pack()

# Calcul de position de la barre de progression au centre de l'écran
bar_y = screen_height // 2
bar_start_x = (screen_width - canvas_width) // 2
bar_end_x = bar_start_x + canvas_width

# Calculer l'échelle (pixels par minute)
pixels_per_minute = canvas_width / total_minutes


# Liste pour conserver les références des icônes des événements, leurs positions et leurs cadres rouges
event_icons = []
event_positions = []
event_frames = []

# Dessiner la ligne de temps principale (en dessous de tous les autres éléments)
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
        event_icon_image = event_icon_image.resize((100, 100), Image.LANCZOS)  # Redimensionner l'icône de l'événement
        event_icon = ImageTk.PhotoImage(event_icon_image)

        # Afficher l'icône de l'événement sur la ligne de temps
        icon_id = canvas.create_image(x_position, bar_y, image=event_icon, anchor="center")
        event_icons.append(event_icon)  # Ajouter l'icône dans la liste pour éviter le garbage collection
        event_positions.append((x_position, event_time))  # Ajouter la position et l'heure de l'événement

        # Afficher l'heure sous l'icône de l'événement
        canvas.create_text(x_position, bar_y + 50, text=event_time_str, anchor="n")


# Ajouter chaque événement défini dans la liste `events`
for event in events:
    add_event_icon(event["time"], event["icon_path"])

# Charger l'icône en tant qu'indicateur de temps actuel
icon_image = Image.open(os.path.join("images", "petite_fille.png"))
icon_image = icon_image.resize((80, 80), Image.LANCZOS)
icon = ImageTk.PhotoImage(icon_image)

# Ajouter l'icône au canvas pour l'indicateur de l'heure actuelle
icon_indicator = canvas.create_image(bar_start_x, bar_y, image=icon, anchor="center")


# Fonction pour mettre à jour la position de l'indicateur de l'heure actuelle et gérer l'encadrement des événements
def update_indicator():
    now = datetime.datetime.now()
    now_time = datetime.datetime.combine(today, now.time())

    if start_time <= now_time <= end_time:
        elapsed_minutes = (now_time - start_time).total_seconds() / 60
        x_position = bar_start_x + elapsed_minutes * pixels_per_minute
        canvas.coords(icon_indicator, x_position, bar_y)

        # Vérifier et mettre à jour les cadres rouges autour des événements
        for i, (event_x, event_time) in enumerate(event_positions):
            # Calculer l'écart en minutes entre l'heure actuelle et l'événement
            time_difference = abs((now_time - event_time).total_seconds() / 60)

            # Si l'heure actuelle est dans la fenêtre de 5 minutes avant ou après l'événement
            if time_difference <= 5:
                # Ajouter un cadre rouge autour de l'icône de l'événement si ce n'est pas déjà fait
                if len(event_frames) <= i or not event_frames[i]:
                    frame = canvas.create_rectangle(
                        event_x - 50, bar_y - 50, event_x + 50, bar_y + 50, outline="red", width=2
                    )
                    if len(event_frames) > i:
                        event_frames[i] = frame
                    else:
                        event_frames.append(frame)
            else:
                # Enlever le cadre rouge si l'événement n'est plus dans la fenêtre de 5 minutes
                if len(event_frames) > i and event_frames[i]:
                    canvas.delete(event_frames[i])
                    event_frames[i] = None

    # Planifier la prochaine mise à jour
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

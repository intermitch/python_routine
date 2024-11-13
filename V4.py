import os
import tkinter as tk
from PIL import Image, ImageTk
import datetime

# Variables pour le choix de l'heure de début et de l'heure de fin
start_hour = "14:00"
end_hour = "15:20"

# Créer start_time et end_time avec la date actuelle
today = datetime.datetime.now().date()
start_time = datetime.datetime.combine(today, datetime.datetime.strptime(start_hour, "%H:%M").time())
end_time = datetime.datetime.combine(today, datetime.datetime.strptime(end_hour, "%H:%M").time())
total_minutes = int((end_time - start_time).total_seconds() / 60)

# Initialiser la fenêtre Tkinter en plein écran
root = tk.Tk()
root.title("Ligne du temps en plein écran")
# root.attributes("-fullscreen", True)

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

# Dessiner la ligne du temps centrée
canvas.create_line(bar_start_x, bar_y, bar_end_x, bar_y, width=5)
canvas.create_text(bar_start_x, bar_y + 20, text=start_hour, anchor="e")
canvas.create_text(bar_end_x, bar_y + 20, text=end_hour, anchor="w")

# Calculer l'échelle (pixels par minute)
pixels_per_minute = canvas_width / total_minutes

# Charger l'icône en tant qu'indicateur de temps actuel
#icon_path = "C:\9000-PROJETS\PYTHON\python_routine\petite_fille.png"  # Chemin vers votre icône téléchargée
icon_image = Image.open(os.path.join("images", "petite_fille.png"))
icon_image = icon_image.resize((80, 80), Image.LANCZOS)
icon = ImageTk.PhotoImage(icon_image)

# Ajouter l'icône au canvas
icon_indicator = canvas.create_image(bar_start_x, bar_y, image=icon, anchor="center")

# Définir les événements avec les heures et les icônes associées
events = [
    {"time": "14:05", "icon_path": os.path.join("images", "dejeuner.png")},
    {"time": "14:50", "icon_path": os.path.join("images", "brosse_dent.png")},
    {"time": "15:00", "icon_path": os.path.join("images", "bus.webp")},
]


# Fonction pour ajouter un événement avec une icône sur la ligne de temps
def add_event_icon(event_time_str, icon_path):
    event_time = datetime.datetime.combine(today, datetime.datetime.strptime(event_time_str, "%H:%M").time())
    print(event_time)
    if start_time <= event_time <= end_time:
        # Calculer la position x de l'événement sur la ligne de temps
        elapsed_minutes = (event_time - start_time).total_seconds() / 60
        x_position = bar_start_x + elapsed_minutes * pixels_per_minute
        print(x_position)
        # Charger l'icône de l'événement
        event_icon_image = Image.open(icon_path)
        event_icon_image = event_icon_image.resize((100, 100), Image.LANCZOS)  # Redimensionner l'icône de l'événement
        event_icon = ImageTk.PhotoImage(event_icon_image)

        # Afficher l'icône de l'événement sur la ligne de temps
        canvas.create_image(x_position, bar_y, image=event_icon, anchor="center")

        # Conserver une référence pour éviter le garbage collection
        canvas.image = event_icon


# Ajouter chaque événement défini dans la liste `events`
for event in events:
    add_event_icon(event["time"], event["icon_path"])


# Fonction pour mettre à jour la position de l'indicateur de l'heure actuelle
def update_indicator():
    now = datetime.datetime.now()
    now_time = datetime.datetime.combine(today, now.time())

    if start_time <= now_time <= end_time:
        elapsed_minutes = (now_time - start_time).total_seconds() / 60
        x_position = bar_start_x + elapsed_minutes * pixels_per_minute
        print("indicateur >>> " + str(x_position))
        canvas.coords(icon_indicator, x_position, bar_y)

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

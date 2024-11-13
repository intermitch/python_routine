import tkinter as tk
from PIL import Image, ImageTk
import datetime

# Variables pour le choix de l'heure de début et de l'heure de fin
start_hour = "10:30"
end_hour = "11:30"

# Créer start_time et end_time avec la date actuelle
today = datetime.datetime.now().date()
start_time = datetime.datetime.combine(today, datetime.datetime.strptime(start_hour, "%H:%M").time())
end_time = datetime.datetime.combine(today, datetime.datetime.strptime(end_hour, "%H:%M").time())
total_minutes = int((end_time - start_time).total_seconds() / 60)

# Initialiser la fenêtre Tkinter en plein écran
root = tk.Tk()
root.title("Ligne du temps en plein écran")
#root.attributes("-fullscreen", True)

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

# Charger l'icône en tant qu'indicateur
icon_path = "C:\9000-PROJETS\PYTHON\python_routine\petite_fille.png"  # Chemin vers votre icône téléchargée
icon_image = Image.open(icon_path)
icon_image = icon_image.resize((30, 30), Image.LANCZOS)  # Redimensionner l'icône si nécessaire
icon = ImageTk.PhotoImage(icon_image)

# Ajouter l'icône au canvas
icon_indicator = canvas.create_image(bar_start_x, bar_y, image=icon, anchor="center")

# Fonction pour mettre à jour la position de l'indicateur
def update_indicator():
    now = datetime.datetime.now()
    now_time = datetime.datetime.combine(today, now.time())  # Assurer la même date pour now_time
    if start_time <= now_time <= end_time:
        elapsed_minutes = (now_time - start_time).total_seconds() / 60
        x_position = bar_start_x + elapsed_minutes * pixels_per_minute
        canvas.coords(icon_indicator, x_position, bar_y)  # Déplacer l'icône

    # Planifier la prochaine mise à jour
    root.after(1000, update_indicator)

# Bouton pour quitter le mode plein écran
def exit_fullscreen(event):
    root.attributes("-fullscreen", False)
    root.destroy()

# Associer la touche "Échap" pour quitter le plein écran
root.bind("<Escape>", exit_fullscreen)

# Démarrer la mise à jour de l'indicateur
update_indicator()

# Lancer la boucle principale
root.mainloop()

import tkinter as tk
import datetime

# Configuration de la ligne du temps
start_time = datetime.datetime.strptime("10:00", "%H:%M")
end_time = datetime.datetime.strptime("12:00", "%H:%M")
total_minutes = int((end_time - start_time).total_seconds() / 60)

# Initialiser la fenêtre Tkinter
root = tk.Tk()
root.title("Ligne du temps")

# Dimensions de la ligne du temps
canvas_width = 600
canvas_height = 100
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
canvas.pack()

# Dessiner la ligne du temps
canvas.create_line(50, 50, canvas_width - 50, 50, width=3)
canvas.create_text(50, 70, text="10:00")
canvas.create_text(canvas_width - 50, 70, text="8:00")

# Calculer l'échelle (pixels par minute)
pixels_per_minute = (canvas_width - 100) / total_minutes

# Fonction pour mettre à jour la position de l'indicateur
def update_indicator():
    now = datetime.datetime.now()
    print(str(start_time.time())+" <= "+str(now.time())+" <= "+str(end_time.time()))
    if start_time.time() <= now.time() <= end_time.time():
        elapsed_minutes = (now - start_time).total_seconds() / 60
        x_position = 50 + elapsed_minutes * pixels_per_minute
        #canvas.coords(indicator, x_position, 45, x_position, 55)  # Déplacer l'indicateur

    # Planifier la prochaine mise à jour
    root.after(1000, update_indicator)

# Ajouter l'indicateur
indicator = canvas.create_line(50, 45, 50, 55, width=5, fill="red")#
#indicator = canvas.create_line(100, 100, 100, 100, width=10, fill="red")

# Démarrer la mise à jour de l'indicateur
update_indicator()

# Lancer la boucle principale
root.mainloop()

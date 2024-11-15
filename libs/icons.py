from datetime import datetime


# Fonction pour ajouter un événement avec une icône et une heure sous l'icône
def add_event_icon(event_time_str, icon_path,start_time,end_time):
    today = datetime.datetime.now().date()
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

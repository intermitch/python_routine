import tkinter as tk
import datetime

class ButtonManager:
    def __init__(self, root, canvas, bar_y, y_offset, button_y_offset, bar_start_x, pixels_per_minute, start_time, button_positions, button_states, events, users):
        self.root = root
        self.canvas = canvas
        self.bar_y = bar_y
        self.y_offset = y_offset
        self.button_y_offset = button_y_offset
        self.bar_start_x = bar_start_x
        self.pixels_per_minute = pixels_per_minute
        self.start_time = start_time
        self.button_positions = button_positions
        self.button_states = button_states
        self.events = events
        self.users = users

    def create_buttons(self, toggle_callback):
        event_buttons = []  # Liste pour suivre les boutons des événements
        green_text = []  # Liste pour suivre le texte vert

        for user_idx, user in enumerate(self.users):
            user_buttons = []
            if len(self.button_states) <= user_idx:
                self.button_states.append([])  # Ajouter une liste pour cet utilisateur

            for event_idx, event in enumerate(self.events):
                # Calculer la position X de chaque bouton en fonction de l'événement
                event_time = datetime.datetime.combine(datetime.datetime.now().date(),
                                                       datetime.datetime.strptime(event["time"], "%H:%M").time())
                elapsed_minutes = (event_time - self.start_time).total_seconds() / 60
                x_position = self.bar_start_x + elapsed_minutes * self.pixels_per_minute

                # Créer le bouton rouge sous l'événement pour chaque utilisateur
                button = tk.Button(self.root, text=" ", width=5, height=1, bg="red",
                                   command=lambda u_idx=user_idx, e_idx=event_idx: toggle_callback(u_idx, e_idx))

                # Décalage vertical du bouton si un événement précédent est proche
                if len(self.button_positions) > 1 and (
                        event_time - self.button_positions[-2][1]).total_seconds() <= 300:
                    pos_y_mod = 0 if len(self.button_positions) % 2 == 0 else 30
                else:
                    pos_y_mod = 0

                self.button_positions.append((x_position, event_time))
                button.place(x=x_position - 25,
                             y=self.bar_y + self.y_offset + user_idx * self.button_y_offset - pos_y_mod)  # Placer le bouton sous l'événement
                user_buttons.append(button)

                # Initialement rouge
                self.button_states[user_idx].append(False)

            event_buttons.append(user_buttons)

            # Afficher le nom de l'utilisateur dans la première colonne
            self.canvas.create_text(self.bar_start_x - 80, self.bar_y + self.y_offset + user_idx * self.button_y_offset,
                                    text=user["name"], anchor="e", font=("Helvetica", 12))

            # Calculer le nombre de boutons verts
            green_count = sum(1 for state in self.button_states[user_idx] if state)
            total_count = len(self.button_states[user_idx])
            green_percentage = f"{green_count}/{total_count}"

            # Afficher le nombre de boutons verts/total à la fin de la ligne de l'utilisateur
            green_text_item = self.canvas.create_text(self.bar_start_x + len(self.events) * self.pixels_per_minute + 1800,
                                                      self.bar_y + self.y_offset + user_idx * self.button_y_offset,
                                                      text=green_percentage, anchor="w", font=("Helvetica", 12))
            green_text.append(green_text_item)  # Sauvegarder la référence pour mise à jour

        return event_buttons, self.button_states, green_text

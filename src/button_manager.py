import tkinter as tk
import datetime
from pygame import mixer  # Pour gérer les sons

class ButtonManager:
    def __init__(self, root, canvas, bar_y, y_offset, button_y_offset, bar_start_x, bar_end_x, pixels_per_minute, start_time, button_positions, button_states, events, users):
        self.root = root
        self.canvas = canvas
        self.bar_y = bar_y
        self.y_offset = y_offset
        self.button_y_offset = button_y_offset
        self.bar_start_x = bar_start_x
        self.bar_end_x = bar_end_x
        self.pixels_per_minute = pixels_per_minute
        self.start_time = start_time
        self.button_positions = button_positions
        self.button_states = button_states
        self.events = events
        self.users = users

        # Initialiser le lecteur de son
        mixer.init()

    def create_buttons(self, toggle_callback, button_sound):
        """
        Crée les boutons pour chaque utilisateur et événement.
        :param toggle_callback: Fonction à appeler lorsque le bouton est cliqué.
        :param button_sound: Chemin du fichier son à jouer lors du clic sur un bouton.
        """
        event_buttons = []  # Liste pour suivre les boutons des événements
        green_text = []  # Liste pour suivre le texte vert

        for user_idx, user in enumerate(self.users):
            user_buttons = []
            if len(self.button_states) <= user_idx:
                self.button_states.append([])  # Ajouter une liste pour cet utilisateur

            for event_idx, event in enumerate(self.events):
                # Calculer la position X de chaque bouton en fonction de l'heure de l'événement
                event_time = datetime.datetime.combine(datetime.datetime.now().date(),
                                                       datetime.datetime.strptime(event["time"], "%H:%M").time())
                elapsed_minutes = (event_time - self.start_time).total_seconds() / 60
                x_position = self.bar_start_x + elapsed_minutes * self.pixels_per_minute

                # Créer le bouton rouge sous l'événement pour chaque utilisateur
                button = tk.Button(
                    self.root, text=" ", width=5, height=1, bg="red",
                    command=lambda u_idx=user_idx, e_idx=event_idx: self.on_button_click(u_idx, e_idx, button_sound,
                                                                                         toggle_callback)
                )

                pos_y_mod = 0
                self.button_positions.append((x_position, event_time))
                button.place(
                    x=x_position - 25,
                    y=self.bar_y + self.y_offset + user_idx * self.button_y_offset - pos_y_mod
                )  # Placer le bouton sous l'événement
                user_buttons.append(button)

                # Initialement rouge
                self.button_states[user_idx].append(False)

            event_buttons.append(user_buttons)

            # Afficher le nom de l'utilisateur dans la première colonne
            self.canvas.create_text(
                self.bar_start_x - 80, self.bar_y + self.y_offset + user_idx * self.button_y_offset,
                text=user["name"], anchor="e", font=("Helvetica", 12)
            )

            # Calculer le nombre de boutons verts
            green_count = sum(1 for state in self.button_states[user_idx] if state)
            total_count = len(self.button_states[user_idx])
            green_percentage = f"{green_count}/{total_count}"

            # Afficher le nombre de boutons verts/total à la fin de la ligne de l'utilisateur
            green_text_item = self.canvas.create_text(
                self.bar_end_x,
                self.bar_y + self.y_offset + user_idx * self.button_y_offset,
                text=green_percentage, anchor="w", font=("Helvetica", 12)
            )
            green_text.append(green_text_item)  # Sauvegarder la référence pour mise à jour

        return event_buttons, self.button_states, green_text

    def on_button_click(self, user_idx, event_idx, sound_path, toggle_callback):
        """
        Callback pour gérer les clics sur les boutons.
        :param user_idx: Index de l'utilisateur.
        :param event_idx: Index de l'événement.
        :param sound_path: Chemin du fichier son associé.
        :param toggle_callback: Fonction de basculement d'état.
        """
        button_sound_path = sound_path.get('button')
        # Jouer le son si disponible
        if sound_path:
            try:
                mixer.music.load(button_sound_path)
                mixer.music.play()
            except Exception as e:
                print(f"Erreur lors de la lecture du son : {e}")

        # Appeler le callback de basculement
        toggle_callback(user_idx, event_idx)

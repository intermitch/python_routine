import os
import random
import tkinter as tk
import datetime
from pathlib import Path

from pygame import mixer

from src.json_data_loader import JsonDataLoader
from src.event_manager import EventManager
from src.button_manager import ButtonManager
from PIL import Image, ImageTk


class TimelineApp:
    def __init__(self, events_file, fullscreen=True):
        """
        Initialisation de l'application TimelineApp.
        """
        # Charger les données du fichier JSON
        self.events_file = events_file
        self.fullscreen = fullscreen
        self.data_loader = JsonDataLoader(events_file)
        self.title = self.data_loader.data["title"]
        self.start_hour = self.data_loader.data["start_hour"]
        self.end_hour = self.data_loader.data["end_hour"]
        self.timelines = self.data_loader.data["timelines"]  # Charger les timelines
        self.users = self.data_loader.data["users"]
        self.num_users = len(self.users)
        self.sounds = self.data_loader.data["sounds"]

        # Gestion des événements journaliers
        self.daily_events = self.data_loader.data.get("daily_events", {})
        self.daily_events_random = self.data_loader.data.get("daily_events_random", [])

        # Calcul des heures de début et de fin
        self.today = datetime.datetime.now().date()
        self.start_time = datetime.datetime.combine(
            self.today, datetime.datetime.strptime(self.start_hour, "%H:%M").time()
        )
        self.end_time = datetime.datetime.combine(
            self.today, datetime.datetime.strptime(self.end_hour, "%H:%M").time()
        )
        self.total_minutes = int((self.end_time - self.start_time).total_seconds() / 60)

        # Initialisation de la fenêtre principale
        self.root = tk.Tk()
        self.root.title("Routine - " + self.title)
        if self.fullscreen:
            self.root.attributes("-fullscreen", True)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Configuration du canvas
        self.canvas_width = self.screen_width * 0.8
        self.canvas_height = self.screen_height
        self.canvas = tk.Canvas(
            self.root, width=self.screen_width, height=self.screen_height, bg="white"
        )
        self.canvas.pack()

        # Positions de base pour la timeline
        self.bar_y = self.screen_height // 4  # Point de départ pour la première timeline
        self.bar_start_x = (self.screen_width - self.canvas_width) // 2
        self.bar_end_x = self.bar_start_x + self.canvas_width
        self.pixels_per_minute = self.canvas_width / self.total_minutes

        # Gestionnaire d'événements
        self.event_manager = EventManager(
            self.timelines,
            self.start_time,
            self.end_time,
            self.canvas,
            self.bar_y,
            self.bar_start_x,
            self.pixels_per_minute,
        )

        # Icône de l'indicateur de temps courant
        self.icon_indicator = None
        self.current_time_text = None

        # Gestion des boutons et de leur état
        self.event_buttons = []
        self.button_states = []  # Suivi de l'état des boutons : True pour vert, False pour rouge
        self.user_names = [user["name"] for user in self.users]  # Noms des utilisateurs
        self.button_positions = []

    def run(self):
        self.canvas.create_text(
            self.screen_width // 2, 50, text=self.title, font=("Helvetica", 48), anchor="center"
        )

        timeline_y_offset = 100
        for idx, timeline in enumerate(self.timelines):
            bar_y = self.bar_y + idx * timeline_y_offset
            self.canvas.create_line(
                self.bar_start_x, bar_y, self.bar_end_x, bar_y, fill="black", width=5
            )
            self.canvas.create_text(self.bar_start_x - 50, bar_y, text=f"Ligne {timeline['id']}", anchor="e")

            # Ajouter les événements
            for event in timeline["events"]:
                self.event_manager.add_event_icon(event["time"], event["icon_path"])

        self.root.mainloop()

    def update_indicator(self):
        now = datetime.datetime.now()
        now_time = datetime.datetime.combine(self.today, now.time())

        self.canvas.itemconfig(self.current_time_text, text=now.strftime("%H:%M:%S"))

        resultats = [
                        indicator for indicator in reversed(self.indicators)
                        if datetime.datetime.combine(self.today, datetime.datetime.strptime(indicator["time"],
                                                                                            "%H:%M").time()) <= now_time
                    ] or [self.indicators[-1]]

        self.event_manager.update_event_frames(now_time)
        self.event_manager.update_indicator_icon(self.icon_indicator, resultats[0]["icon_path"])

        if self.start_time <= now_time <= self.end_time:
            elapsed_minutes = (now_time - self.start_time).total_seconds() / 60
            x_position = self.bar_start_x + elapsed_minutes * self.pixels_per_minute
            self.canvas.coords(self.icon_indicator, x_position, self.bar_y)

        self.root.after(1000, self.update_indicator)

    def exit_fullscreen(self, event):
        self.root.attributes("-fullscreen", False)
        self.root.destroy()

    def toggle_button(self, user_idx, event_idx):
        """Change la couleur du bouton (rouge ou vert) pour un utilisateur et un événement donnés"""
        if self.button_states[user_idx][event_idx]:
            self.event_buttons[user_idx][event_idx].config(bg="red")  # Retour au rouge
            self.button_states[user_idx][event_idx] = False
        else:
            self.event_buttons[user_idx][event_idx].config(bg="green")  # Passage au vert
            self.button_states[user_idx][event_idx] = True

        # Mettre à jour le texte affichant le nombre de boutons verts/total
        self.update_completion(user_idx)

    def update_completion(self, user_idx):
        """Met à jour le texte affichant le nombre de boutons verts/total pour un utilisateur donné"""
        green_count = sum(1 for state in self.button_states[user_idx] if state)
        total_count = len(self.button_states[user_idx])
        green_percentage = f"{green_count}/{total_count}"

        if green_count/total_count == 1:

            # Initialiser le lecteur de son
            mixer.init()

            print("Réussite")
            button_sound_path = self.load_sounds().get('completion')
            print(button_sound_path)
            # Jouer le son si disponible
            if self.load_sounds():
                try:
                    mixer.music.load(button_sound_path)
                    mixer.music.play()
                except Exception as e:
                    print(f"Erreur lors de la lecture du son : {e}")

        # Mettre à jour le texte de la colonne des boutons verts/total
        self.canvas.itemconfig(self.green_text[user_idx], text=green_percentage)

    def create_buttons(self):
        """Créer les boutons sous les événements pour chaque utilisateur"""
        y_offset = 100  # Décalage vertical pour la ligne des boutons principaux
        button_y_offset = 120  # Décalage pour les lignes supplémentaires (utilisateurs)
        self.event_buttons = []  # Réinitialiser les boutons
        self.button_states = []  # Réinitialiser l'état des boutons
        self.green_text = []  # Réinitialiser les éléments de texte pour le nombre de boutons verts

        # Charger les sons associés aux événements
        sounds = self.load_sounds()

        #button_manager = ButtonManager(self.root, self.canvas, self.bar_y, y_offset, button_y_offset, self.bar_start_x, self.pixels_per_minute, self.start_time, self.button_positions, self.button_states, self.events, self.users)
        button_manager = ButtonManager(
            self.root,
            self.canvas,
            self.bar_y,
            y_offset,
            button_y_offset,
            self.bar_start_x,
            self.bar_end_x,
            self.pixels_per_minute,
            self.start_time,
            self.button_positions,
            self.button_states,
            self.events,
            self.users
        )
        self.event_buttons, self.button_states, self.green_text = button_manager.create_buttons(self.toggle_button, sounds)

    def load_sounds(self):
        """
        Charger les sons associés depuis la section 'sound' du fichier JSON.
        Retourne un dictionnaire avec les types de sons comme clés et leurs chemins complets comme valeurs.
        """
        sounds = {}
        for sound in self.data_loader.data.get("sounds", []):  # Utilise la clé 'sounds' corrigée
            if "type" in sound and "sound_path" in sound:  # Vérifie que les clés existent
                sounds[sound["type"]] = sound["sound_path"]
            else:
                print(f"Entrée de son invalide dans le JSON : {sound}")

        #print("Sons chargés :", sounds)  # Affiche les sons chargés pour le débogage
        return sounds

    import random

    def display_daily_event(self):
        """
        Affiche un événement quotidien dans un carré en haut à droite.
        Si aucun événement spécifique au jour n'est défini, un événement aléatoire est choisi.
        """
        # Obtenir le jour de la semaine
        today = datetime.datetime.now().strftime("%A")

        # Charger les événements journaliers et aléatoires
        daily_events = self.data_loader.data.get("daily_events", {})
        random_events = self.data_loader.data.get("daily_events_random", [])

        # Récupérer l'événement spécifique au jour
        event = daily_events.get(today, None)

        # Si aucun événement spécifique au jour, choisir un événement aléatoire
        if not event and random_events:
            event = random.choice(random_events)

            # Construire le chemin absolu pour l'icône si nécessaire
            if "icon" in event and "icon_path" not in event:
                project_root = Path(__file__).resolve().parents[1]
                event["icon_path"] = os.path.join(project_root, event["icon"])

        # Si un événement est trouvé, afficher son icône et sa description
        if event:
            icon_path = event.get("icon_path")
            description = event.get("description", "")

            # Ajouter un rectangle (le fond du carré)
            self.canvas.create_rectangle(
                self.screen_width - 300, 20, self.screen_width - 20, 300, fill="yellow", outline="black"
            )

            # Ajouter un titre en gras centré en haut du carré
            self.canvas.create_text(
                self.screen_width - 160, 40, text=f"Défi",
                font=("Helvetica", 16, "bold"), anchor="center"
            )

            # Charger et afficher l'icône si disponible
            if icon_path:
                icon_image = Image.open(icon_path)
                icon_image = icon_image.resize((210, 210), Image.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)

                self.canvas.create_image(
                    self.screen_width - 160, 165, image=icon_photo, anchor="center"
                )

                # Sauvegarder l'image pour éviter que le ramasse-miettes ne la supprime
                if not hasattr(self, "image_references"):
                    self.image_references = []
                self.image_references.append(icon_photo)

            # Ajouter une description sous l'icône
            self.canvas.create_text(
                self.screen_width - 160, 285, text=description,
                font=("Helvetica", 12), anchor="center"
            )


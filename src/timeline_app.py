import tkinter as tk
import datetime

from pygame import mixer

from src.json_data_loader import JsonDataLoader
from src.event_manager import EventManager
from src.button_manager import ButtonManager
from PIL import Image, ImageTk


class TimelineApp:
    def __init__(self, events_file, fullscreen=True):
        self.events_file = events_file
        self.fullscreen = fullscreen
        self.data_loader = JsonDataLoader(events_file)
        self.title = self.data_loader.data["title"]
        self.start_hour = self.data_loader.data["start_hour"]
        self.end_hour = self.data_loader.data["end_hour"]
        self.events = self.data_loader.data["events"]
        self.users = self.data_loader.data["users"]
        self.num_users = len(self.users)
        self.indicators = self.data_loader.data["indicators"]

        self.today = datetime.datetime.now().date()
        self.start_time = datetime.datetime.combine(self.today,
                                                    datetime.datetime.strptime(self.start_hour, "%H:%M").time())
        self.end_time = datetime.datetime.combine(self.today, datetime.datetime.strptime(self.end_hour, "%H:%M").time())
        self.total_minutes = int((self.end_time - self.start_time).total_seconds() / 60)

        self.root = tk.Tk()
        self.root.title("Routine - " + self.title)
        if self.fullscreen:
            self.root.attributes("-fullscreen", True)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.canvas_width = self.screen_width * 0.8
        self.canvas_height = 100
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, bg="white")
        self.canvas.pack()

        self.bar_y = self.screen_height // 2
        self.bar_start_x = (self.screen_width - self.canvas_width) // 2
        self.bar_end_x = self.bar_start_x + self.canvas_width
        self.pixels_per_minute = self.canvas_width / self.total_minutes

        self.event_manager = EventManager(self.events, self.start_time, self.end_time, self.canvas, self.bar_y,
                                          self.bar_start_x, self.pixels_per_minute)

        self.icon_indicator = None
        self.current_time_text = None

        # Liste pour suivre l'état des boutons (rouge ou vert)
        self.event_buttons = []
        self.button_states = []  # Suivi de l'état des boutons : True pour vert, False pour rouge
        self.user_names = [user['name'] for user in self.users]  # Noms d'utilisateurs
        self.button_positions = []


    def run(self):
        self.canvas.create_text(
            self.screen_width // 2, 50, text=self.title, font=("Helvetica", 48), anchor="center"
        )

        # Création de la timeline
        self.canvas.create_line(self.bar_start_x, self.bar_y, self.bar_end_x, self.bar_y, fill="black", width=5)
        self.canvas.create_text(self.bar_start_x, self.bar_y + 20, text=self.start_hour, anchor="e")
        self.canvas.create_text(self.bar_end_x, self.bar_y + 20, text=self.end_hour, anchor="w")

        self.event_manager.add_all_event_icons()

        self.icon_indicator = self.event_manager.add_indicator_icon(self.indicators[0]["icon_path"])
        self.current_time_text = self.canvas.create_text(self.screen_width // 2, self.screen_height - 50, text="",
                                                         font=("Helvetica", 48), anchor="center")

        # Appeler la méthode pour créer les boutons sous chaque événement pour chaque utilisateur
        self.create_buttons()

        # Appeler la méthode pour afficher l'événement quotidien
        self.display_daily_event()

        self.root.bind("<Escape>", self.exit_fullscreen)

        self.update_indicator()

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

    def display_daily_event(self):
        """
        Affiche un événement quotidien dans un carré en haut à droite.
        """
        #today = datetime.now().strftime("%A")  # Obtenir le jour de la semaine
        today = datetime.datetime.now().strftime("%A")

        daily_events = self.data_loader.data["daily_events"]
        event = daily_events.get(today, None)

        # Si un événement est trouvé, afficher son icône et sa description
        if event:
            icon_path = event.get("icon_path")
            description = event.get("description", "")

            # Charger l'icône
            if icon_path:
                icon_image = Image.open(icon_path)
                icon_image = icon_image.resize((100, 100), Image.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)

                # Ajouter un rectangle
                self.canvas.create_rectangle(
                    self.screen_width - 300, 20, self.screen_width - 20, 300, fill="lightgray", outline="black"
                )
                # Ajouter l'icône
                self.canvas.create_image(
                    self.screen_width - 90, 60, image=icon_photo, anchor="center"
                )

                # Sauvegarder l'image pour éviter que le ramasse-miettes ne la supprime
                if not hasattr(self, "image_references"):
                    self.image_references = []
                self.image_references.append(icon_photo)

            # Ajouter le texte
            self.canvas.create_text(
                self.screen_width - 90, 120, text=description, font=("Helvetica", 12), anchor="center"
            )
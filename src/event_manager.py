import datetime
from PIL import Image, ImageTk


class EventManager:
    def __init__(self, events_data, start_time, end_time, canvas, bar_y, bar_start_x, pixels_per_minute):
        self.events = events_data
        self.indicators = []
        self.start_time = start_time
        self.end_time = end_time
        self.canvas = canvas
        self.bar_y = bar_y
        self.bar_start_x = bar_start_x
        self.pixels_per_minute = pixels_per_minute
        self.event_icons = []
        self.event_positions = []
        self.event_frames = []

    def add_event_icon(self, event_time_str, icon_path, bar_y):
        """
        Ajoute une icône d'événement à une position spécifique sur la timeline.
        :param event_time_str: Heure de l'événement (format HH:MM).
        :param icon_path: Chemin vers l'icône de l'événement.
        :param bar_y: Position verticale de la timeline.
        """
        event_time = datetime.datetime.combine(
            self.start_time.date(),
            datetime.datetime.strptime(event_time_str, "%H:%M").time()
        )
        if self.start_time <= event_time <= self.end_time:
            elapsed_minutes = (event_time - self.start_time).total_seconds() / 60
            x_position = self.bar_start_x + elapsed_minutes * self.pixels_per_minute

            # Charger l'icône
            icon_image = Image.open(icon_path)
            icon_image = icon_image.resize((30, 30), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)

            # Ajouter l'icône au canvas
            self.canvas.create_image(x_position, bar_y - 30, image=icon_photo, anchor="center")

            # Sauvegarder l'image pour éviter qu'elle soit supprimée
            if not hasattr(self, "image_references"):
                self.image_references = []
            self.image_references.append(icon_photo)

    def add_indicator_icon(self, icon_path):
        # Charger l'image (WebP ou tout autre format supporté)
        icon_image = Image.open(icon_path)

        # Vérifier si l'image a un canal alpha, sinon le convertir en RGBA
        if icon_image.mode != "RGBA":
            icon_image = icon_image.convert("RGBA")

        # Redimensionner l'image
        icon_image = icon_image.resize((80, 80), Image.LANCZOS)

        # Créer une version compatible avec Tkinter
        icon = ImageTk.PhotoImage(icon_image)

        # Sauvegarder une référence pour empêcher le ramasse-miettes de supprimer l'image
        if not hasattr(self.canvas, "image_references"):
            self.canvas.image_references = []
        self.canvas.image_references.append(icon)

        # Ajouter l'image à la Canvas
        return self.canvas.create_image(self.bar_start_x, self.bar_y, image=icon, anchor="center")

    def add_indicator_icon(self, indicator_time, icon_path, bar_y):
        """
        Ajoute une icône d'indicateur à une timeline spécifique.
        :param indicator_time: Heure de l'indicateur.
        :param icon_path: Chemin vers l'icône de l'indicateur.
        :param bar_y: Position verticale de la timeline.
        """
        indicator_time = datetime.datetime.combine(
            self.start_time.date(),
            datetime.datetime.strptime(indicator_time, "%H:%M").time()
        )
        if self.start_time <= indicator_time <= self.end_time:
            elapsed_minutes = (indicator_time - self.start_time).total_seconds() / 60
            x_position = self.bar_start_x + elapsed_minutes * self.pixels_per_minute

            # Charger l'icône
            icon_image = Image.open(icon_path)
            icon_image = icon_image.resize((30, 30), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)

            # Ajouter l'icône au canvas
            self.canvas.create_image(x_position, bar_y - 30, image=icon_photo, anchor="center")

            # Sauvegarder l'image pour éviter qu'elle soit supprimée
            if not hasattr(self, "image_references"):
                self.image_references = []
            self.image_references.append(icon_photo)

    def update_event_frames(self, now_time):
        for i, (event_x, event_time) in enumerate(self.event_positions):
            time_difference = abs((now_time - event_time).total_seconds() / 60)
            if time_difference <= 2:
                if len(self.event_frames) <= i or not self.event_frames[i]:
                    frame = self.canvas.create_rectangle(
                        event_x - 30, self.bar_y - 30 - 80, event_x + 30, self.bar_y + 30 - 80, outline="red", width=2
                    )
                    if len(self.event_frames) > i:
                        self.event_frames[i] = frame
                    else:
                        self.event_frames.append(frame)
            else:
                if len(self.event_frames) > i and self.event_frames[i]:
                    self.canvas.delete(self.event_frames[i])
                    self.event_frames[i] = None

    def add_all_event_icons(self):
        """
        Ajoute toutes les icônes d'événements pour chaque timeline.
        """
        for timeline in self.timelines:
            # Déterminer la position verticale pour cette timeline
            timeline_id = timeline["id"]
            bar_y = self.bar_y + (timeline_id - 1) * 100  # Décalage vertical par timeline

            # Ajouter les icônes d'événements pour cette timeline
            for event in timeline["events"]:
                self.add_event_icon(event["time"], event["icon_path"], bar_y)


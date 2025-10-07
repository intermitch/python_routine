import datetime
import os
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

        # Dossier relatif pour les icônes météo
        self.weather_icon_dir = os.path.join(
            os.path.dirname(__file__), "..", "images", "addon", "weather"
        )

    def _get_icon_path(self, filename):
        """Retourne le chemin complet d'une icône à partir du dossier weather."""
        return os.path.join(self.weather_icon_dir, filename)

    def add_event_icon(self, event_time_str, icon_filename):
        event_time = datetime.datetime.combine(
            self.start_time.date(),
            datetime.datetime.strptime(event_time_str, "%H:%M").time()
        )
        if self.start_time <= event_time <= self.end_time:
            elapsed_minutes = (event_time - self.start_time).total_seconds() / 60
            x_position = self.bar_start_x + elapsed_minutes * self.pixels_per_minute

            icon_path = self._get_icon_path(icon_filename)
            event_icon_image = Image.open(icon_path)

            if event_icon_image.mode != "RGBA":
                event_icon_image = event_icon_image.convert("RGBA")

            event_icon_image = event_icon_image.resize((50, 50), Image.LANCZOS)
            event_icon = ImageTk.PhotoImage(event_icon_image)

            icon_id = self.canvas.create_image(x_position, self.bar_y - 80, image=event_icon, anchor="center")
            self.event_icons.append(event_icon)
            self.event_positions.append((x_position, event_time))

            pos_y_mod = 0 if len(self.event_positions) % 2 == 0 else 20
            self.canvas.create_text(x_position, self.bar_y + 60 - pos_y_mod, text=event_time_str, anchor="n")

    def add_indicator_icon(self, icon_filename):
        icon_path = self._get_icon_path(icon_filename)
        icon_image = Image.open(icon_path)

        if icon_image.mode != "RGBA":
            icon_image = icon_image.convert("RGBA")

        icon_image = icon_image.resize((80, 80), Image.LANCZOS)
        icon = ImageTk.PhotoImage(icon_image)

        if not hasattr(self.canvas, "image_references"):
            self.canvas.image_references = []
        self.canvas.image_references.append(icon)

        return self.canvas.create_image(self.bar_start_x, self.bar_y, image=icon, anchor="center")

    def update_indicator_icon(self, canvas_item, new_icon_filename):
        icon_path = self._get_icon_path(new_icon_filename)
        icon_image = Image.open(icon_path)
        icon_image = icon_image.resize((80, 80), Image.LANCZOS)
        new_icon = ImageTk.PhotoImage(icon_image)

        if not hasattr(self.canvas, "image_references"):
            self.canvas.image_references = []
        self.canvas.image_references.append(new_icon)

        self.canvas.itemconfig(canvas_item, image=new_icon)

    def update_event_frames(self, now_time):
        for i, (event_x, event_time) in enumerate(self.event_positions):
            time_difference = abs((now_time - event_time).total_seconds() / 60)
            if time_difference <= 2:
                if len(self.event_frames) <= i or not self.event_frames[i]:
                    frame = self.canvas.create_rectangle(
                        event_x - 30, self.bar_y - 110, event_x + 30, self.bar_y - 50, outline="red", width=2
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
        for event in self.events:
            self.add_event_icon(event["time"], event["icon_path"])

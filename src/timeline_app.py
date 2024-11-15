
import tkinter as tk
import datetime

from src.json_data_loader import JsonDataLoader
from src.event_manager import EventManager


class TimelineApp:
    def __init__(self, events_file, fullscreen=True):
        self.events_file = events_file
        self.fullscreen = fullscreen
        self.data_loader = JsonDataLoader(events_file)
        self.title = self.data_loader.data["title"]
        self.start_hour = self.data_loader.data["start_hour"]
        self.end_hour = self.data_loader.data["end_hour"]
        self.events = self.data_loader.data["events"]
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

    def update_indicator(self):
        now = datetime.datetime.now()
        now_time = datetime.datetime.combine(self.today, now.time())

        self.canvas.itemconfig(self.current_time_text, text=now.strftime("%H:%M:%S"))

        resultats = [indicator for indicator in reversed(self.indicators) if
                     datetime.datetime.combine(self.today, datetime.datetime.strptime(indicator["time"],
                                                                                      "%H:%M").time()) <= now_time]

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

    def run(self):
        self.canvas.create_text(
            self.screen_width // 2, 50, text=self.title, font=("Helvetica", 48), anchor="center"
        )

        #création de la timeline
        self.canvas.create_line(self.bar_start_x, self.bar_y, self.bar_end_x, self.bar_y, fill="black", width=5)
        self.canvas.create_text(self.bar_start_x, self.bar_y + 20, text=self.start_hour, anchor="e")
        self.canvas.create_text(self.bar_end_x, self.bar_y + 20, text=self.end_hour, anchor="w")

        self.event_manager.add_all_event_icons()

        self.icon_indicator = self.event_manager.add_indicator_icon(self.indicators[0]["icon_path"])
        self.current_time_text = self.canvas.create_text(self.screen_width // 2, self.screen_height - 50, text="",
                                                         font=("Helvetica", 48), anchor="center")

        self.root.bind("<Escape>", self.exit_fullscreen)

        self.update_indicator()

        self.root.mainloop()


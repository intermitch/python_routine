import os
import random
import tkinter as tk
import datetime
from pathlib import Path

from pygame import mixer

from src.json_data_loader import JsonDataLoader
from src.event_manager import EventManager
from PIL import Image, ImageTk

class TimelineApp:
    def __init__(self, events_file, fullscreen=True):
        self.events_file = events_file
        self.fullscreen = fullscreen
        self.data_loader = JsonDataLoader(events_file)
        self.title = self.data_loader.data["title"]
        self.start_hour = self.data_loader.data["start_hour"]
        self.end_hour = self.data_loader.data["end_hour"]
        self.timelines = self.data_loader.data["timelines"]

        self.today = datetime.datetime.now().date()
        self.start_time = datetime.datetime.combine(self.today, datetime.datetime.strptime(self.start_hour, "%H:%M").time())
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

        self.bar_start_x = (self.screen_width - self.canvas_width) // 2
        self.bar_end_x = self.bar_start_x + self.canvas_width
        self.pixels_per_minute = self.canvas_width / self.total_minutes

        self.event_manager = EventManager(self.canvas, self.bar_start_x, self.pixels_per_minute, self.today, self.start_time, self.end_time)

        self.image_references = []

    def run(self):
        self.canvas.create_text(
            self.screen_width // 2, 50, text=self.title, font=("Helvetica", 48), anchor="center"
        )

        y_offset = 0
        for timeline in self.timelines:
            # Timeline name
            self.canvas.create_text(
                self.screen_width // 2, 100 + y_offset, text=timeline["name"], font=("Helvetica", 24), anchor="center"
            )

            timeline_y_offset = y_offset + 100

            self.event_manager.add_events(timeline["events"], timeline_y_offset)
            self.event_manager.add_indicators(timeline["indicators"], timeline_y_offset)

            for user_idx, user in enumerate(timeline["users"]):
                user_bar_y = timeline_y_offset + user_idx * 150
                self.canvas.create_line(
                    self.bar_start_x, user_bar_y, self.bar_end_x, user_bar_y, fill="black", width=2
                )
                self.canvas.create_text(
                    self.bar_start_x - 100, user_bar_y, text=user["name"], anchor="e", font=("Helvetica", 12)
                )

            y_offset += len(timeline["users"]) * 150 + 200

        self.root.bind("<Escape>", self.exit_fullscreen)
        self.update_indicator()
        self.root.mainloop()

    def update_indicator(self):
        now = datetime.datetime.now()
        now_time = datetime.datetime.combine(self.today, now.time())

        for timeline in self.timelines:
            indicators = timeline["indicators"]
            active_indicator = next(
                (indicator for indicator in reversed(indicators)
                 if datetime.datetime.combine(self.today, datetime.datetime.strptime(indicator["time"], "%H:%M").time()) <= now_time),
                None
            )
            if active_indicator:
                pass  # Update logic for active indicators if needed

        self.root.after(1000, self.update_indicator)

    def exit_fullscreen(self, event):
        self.root.attributes("-fullscreen", False)
        self.root.destroy()

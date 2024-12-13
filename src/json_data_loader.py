import os
import json
from pathlib import Path


class JsonDataLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = self.load_data()

    def load_data(self):
        project_root = Path(__file__).resolve().parents[1]
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        daily_events_list = data.get("daily_events", [])
        daily_events = {}
        for event in daily_events_list:
            if "day" in event and "icon" in event:
                day = event["day"]
                event["icon_path"] = os.path.join(project_root, "images", event["icon"])
                daily_events[day] = {
                    "icon_path": event["icon_path"],
                    "description": event.get("description", "")
                }

        daily_events_random_list = data.get("daily_events_random", [])
        daily_events_random = []
        for event in daily_events_random_list:
            if "icon" in event:
                event["icon_path"] = os.path.join(project_root, "images", event["icon"])
                daily_events_random.append({
                    "icon_path": event["icon_path"],
                    "description": event.get("description", "")
                })
        sounds_data = data.get("sounds", [])
        for sound in sounds_data:
            sound["sound_path"] = os.path.join(project_root, "sounds", sound["file"])

        timelines_data = data.get("timelines", [])
        for timeline in timelines_data:
            for user in timeline["users"]:
                for event in user.get("events", []):
                    event["icon_path"] = os.path.join(project_root, "images", event["icon"])

        title = data.get("title", "Titre")
        start_hour = data.get("start_hour", "00:00")
        end_hour = data.get("end_hour", "23:59")

        return {
            "title": title,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "sounds": sounds_data,
            "timelines": timelines_data,
            "daily_events": daily_events,
            "daily_events_random": daily_events_random
        }

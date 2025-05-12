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

        users_data = data.get("users", [])

        events_data = data.get("events", [])
        for event in events_data:
            event["icon_path"] = os.path.join(project_root, "images", event["icon"])

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

        indicators_data = data.get("indicators", [])
        for indicator in indicators_data:
            indicator["icon_path"] = os.path.join(project_root, "images", indicator["icon"])

        sounds_data = data.get("sounds", [])
        for sound in sounds_data:
            sound["sound_path"] = os.path.join(project_root, "sounds", sound["file"])

        title = data.get("title", "Titre")
        start_hour = data.get("start_hour", "00:00")
        end_hour = data.get("end_hour", "23:59")
        weather_config = data.get("weather", {})

        return {
            "title": title,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "events": events_data,
            "users": users_data,
            "sounds": sounds_data,
            "indicators": indicators_data,
            "daily_events": daily_events,
            "daily_events_random": daily_events_random,
            "weather": weather_config
        }

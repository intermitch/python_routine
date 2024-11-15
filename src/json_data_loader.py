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

        events_data = data.get("events", [])
        for event in events_data:
            event["icon_path"] = os.path.join(project_root, "images", event["icon"])

        indicators_data = data.get("indicators", [])
        for indicator in indicators_data:
            indicator["icon_path"] = os.path.join(project_root, "images", indicator["icon"])

        title = data.get("title", "Titre")
        start_hour = data.get("start_hour", "00:00")
        end_hour = data.get("end_hour", "23:59")

        return {
            "title": title,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "events": events_data,
            "indicators": indicators_data
        }

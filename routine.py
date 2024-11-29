import os
import sys
from src.timeline_app import TimelineApp
from src.args_parser import configure_args  # Importer depuis args_parser

if __name__ == "__main__":
    events_file, fullscreen = configure_args()

    app = TimelineApp(events_file, fullscreen=fullscreen)
    app.run()


#test audio
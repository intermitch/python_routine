import os
import sys
from src.timeline_app import TimelineApp
from src.args_parser import configure_args  # Importer depuis args_parser
if __name__ == "__main__":
    events_file, fullscreen = configure_args()

    app = TimelineApp(events_file, fullscreen=fullscreen)
    app.run()


#test audio

#from pygame import mixer
#mixer.init()
#mixer.music.load("sounds/button.mp3")  # Remplacez par le chemin exact
#mixer.music.play()
#
## Ajoutez une pause pour écouter le son
#import time
#time.sleep(5)  # Attend 5 secondes pour laisser le son jouer
import os
from pygame import mixer

class Sound:
    def __init__(self, sound_data):
        """
        Initialise la gestion des sons avec les données chargées depuis le JSON.
        :param sound_data: Liste des sons définis dans le JSON.
        """
        self.sounds = {}
        self.initialize_sounds(sound_data)

    def initialize_sounds(self, sound_data):
        """
        Initialise les chemins des sons à partir des données JSON.
        :param sound_data: Liste des sons définis dans le JSON.
        """
        for sound in sound_data:
            if "type" in sound and "sound_path" in sound:
                self.sounds[sound["type"]] = sound["sound_path"]
            else:
                print(f"Entrée de son invalide dans le JSON : {sound}")

    def play_sound(self, sound_type):
        """
        Joue un son en fonction de son type.
        :param sound_type: Type du son à jouer (par exemple, 'button', 'completion').
        """
        sound_path = self.sounds.get(sound_type)
        if not sound_path:
            print(f"Son introuvable pour le type : {sound_type}")
            return

        if not os.path.isfile(sound_path):
            print(f"Fichier son introuvable : {sound_path}")
            return

        try:
            mixer.init()
            mixer.music.load(sound_path)
            mixer.music.play()
        except Exception as e:
            print(f"Erreur lors de la lecture du son : {e}")

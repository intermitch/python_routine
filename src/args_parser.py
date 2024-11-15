import os
import sys
import argparse
from pathlib import Path


def configure_args():
    """Configure et renvoie les arguments du script."""
    if len(sys.argv) < 2:
        print("Usage: python routine.py <events_file.json>")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Script pour gérer le mode plein écran.")
    parser.add_argument("filename", type=str, help="Nom du fichier à traiter.")
    parser.add_argument(
        "--nofullscreen",
        action="store_false",
        dest="fullscreen",
        help="Désactiver le mode plein écran."
    )
    parser.set_defaults(fullscreen=True)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    scenario_dir = os.path.join(project_root, "scenario")
    events_file = os.path.join(scenario_dir, args.filename + ".json")

    return events_file, args.fullscreen

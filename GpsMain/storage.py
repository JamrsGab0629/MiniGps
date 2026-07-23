import json
import os

TXT_FILE_PATH = "map_data.txt"


class StorageManager:
    """Handles persistent storage operations for map data."""

    def __init__(self, file_path=TXT_FILE_PATH):
        self.file_path = file_path

    def load(self):
        """Loads junctions and houses from local text/JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    return data.get("junctions", {}), data.get("houses", {})
            except Exception as e:
                print(f"Error loading {self.file_path}: {e}")
        return {}, {}

    def save(self, junctions, houses):
        """Saves current junctions and houses to file."""
        data = {"junctions": junctions, "houses": houses}
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)
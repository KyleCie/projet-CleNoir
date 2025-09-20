
# json and dict handler.
from json import dump, load

# files and directory.
from os import listdir, getcwd, path

class file:

    def __init__(self):

        # directorys.
        self.DIRECTORY = getcwd()
        self.FOLDER_DIR = path.join(self.DIRECTORY, "me")
        self.DATA_DIR = path.join(self.FOLDER_DIR, "data.json")
        self.data = {}
        self.my_name = ""
        
        self._open_json()
    
    def _open_json(self) -> None:
        """open json file."""

        with open(self.DATA_DIR, "r", encoding="utf-8") as file:
            self.data = load(file)

        self.my_name = self.data.get("me", "unknown")

        if self.my_name == "unknown":
            exit()

    def _get_data_json(self) -> tuple[dict, str]:
        """Get the data from data.json"""

        return self.data, self.my_name

    def _store_data_json(self, data) -> None:
        """Store the `self.data` into data.json"""

        with open(self.DATA_DIR, "w", encoding="utf-8") as file:
            dump(data, file, indent=4)

    def _get_parameters_json(self) -> dict:
        """Return the parameter's user from data.json."""

        return self.data.get("parameters")

    def _verify_json_files(self) -> bool:
        """Verify if the data file is here."""

        files = listdir(self.FOLDER_DIR)
        return "data.json" in files
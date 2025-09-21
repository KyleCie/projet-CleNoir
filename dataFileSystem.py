
# json, files and dict handler.
from json import dump, loads, load
from cryptography.fernet import Fernet

# files and directory.s
from os import listdir, getcwd, path

class file:

    def __init__(self):
        
        print("Starting file system...")
        print("-> Creating paths...")
        # directorys.
        self.DIRECTORY = getcwd()
        self.MY_KEY = path.join(self.DIRECTORY, "pems_files", "key.pem")
        self.FOLDER_DIR = path.join(self.DIRECTORY, "me")
        self.DB_DIR = path.join(self.FOLDER_DIR, "db.txt")
        self.DATA_DIR = path.join(self.FOLDER_DIR, "data.json")
        self.data = {}
        self.db_data = {}
        self.my_name = ""
        
        print("-> Opening files...")
        self._open_db()
        self._open_json()
        print("File system done.")

    def _open_db(self) -> None:
        """Open and decrypt the database infos file."""

        with open(self.MY_KEY, "rb") as key_file:
            key = key_file.read()

        fernet = Fernet(key)

        with open(self.DB_DIR, "rb") as file:
            encrypted = file.read()

        decrypted = fernet.decrypt(encrypted)
        self.db_data = loads(decrypted.decode())

    def _open_json(self) -> None:
        """open json file."""

        with open(self.DATA_DIR, "r", encoding="utf-8") as file:
            self.data = load(file)

        self.my_name = self.data.get("me", "unknown")

        if self.my_name == "unknown":
            raise ValueError("The value of self.my_name is None.")

    def _get_db_infos(self) -> dict:
        """Get the dict of the db infos."""

        return self.db_data

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
        return "data.json" in files and "db.txt" in files
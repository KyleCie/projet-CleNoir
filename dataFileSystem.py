
# json, files and dict handler.
from json import dump, loads, load
from cryptography.fernet import Fernet

# decrypting system.
from Crypto.Cipher import AES
from base64 import b64decode

# files and directorys.
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
        self.PWD_DIR = path.join(self.FOLDER_DIR, "pwd.txt")
        self.PC_DIR = path.join(self.FOLDER_DIR, "pc.txt")
        self.DATA_DIR = path.join(self.FOLDER_DIR, "data.json")

        print("-> Init. variables...")
        self.data = {}
        self.db_data = {}
        self.my_name = ""
        
        print("-> Opening files...")
        self._open_db()
        self._open_json()
        print("File system done.")

    def _open_key(self) -> bytes:
        """Open and return the key file."""

        with open(self.MY_KEY, "rb") as key_file:
            key = key_file.read()

        key = b64decode(key)
        key = key[::-1]

        s_k = key[:16]
        nonce = key[16:32]
        cipher_text = key[32:-16]
        tag = key[-16:]

        cipher_aes = AES.new(s_k, AES.MODE_EAX, nonce)
        key = cipher_aes.decrypt_and_verify(cipher_text, tag)

        key = bytes(b ^ 0xAA for b in key)
        key = key[8:-8][::-1]

        return key

    def _open_db(self) -> None:
        """Open and decrypt the database infos file."""

        key = self._open_key()
        fernet = Fernet(key)

        with open(self.DB_DIR, "rb") as file:
            encrypted = file.read()

        decrypted = fernet.decrypt(encrypted)
        self.db_data = loads(decrypted.decode())

    def _open_pwd(self) -> str:
        """Open and decrypt the password file."""

        key = self._open_key()
        fernet = Fernet(key)

        with open(self.PWD_DIR, "rb") as file:
            encrypted = file.read()

        decrypted = fernet.decrypt(encrypted)
        return decrypted.decode()

    def _get_passcode(self) -> str:
        """Get the passcode from the passcode file."""

        key = self._open_key()
        fernet = Fernet(key)

        with open(self.PC_DIR, "rb") as file:
            encrypted = file.read()

        decrypted = fernet.decrypt(encrypted)
        return decrypted.decode()

    def _delete_pwd_file(self) -> None:
        """Delete the password file."""

        if path.exists(self.PWD_DIR):
            path.remove(self.PWD_DIR)

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

    def _save_colors(self, colors: list[str]) -> None:
        """Change and save colors parameters."""

        json_colors = self.data.get("parameters")
        new_json_colors = {k: colors[i] for i, k in enumerate(json_colors)}
        self.data["parameters"] = new_json_colors

        self._store_data_json(self.data)

    def _save_password(self, password: str) -> None:
        """Encrypt and save the new password into pwd.txt"""

        with open(self.MY_KEY, "rb") as key_file:
            key = key_file.read()

        fernet =Fernet(key)
        encrypted = fernet.encrypt(password.encode())

        with open(self.PWD_DIR, "wb") as file:
            file.write(encrypted)

    def _get_parameters_json(self) -> dict:
        """Return the parameter's user from data.json."""

        return self.data.get("parameters")

    def _verify_json_files(self) -> bool:
        """Verify if the data file is here."""

        files = listdir(self.FOLDER_DIR)
        return "data.json" in files and "db.txt" in files

    def _verify_pwd_file(self) -> bool:
        """Verify if the password file is here."""

        files = listdir(self.FOLDER_DIR)
        return "pwd.txt" in files
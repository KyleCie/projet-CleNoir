
# json, files, dict, and password handler.
from Crypto.Random import get_random_bytes
from argon2 import PasswordHasher

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

        # -> keys paths.
        self.KEY_DIR = path.join(self.DIRECTORY, "pems_files")
        self.MY_KEY = path.join(self.DIRECTORY, "pems_files", "key.pem")
        self.PRIVATE_KEY = path.join(self.DIRECTORY, "pems_files", "private.pem")
        self.PUBLIC_KEY = path.join(self.DIRECTORY, "pems_files", "public.pem")

        # -> data paths.
        self.FOLDER_DIR = path.join(self.DIRECTORY, "me")
        self.DB_DIR = path.join(self.FOLDER_DIR, "db.txt")
        self.PWD_DIR = path.join(self.FOLDER_DIR, "pwd.txt")
        self.PC_DIR = path.join(self.FOLDER_DIR, "pc.txt")
        self.DATA_DIR = path.join(self.FOLDER_DIR, "data.json")

        print("-> Init. variables...")
        self.data = {}
        self.db_data = {}
        self.my_name = ""
        self.pwd_hasher = PasswordHasher(time_cost=10, memory_cost=512000, parallelism=10, hash_len=2056)
        
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

        if not path.exists(self.PWD_DIR):
            raise FileNotFoundError("Password file not found (1) !")

        with open(self.PWD_DIR, "rb") as file:
            encrypted = file.read()

        decrypted = fernet.decrypt(encrypted)

        return decrypted[64:].decode()

    def _get_passcode(self) -> str:
        """Get the passcode from the passcode file."""

        key = self._open_key()
        fernet = Fernet(key)

        with open(self.PC_DIR, "rb") as file:
            encrypted = file.read()

        decrypted = fernet.decrypt(encrypted)
        return decrypted.decode()

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

        key = self._open_key()
        fernet = Fernet(key)

        salt = get_random_bytes(64)
        derive = self.pwd_hasher.hash(password.encode()).encode()
        password = salt + derive

        encrypted = fernet.encrypt(password)

        with open(self.PWD_DIR, "wb") as file:
            file.write(encrypted)

    def _get_parameters_json(self) -> dict:
        """Return the parameter's user from data.json."""

        return self.data.get("parameters")

    def _get_version(self) -> str:
        """Return the current version of the application."""

        return self.data.get("version", "0.0.0")

    def _verify_json_files(self) -> bool:
        """Verify if the data file is here."""

        files = listdir(self.FOLDER_DIR)
        return "data.json" in files and "db.txt" in files

    def _verify_pwd_file(self) -> bool:
        """Verify if the password file is here."""

        files = listdir(self.FOLDER_DIR)
        
        if "pwd.txt" in files:
            pwd = self._open_pwd()

            try:
                self.pwd_hasher.verify(pwd, "")  # if verification fails, it's not empty/
                return False
            except:
                return True

        raise FileNotFoundError("Password file not found (2) !")

    def _check_pwd(self, stored_pwd: str, input_pwd: str) -> bool:
        """Check if the input password matches the stored password."""

        try:
            self.pwd_hasher.verify(stored_pwd, input_pwd)
            return False  # Password is correct
        except:
            return True  # Password is incorrect

    def _verify_keys_files(self) -> bool:
        """Verify if the keys files are here."""

        files = listdir(self.KEY_DIR)
        return "private.pem" in files and "public.pem" in files
    
    def _write_RSA_keys(self, private_key: bytes, public_key: bytes) -> None:
        """Write the RSA keys into files."""

        with open(self.PRIVATE_KEY, "wb") as prv_file:
            prv_file.write(private_key)

        with open(self.PUBLIC_KEY, "wb") as pub_file:
            pub_file.write(public_key)
    
    def _get_RSA_keys(self) -> tuple[bytes, bytes]:
        """Get the RSA set keys from the files."""

        with open(self.PRIVATE_KEY, "rb") as prv_file:
            private_key = prv_file.read()

        with open(self.PUBLIC_KEY, "rb") as pub_file:
            public_key = pub_file.read()

        return private_key, public_key
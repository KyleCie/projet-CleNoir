
# files and directory.
from os import listdir, getcwd, path

# Styling types functions.
from typing import overload, Union

# AES system, RSA system and base64 system.
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from base64 import b64decode, b64encode

from concurrent.futures import ThreadPoolExecutor

# randomness.
from Crypto.Random import get_random_bytes

class rsaSystem:

    def __init__(self) -> None:
        
        # directorys.
        print("-> Creating paths...")
        self.DIRECTORY = getcwd()
        self.FOLDER_DIR = path.join(self.DIRECTORY, "pems_files")
        self.PRIVATE_DIR = path.join(self.FOLDER_DIR, "private.pem")
        self.PUBLIC_DIR = path.join(self.FOLDER_DIR, "public.pem")

        # RSA keys and passphrase.
        print("-> Init. variables...")
        self.public_key = None
        self.private_key = None
        
        # passphrase
        # TODO: better passCode.
        self.passCode = "test"

        # open ( and create ) RSA keys.
        print("-> Checking RSA keys...")
        if not self._verify_keys_files():
            print("--> Keys don't exist ! Creating a set...")
            self._make_RSA_keys()
            print("--> Created.")
        
        print("-> Opening files...")
        self._get_RSA_keys()
        print("-> All done.")

    def _verify_keys_files(self) -> bool:
        """Verify if the keys files are here."""

        files: list[str] = listdir(self.FOLDER_DIR)

        return all(file in files for file in ("private.pem", "public.pem"))

    def _make_RSA_keys(self) -> None:
        """Create and save a new set of RSA keys."""

        instance_key = RSA.generate(2048)
        private_key = instance_key.export_key(  
                                                passphrase=self.passCode, pkcs=8,
                                                protection="scryptAndAES128-CBC",
                                                prot_params={'iteration_count':131072}
                                            )
        
        with open(self.PRIVATE_DIR, "wb") as file:
            file.write(private_key)

        public_key = instance_key.public_key().export_key()

        with open(self.PUBLIC_DIR, "wb") as file:
            file.write(public_key)

    def _get_RSA_keys(self) -> None:
        """Get the RSA set keys from the files."""

        with open(self.PRIVATE_DIR, "rb") as file:
            key = file.read()

        self.private_key = RSA.import_key(key, passphrase=self.passCode)

        with open(self.PUBLIC_DIR, "rb") as file:
            key = file.read()

        self.public_key = RSA.import_key(key)
    
    def _get_public_RSA(self) -> bytes:
        """return the public key."""

        if self.public_key is None:
            raise ValueError("The value of rsa.public_key is None.")

        return self.public_key.export_key()

    def encrypt_message(self, reciever_key: RSA.RsaKey | str) -> tuple[bytes, bytes, bytes]:
        """create a session_key and enc_session_key from the public key: `reciever_key`."""

        if isinstance(reciever_key, str):
            clean_key = RSA.import_key(reciever_key)

        else:
            clean_key = reciever_key

        session_key = get_random_bytes(16)

        cipher_rsa_reciever = PKCS1_OAEP.new(clean_key)
        enc_session_key_reciever = cipher_rsa_reciever.encrypt(session_key)

        cipher_rsa_me = PKCS1_OAEP.new(self.public_key)
        enc_session_key_me = cipher_rsa_me.encrypt(session_key)

        return (session_key, enc_session_key_reciever, enc_session_key_me)

    def encrypt_note(self) -> tuple[bytes, bytes, bytes]:
        """create a session_key and enc_session_key from the public key: `reciever_key`."""

        session_key = get_random_bytes(16)

        cipher_rsa_me = PKCS1_OAEP.new(self.public_key)
        enc_session_key_me = cipher_rsa_me.encrypt(session_key)

        return (session_key, enc_session_key_me)

    def encrypt_notif(self, reciever_key: RSA.RsaKey | str) -> tuple[bytes, bytes]:
        """create a session_key and enc_session_key from the public key: `reciever_key`."""

        if isinstance(reciever_key, str):
            clean_key = RSA.import_key(reciever_key)

        else:
            clean_key = reciever_key

        session_key = get_random_bytes(16)

        cipher_rsa_reciever = PKCS1_OAEP.new(clean_key)
        enc_session_key_reciever = cipher_rsa_reciever.encrypt(session_key)

        return (session_key, enc_session_key_reciever)

    def decrypt(self, enc_session_key: bytes) -> bytes:
        """retrieve session_key from enc_session_key with the private key. `enc_session_key`."""

        if self.private_key is None:
            raise ValueError("The value of rsa.public_key is None.")

        cipher_rsa = PKCS1_OAEP.new(self.private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        return session_key

class aesSystem:

    def __init__(self) -> None:
        print("-> All done.")

    def encrypt(self, data: bytes, session_key: bytes) -> tuple[bytes, bytes, bytes]:
        """encrypt data with session_key as the key for the AES system and return the `nonce`, `cipher_text` and `tag`."""

        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        cipher_text, tag = cipher_aes.encrypt_and_digest(data)

        return (cipher_aes.nonce, cipher_text, tag)

    def decrypt(self, session_key: bytes, nonce: bytes, tag: bytes, cipher_text: bytes) -> bytes:
        """decrypt data with `session_key` as the key, `nonce`, `tag` and `ciphertext` for the AES system and return original data."""

        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(cipher_text, tag)

        return data

class encryption:

    def __init__(self) -> None:
        
        # encryption system.
        print("Starting RSA system...")
        self.rsa = rsaSystem()
        print("Starting AES system...")
        self.aes = aesSystem()
        print("Encryption system done.")

    @overload # str handler
    def encrypt(self, data: str, public_key: str) -> str: ...

    @overload # bytes handler
    def encrypt(self, data: bytes, public_key: str) -> bytes: ...
    
    def encrypt(self, data: Union[str, bytes], public_key: str) -> Union[str, bytes]:
        """encrypt the data to bytes with the encryption method."""

        if isinstance(data, str):
            clean_data = data.encode('utf-8')
        else:
            clean_data = data
        
        if not self.rsa.public_key:
            raise ValueError("The value of rsa.public_key is None.")

        session_key, enc_session_key_re, enc_session_key_me  = self.rsa.encrypt_message(public_key)
        nonce, cipher_text, tag = self.aes.encrypt(clean_data, session_key)
        result = enc_session_key_re + enc_session_key_me + nonce + tag + cipher_text    # crypted key for receiver + me, ...

        if isinstance(data, str):
            return b64encode(result).decode()
        return result
    
    def encrypt_note(self, data: str) -> str:
        """encrypt the data with the encryption method."""

        if isinstance(data, str):
            clean_data = data.encode('utf-8')
        else:
            clean_data = data

        if not self.rsa.public_key:
            raise ValueError("The value of rsa.public_key is None.")

        session_key, enc_session_key_me  = self.rsa.encrypt_note()
        nonce, cipher_text, tag = self.aes.encrypt(clean_data, session_key)
        result = enc_session_key_me + nonce + tag + cipher_text

        if isinstance(data, str):
            return b64encode(result).decode()
        return result
    
    def encrypt_notif(self, data: str, key_reciever) -> str:
        """encrypt the data with the encryption method."""

        if isinstance(data, str):
            clean_data = data.encode('utf-8')
        else:
            clean_data = data

        if not key_reciever:
            raise ValueError("The value of key_reciever is None.")

        session_key, enc_session_key_re  = self.rsa.encrypt_notif(key_reciever)
        nonce, cipher_text, tag = self.aes.encrypt(clean_data, session_key)
        result = enc_session_key_re + nonce + tag + cipher_text

        if isinstance(data, str):
            return b64encode(result).decode()
        return result

    @overload # str handler
    def decrypt(self, data: str) -> str: ...
    
    @overload # bytes handler
    def decrypt(self, data: bytes) -> bytes: ...

    def decrypt(self, data: Union[str, bytes]) -> Union[str, bytes]:
        """encrypt the data to str with the encryption method."""
        
        if isinstance(data, str):
            clean_data = b64decode(data)
        else:
            clean_data = data

        if len(clean_data) < 288:
            raise ValueError(f"The variable clean_data is less than 288 bytes, -> {len(clean_data)}.")

        es_key = clean_data[0:256]    # 2048 bits enc_session_key
        nonce = clean_data[256:272]   # 16 bits nonce
        tag = clean_data[272:288]     # 16 bits tag
        c_text = clean_data[288:]     # data

        s_key = self.rsa.decrypt(es_key)
        res_data = self.aes.decrypt(s_key, nonce, tag, c_text)

        if isinstance(data, str):
            return res_data.decode()
        
        return res_data

    def decrypt_messages(self, data: list[dict], me: str) -> list[dict]:
        def worker(msg):
            from_who = msg.get("from")
            raw_data = msg.get("data")
            clean_data = b64decode(raw_data) if isinstance(raw_data, str) else raw_data

            if len(clean_data) < 512:
                return None

            if from_who == me:
                segment = clean_data[256:]
            else:
                segment = clean_data[0:256] + clean_data[512:]

            plaintext = self.decrypt(segment)

            return {
                "from": from_who,
                "data": plaintext.decode(errors="replace"),
                "timestamp": msg.get("timestamp")
            }

        with ThreadPoolExecutor() as ex:
            return [r for r in ex.map(worker, data) if r]

    def decrypt_notes_myspace(self, data: list[dict]) -> list[dict]:
        """Return a decrypted list of the data `data`."""

        clean_datas = []

        for note in data:
            note_data = note.get("data")

            if isinstance(note_data, str):
                clean_note = b64decode(note_data)
            else:
                clean_note = note_data

            clean_datas.append({
                "data": self.decrypt(clean_note).decode(),
                "timestamp": note.get("timestamp")
            })

        return clean_datas

    def decrypt_notifications(self, data: list[dict]) -> list[dict]:
        """Return a decrypted list of the data `data`."""

        if data is None:
            return None

        clean_datas = []

        for notif in data:
            note_data = notif.get("data")

            if isinstance(note_data, str):
                clean_note = b64decode(note_data)
            else:
                clean_note = note_data

            clean_datas.append({
                "from": notif.get("from"),
                "data": self.decrypt(clean_note).decode(),
                "timestamp":notif.get("timestamp")
            })

        return clean_datas

    def public_key_RSA(self) -> bytes:
        """Get the public key from the RSA system."""

        return self.rsa._get_public_RSA()
    
    def reset_keys(self, sure: bool = False) -> None:
        """Reset the set keys for the RSA system, need to put `sure` to True."""

        if sure:
            self.rsa._make_RSA_keys()
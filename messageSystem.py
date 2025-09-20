
# get the class type
from dataFileSystem import file

# firebase messaging handler.
import pyrebase

# timestamp
from time import time
from datetime import datetime

# Styling types functions.
from typing import overload, Union

class dataSystem:

    def __init__(self, dataFileHandler: file) -> None:

        print("-> Init. variables...")
        self.dataFile = dataFileHandler
        # data from the file.
        self.data: dict = {}
        # the pseudo of the user.
        self.my_name: str = ""

        # database informations.
        # TODO: put this below in a json file and use an encryption system. (For more security.)
        self.db_infos = {
            "apiKey": "AIzaSyDscH9QK75IX6PlwfWN6MFg5xISWd0ckcU",
            "authDomain": "aesrsa-db.firebaseapp.com",
            "databaseURL": "https://aesrsa-db-default-rtdb.europe-west1.firebasedatabase.app",
            "projectId": "aesrsa-db",
            "storageBucket": "aesrsa-db.firebasestorage.app",
            "messagingSenderId": "273047937386",
            "appId": "1:273047937386:web:ff3f776d80ed0d73434513"
        }

        # database instance.
        self.database = None
        # firebase instance.
        self.firebase = None
        # PublicKeys list.
        self.PublicKeys = []

        print("-> Checking files...")
        if self.dataFile._verify_json_files():
            print("-> Getting data...")
            self.data, self.my_name = self.dataFile._get_data_json()
            print("-> Connecting to database...")
            self._connect_to_db()
        else:
            exit()
    
    def _connect_to_db(self) -> None:
        """Create an instance database."""

        self.firebase = pyrebase.initialize_app(self.db_infos)
        self.database = self.firebase.database()

        self.PublicKeys = self._get_RSA_keys()

    def _get_RSA_keys(self) -> list[dict]:
        """Get the public RSA keys from database."""

        if not self.database:
            exit()

        rsa_messages = self.database.child("rsa-keys").get()
        rsa_messages = rsa_messages.each()

        messages: list[dict] = []

        if rsa_messages:

            for rsa in rsa_messages:
                messages.append(rsa.val())

        return messages
    
    def _refresh(self) -> None:
        """Refresh the public keys."""
        
        self.PublicKeys = self._get_RSA_keys()

    def _send(self, data: dict, database: str, is_msg: bool = False) -> None:
        """Send a data `data` to the child database named `database`"""

        if not self.database:
            exit()

        if database == "rsa-keys":
            msg_link = self.data.get("rsa_msg", "unknown")
            
            if msg_link == "" or msg_link == "unknown":
                result = self.database.child(database).push(data)
                self.data["rsa_msg"] = result["name"]
                self.dataFile._store_data_json(self.data)

            else:
                self.database.child(database).child(msg_link).set(data)
            
            return

        if is_msg:
            self.database.child(database).child("messages").push(data)
            return

        self.database.child(database).child("messages").push(data)

    @overload # last_one handler.
    def  _get_data_from_database(self, database: str, last_one: bool = True) -> str: ...

    @overload # not last_one handler.
    def  _get_data_from_database(self, database: str, last_one: bool = False) -> list[dict]: ...

    def _get_data_from_database(self, database: str, last_one: bool = Union[False, True]) -> Union[list[dict], str]:
        """Return the raw data from database `database`."""

        if not self.database:
            exit()

        messages = self.database.child(database).child("messages").get()
        messages = messages.each()

        if messages is None:
            return []

        if not last_one:

            list_msg: list[dict] = []

            if messages:
                for msg in messages:
                    list_msg.append(msg.val())

            return list_msg
        
        return [messages[-1].val()]
    
    def _data_to_msg(self, data: list[dict]) -> list[tuple[str, str, str]]:
        """Return a printable data from `data`."""

        list_msg: list[tuple[str, str]] = []

        for msg in data:
            dt = datetime.fromtimestamp(msg.get("timestamp"))
            dt = dt.strftime("%d/%m/%Y %H:%M:%S")
            list_msg.append((f"[{dt}]", f"[{msg.get("from")}]", f"{msg.get("data")}"))

        if len(list_msg) != 0:
            return list_msg

        return ["NO MESSAGES"]

    def _get_contacts(self) -> list[str]:
        """Return a list of contacts from the database PublicKey"""

        clean_datas = []

        for msg in self.PublicKeys:
            clean_datas.append(msg["name"])

        return clean_datas
    
    def _get_publicKey_from(self, who: str) -> str:
        """Return the PublicKey from ` who`."""

        for keys in self.PublicKeys:
            if keys["name"] == who:
                return keys["key"]
        
        return ""

    def _is_database_exist(self, database: str) -> bool:
        """Return a bool if the database `database` exist."""

        return self.database.child(database).get().val() is not None
    
    def _find_database(self, with_user: str) -> str:
        """Return a database name where it is a conversation with `with_user`."""

        db_name1 = f"conv_{self.my_name}_{with_user}"
        db_name2 = f"conv_{with_user}_{self.my_name}"

        if self._is_database_exist(db_name1):
            return db_name1
        
        if self._is_database_exist(db_name2):
            return db_name2
        
        self.database.child(db_name1).set({"auth": [self.my_name, with_user], "messages": {}})
        return db_name1

    def _create_dict_data(self, data: str | bytes, for_who: str | None = None) -> dict:
        """Create an dict to be send in database."""

        if isinstance(data, bytes):
            clean_data = data.decode('utf-8')
        
        else:
            clean_data = data

        dict_message: dict = {
            "from": self.my_name,
            "data": clean_data,
            "timestamp": time()
        }

        if for_who:
            dict_message["to"] = for_who

        return dict_message

    def _create_dict_PublicKey(self, key: str | bytes) -> dict:
        """Create an dict for `PublicKey` to be send in database."""

        if isinstance(key, bytes):
            clean_key = key.decode('utf-8')
        else:
            clean_key = key

        dict_PublicKey: dict = {
            "name": self.my_name,
            "key": clean_key
        }

        return dict_PublicKey

class message:

    def __init__(self, dataFileHandler) -> None:
        
        print("Starting message and database system...")
        self.data = dataSystem(dataFileHandler)
        print("Message and database system done.")

    def refresh(self) -> None:
        """Refresh the system."""

        self.data._refresh()
    
    def send(self, msg: str | bytes, database: str) -> None:
        """Send a message `msg` in `message` database."""

        dict_msg = self.data._create_dict_data(msg)
        self.data._send(data=dict_msg, database=database, is_msg=True)

    def sendPublicKey(self, public_key: bytes) -> None:
        """Send PublicKey `public_key` in `rsa_keys` database."""

        dict_PublicKey = self.data._create_dict_PublicKey(public_key)
        self.data._send(data=dict_PublicKey, database="rsa-keys")

    def get_contact(self) -> list[str]:
        """Return a list of persons (contact) ."""

        return self.data._get_contacts()
    
    def get_PublicKey_from(self, user: str) -> str:
        """Return the public key of `user` else '' if not found."""

        return self.data._get_publicKey_from(user)
    
    def get_my_pseudo(self) -> str:
        """Return the pseudo of the user."""

        return self.data.my_name
    
    def find_conversation(self, user: str) -> str:
        """Find the name of the database from user, and create one if not created."""

        return self.data._find_database(with_user=user)

    def find_messages(self, database: str) -> list[dict]:
        """Return all the messages from a database `database`."""

        return self.data._get_data_from_database(database, last_one=False)
    
    def find_last_messages(self, database: str) -> str:
        """Return the last message from a database `database`."""

        return self.data._get_data_from_database(database, True)

    def transform_messages(self, messages: list[dict]) -> list[tuple[str, str, str]]:
        """Return a printable list of messages `messages` (NEED TO BE DECRYPTED BEFORE)."""

        return self.data._data_to_msg(messages)
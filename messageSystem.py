
# get the class type
from dataFileSystem import file
from encryptionSystem import encryption
from TerminalSystem import terminal

# firebase messaging handler.
import pyrebase

# timestamp
from time import time
from datetime import datetime

class dataSystem:

    def __init__(self, dataFileHandler: file, encr: encryption, printer: terminal) -> None:

        print("-> Init. variables...")
        # Instances.
        self.dataFile = dataFileHandler
        self.encr = encr
        self.printer = printer
        # data from the file.
        self.data: dict = {}
        # the pseudo of the user.
        self.my_name: str = ""

        # database informations.
        self.db_infos = self.dataFile._get_db_infos()

        # database instance.
        self.database = None
        # firebase instance.
        self.firebase = None
        # stream messages instance.
        self.msg_stream = None
        # PublicKeys list.
        self.PublicKeys = []

        print("-> Checking files...")
        if self.dataFile._verify_json_files():
            print("-> Getting data...")
            self.data, self.my_name = self.dataFile._get_data_json()
            print("-> Connecting to database...")
            self._connect_to_db()
        else:
            raise FileNotFoundError("the infos files don't exist !")
    
    def _connect_to_db(self) -> None:
        """Create an instance database."""

        self.firebase = pyrebase.initialize_app(self.db_infos)
        self.database = self.firebase.database()

        self.PublicKeys = self._get_RSA_keys()

    def _get_RSA_keys(self) -> list[dict]:
        """Get the public RSA keys from database."""

        if not self.database:
            raise ValueError("The value of database is None.")

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

    def __stream_messages(self, message) -> None:
        """Add automatically the message in the terminal."""        
        
        if message["data"] is None: # ignore if don't data.
            return

        msg_data = message["data"] # get the data.

        # if one only msg.
        if isinstance(msg_data, dict) and "data" in msg_data:
            conversation = [msg_data]
        else:
            # multiples.
            conversation = []
            if isinstance(msg_data, dict):
                for key, val in msg_data.items():
                    if isinstance(val, dict):
                        conversation.append(val)

        conversation = self.encr.decrypt_messages(conversation, self.my_name)
        conversation = self._data_to_msg(conversation)

        self.printer.print_messages(conversation) # show on screen.

    def _send_note(self, data: dict, myself_name: str) -> None:
        """Send data `data` to the child database."""

        if not self.database:
            raise ValueError("The value of database is None.")

        self.database.child(self.my_name).child("myspace").child(myself_name).push(data)

    def _send(self, data: dict, database: str, is_msg: bool = False) -> None:
        """Send a data `data` to the child database named `database`"""

        if not self.database:
            raise ValueError("The value of database is None.")

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
            self.database.child("conversations").child(database).child("messages").push(data)
            return

        self.database.child(database).child("messages").push(data)
    
    def _send_notif(self, receiver: str, data: dict) -> None:
        """Send a notif to the user `receiver` from database `database`."""

        if not self.database:
            raise ValueError("The value of database is None.")
        
        self.database.child(receiver).child("notifications").push(data)

    def _get_data_from_myspace(self, name: str) -> list[dict]:
        """Return the raw data from myspace `myspace`."""

        if not self.database:
            raise ValueError("The value of database is None.")

        notes = self.database.child(self.my_name).child("myspace").child(name).get()
        notes = notes.each()

        if notes is None:
            return []

        list_notes: list[dict] = []

        for note in notes:
            list_notes.append(note.val())

        return list_notes

    def _get_data_from_database(self, database: str, is_msg: bool = False, stream: bool = False) -> list[dict]:
        """Return the raw data from database `database`."""

        if not self.database:
            raise ValueError("The value of database is None.")

        if is_msg:
            messages = self.database.child("conversations").child(database).child("messages").get()
            messages = messages.each()

        else:
            messages = self.database.child(database).child("messages").get()
            messages = messages.each()

        if messages is None:
            return []

        list_msg: list[dict] = []

        for msg in messages:
            list_msg.append(msg.val())

        if stream:
            self.msg_stream = self.database.child("conversations").child(database).child("messages").stream(self.__stream_messages)

        return list_msg
    
    def _del_stream(self) -> None:
        """Delete stream instance."""

        if self.msg_stream:
            self.msg_stream.close()
            self.msg_stream = None

    def _data_to_notes(self, data: list[dict]) -> list[tuple[str, str]]:
        """Return a printable data from `data`."""

        list_notes: list[tuple[str, str]] = []

        for note in data:
            dt = datetime.fromtimestamp(note.get("timestamp"))
            dt = dt.strftime("%d/%m/%Y %H:%M:%S")
            list_notes.append((f"[{dt}]", f"{note.get("data")}"))

        if list_notes != []:
            return list_notes
        
        return ["NO NOTES"]

    def _data_to_msg(self, data: list[dict]) -> list[tuple[str, str, str]]:
        """Return a printable data from `data`."""

        list_msg: list[tuple[str, str, str]] = []

        for msg in data:
            dt = datetime.fromtimestamp(msg.get("timestamp"))
            dt = dt.strftime("%d/%m/%Y %H:%M:%S")
            list_msg.append((f"[{dt}]", f"[{msg.get("from")}]", f"{msg.get("data")}"))

        if list_msg != []:
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

    def _is_database_exist(self, database: str, is_msg: bool = False) -> bool:
        """Return a bool if the database `database` exist."""

        if is_msg:
            return self.database.child("conversations").child(database).get().val() is not None
        
        return self.database.child(database).get().val() is not None
    
    def _find_myspace(self) -> None:
        """Create or find the myspace's user."""

        myspace = self.database.child(self.my_name).get().val()

        if myspace is None:
            self.database.child(self.my_name).set({"auth": [self.my_name]})

    def _find_database(self, with_user: str) -> str:
        """Return a database name where it is a conversation with `with_user`."""

        db_name1 = f"conv_{self.my_name}_{with_user}"
        db_name2 = f"conv_{with_user}_{self.my_name}"

        if self._is_database_exist(db_name1, True):
            return db_name1
        
        if self._is_database_exist(db_name2, True):
            return db_name2
        
        self.database.child("conversations").child(db_name1).set({"auth": [self.my_name, with_user], "messages": {}})
        return db_name1
    
    def _get_notifications(self) -> list[tuple[str, str, str]]:
        """Return the user's notifications."""

        notifs = self.database.child(self.my_name).child("notifications").get()
        notifs = notifs.each()

        if notifs is None:
            return ["NO NOTIFS"]
        
        list_notifs: list[tuple[str, str, str]] = []

        for notif in notifs:
            notif = notif.val()
            dt = datetime.fromtimestamp(notif.get("timestamp"))
            dt = dt.strftime("%d/%m/%Y %H:%M:%S")
            list_notifs.append((f"[{dt}]", f"[{notif.get("from")}]", f"{notif.get("data")}"))

        return list_notifs

    def _delete_notifications(self) -> None:
        """Delete notifications."""

        self.database.child(self.my_name).child("notifications").set({})

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

    def __init__(self, dataFileHandler, Encryption, Printer: terminal) -> None:
        
        print("Starting message and database system...")
        self.data = dataSystem(dataFileHandler, Encryption, Printer)
        print("Message and database system done.")

    def refresh(self) -> None:
        """Refresh the system."""

        self.data._refresh()
    
    def send(self, msg: str | bytes, database: str, receiver: str) -> None:
        """Send a message `msg` in `message` database."""

        dict_msg = self.data._create_dict_data(msg)
        dict_notif = self.data._create_dict_data("New message")
        self.data._send(data=dict_msg, database=database, is_msg=True)
        self.data._send_notif(receiver, dict_notif)

    def send_note(self, note: str, myself_name: str) -> None:
        """Send a note `note` in myself `myself_name`."""

        dict_msg = self.data._create_dict_data(note)
        self.data._send_note(dict_msg, myself_name)

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
    
    def find_myspace(self) -> None:
        """Find the user's myspace `myspace_name`."""

        self.data._find_myspace()

    def find_notes_myspace(self, myspace_name: str) -> list[dict]:
        """Return all the messages from a myspace `myspace`.""" 

        return self.data._get_data_from_myspace(myspace_name)

    def find_conversation(self, user: str) -> str:
        """Find the name of the database from user, and create one if not created."""

        return self.data._find_database(with_user=user)

    def delete_stream(self) -> None:
        """Delete the instance stream to stop the automatic refresh messages."""

        self.data._del_stream()

    def find_messages(self, database: str, stream: bool = False) -> list[dict]:
        """Return all the messages from a database `database`."""

        return self.data._get_data_from_database(database, is_msg=True, stream = stream)

    def transform_messages(self, messages: list[dict]) -> list[tuple[str, str, str]]:
        """Return a printable list of messages `messages` (NEED TO BE DECRYPTED BEFORE)."""

        return self.data._data_to_msg(messages)
    
    def transform_notes(self, notes: list[dict]) -> list[tuple[str, str]]:
        """Return a printable list of notes `notes` (NEED TO BE DECRYPTED BEFORE)."""

        return self.data._data_to_notes(notes)
    
    def get_notifications(self) -> list[tuple[str, str, str]]:
        """Return a list of the user notifications."""

        return self.data._get_notifications()
    
    def delete_notifications(self) -> None:
        """Delete the user's notifications."""

        self.data._delete_notifications()

# Styling functions calls.
from typing import Callable, Literal

# To clear the terminal.
from os import system
from sys import stdout

class commandSystem:
    def __init__(self) -> None:
        pass

    def _clean_command(self, command: str, length_words: int = 1, start_pos: int = 0) -> str:
        """return the `command` with `length_word` words."""

        words = command.strip().split()

        if length_words == -1:
            return " ".join(words[start_pos:])
        else:
            return " ".join(words[start_pos:start_pos + length_words])
    
    def _to_tuple_command(self, command: str) -> tuple[str, ...]:
        """return a tuple of words from `command`."""

        return tuple(command.strip().split())

    def _clear_terminal(self, *args) -> None:
        """Clear the terminal."""

        system("cls||clear")

    def _clear_line_terminal(self, *args) -> None:
        """Clear the last line in terminal."""

        stdout.write("\033[F\033[K")
        stdout.flush()

    def _test(self, *args) -> None:
        """test command!"""

        print("test !")

    def _myself(self, *args) -> Literal["SAY_PSEUDO"]:
        """Return a command to the main to get your pseudo."""

        return "SAY_PSEUDO"
  
    def _say(self, command: str, *args):
        """Print the thing to say from the command."""

        to_say: str = self._clean_command(command=command, length_words=-1, start_pos=1)
        print(to_say)

    def _find_contacts(self, *args) -> Literal["FIND_CONTACTS"]:
        """Return a command to the main to search contacts."""

        return "FIND_CONTACTS"
  
    def _refresh(self, *args) -> Literal["REFRESH"]:
        """Return a command to the main to refresh."""

        return "REFRESH"
    
    def _exit(self, *args) -> Literal["EXIT"]:
        """Return a command to the main to exit the program."""

        return "EXIT"
    
    def _myspace_system(self, command: str, *args) -> tuple[Literal["MYSPACE"], str]:
        """Return a command to the main to access the myspace's user."""
        
        clean_cmd = self._clean_command(command, -1, 1)
        clean_cmd = self._to_tuple_command(clean_cmd)

        if len(clean_cmd) != 0:
            
            return ("MYSPACE", " ".join(clean_cmd))
        
        myspace_name = input("Myspace name : ")

        return ("MYSPACE", myspace_name)

    def _change_system(self, command: str, *args) -> tuple[str, ...] | None:
        """Return a command to the main to change parameter's user."""

        clean_cmd = self._clean_command(command, -1, 1)
        clean_cmd = self._to_tuple_command(clean_cmd)

        if len(clean_cmd) != 0:

            match clean_cmd[0]:

                case "message":
                    
                    if len(clean_cmd) == 1:
                        self._error_need_parameters("change", "WHAT_IN_MESSAGE")
                        return

                    if clean_cmd[1] == "color":
                        if clean_cmd[-1] != "color":

                            return ("CHANGE_MSG_COLOR", clean_cmd[2].upper(), clean_cmd[3].upper(), clean_cmd[4].upper())

                        print("Colors available : WHITE, BLACK, YELLOW, GREEN, RED, PURPLE.")
                        color1 = input("Color for informations (empty = don't change) : ").upper()
                        color2 = input("Color for name (empty = don't change) : ").upper()
                        color3 = input("Color for content (empty = don't change) : ").upper()

                        return ("CHANGE_MSG_COLOR", color1, color2, color3)

                case "note":
                    
                    if len(clean_cmd) == 1:
                        self._error_need_parameters("change", "WHAT_IN_NOTE")
                        return

                    if clean_cmd[1] == "color":
                        if clean_cmd[-1] != "color":

                            return ("CHANGE_MSG_COLOR", clean_cmd[2].upper(), clean_cmd[3].upper())

                        print("Colors available : WHITE, BLACK, YELLOW, GREEN, RED, PURPLE.")
                        color1 = input("Color for informations (empty = don't change) : ").upper()
                        color2 = input("Color for content (empty = don't change) : ").upper()

                        return ("CHANGE_NOTES_COLOR", color1, color2)

                case _:
                    self._error_not_found(f"change -> {clean_cmd[0]}")
                    return

        self._error_need_parameters("change", "WHAT_TO_CHANGE")
        return

    def _reset_system(self, command: str, *args) -> str | None:
        """The reset system, return a command to the main."""

        clean_cmd = self._clean_command(command, -1, 1)
        clean_cmd = self._to_tuple_command(clean_cmd)

        if len(clean_cmd) != 0:

            match clean_cmd[0]:

                case "rsa":
                    if clean_cmd[-1] == "-y":
                        return "RESET_RSA_KEYS"
                    
                    accept = input("ALL THE MESSAGES WILL BE ERASED (BECAUSE YOU ARE CHANGING KEYS) !!!\n" \
                                    "Are you sure to do this (y/n) ? ")
                    
                    if accept.lower() in ("y", "yes"):
                        return "RESET_RSA_KEYS"
                    
                    print("-> Command canceled <-")
                    return
        
                case _:
                    self._error_not_found(f"reset -> {clean_cmd[0]}")
                    return

        self._error_need_parameters(command, "WHAT_TO_RESET")
  
    def _connect_conversation(self, command: str, *args) -> tuple | None:
        """The system to connect to a conversation (database), return a command to the main."""

        to_who = self._clean_command(command, -1, 1)
        to_who = self._to_tuple_command(to_who)

        if len(to_who) > 1:
            print(to_who)
            self._error_not_found(f"connect -> {to_who[1:]}")
            return
    
        if len(to_who) == 0:
            self._error_need_parameters("connect", "TO_WHO")
            return
    
        return ("CONNECT_CONV", to_who[0])

    def _error_need_parameters(self, command: str, *args) -> None:
        """When a command need a parameters."""

        print(f"Error with '{command}' : need parameters : {args} .")

    def _error_not_found(self, command: str, *args) -> None:
        """When no commands found for `command`."""

        print(f"Error with '{command}' : command not found.")

    def _error_systemCommand_not_found(self, command: str, *args) -> None:
        """When the system do a wrong call. (weird!)"""

        print(f"ERROR !!! System call {command} is not found (have to exit) !")
        exit()

class interpreter:
    def __init__(self) -> None:

        print("Starting interpreter system...")
        self.commands = commandSystem()

        print("-> Init. variables...")
        self.traduct_commands: dict[str, str] = {
            "t": "test",
            "c": "contact",
            "m": "myself",
            "pseudo": "myself",
            "contacts": "contact",
            "clr": "clear",
            "rst": "reset",
            "r": "refresh"
        }

        self.auth_commands: dict[str, Callable] = {
            "test": self.commands._test,
            "myself": self.commands._myself,
            "contact": self.commands._find_contacts,
            "clear": self.commands._clear_terminal,
            "say": self.commands._say,
            "reset": self.commands._reset_system,
            "connect": self.commands._connect_conversation,
            "clearline": self.commands._clear_line_terminal,
            "refresh": self.commands._refresh,
            "change": self.commands._change_system,
            "myspace": self.commands._myspace_system,
            "exit": self.commands._exit
        }

        print("Interpreter system done.")

    def find_command(self, command: str) -> Callable:
        """Return a usable command who correspond to `command` else return None."""

        clean_cmd: str = self.commands._clean_command(command.lower())
        clean_cmd = self.traduct_commands.get(clean_cmd, clean_cmd)
        cmd: Callable = self.auth_commands.get(clean_cmd, self.commands._error_not_found)

        return cmd

    def run(self, command: str) -> None:
        """Run a command from the system, NOT USER."""

        cmd: Callable = self.auth_commands.get(command,
                                            self.commands._error_systemCommand_not_found)
        cmd(command)
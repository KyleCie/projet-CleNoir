
# for class type.
from dataFileSystem import file

# color system.
from colorama import Fore, Style

class PrintSystem:
    def __init__(self, messages_parameters: file):

        print("-> Getting parameters...")

        self.params = messages_parameters._get_parameters_json()

        print("-> Init. variables...")

        self.colors: dict[str, str] = {
            "WHITE": Fore.WHITE,
            "BLACK": Fore.BLACK,
            "YELLOW": Fore.YELLOW,
            "GREEN": Fore.GREEN,
            "RED": Fore.RED,
            "PURPLE": Fore.MAGENTA,
        }

        self.key_colors = self.colors.keys()

        self.info_color = self.params.get("date_info_color", "WHITE")
        self.name_color = self.params.get("name_info_color", "WHITE")
        self.content_color = self.params.get("content_info_color", "WHITE")

        self.info_color = self.colors.get(self.info_color)
        self.name_color = self.colors.get(self.name_color)
        self.content_color = self.colors.get(self.content_color)

    def _change_msg_colors(self, colors: tuple[str, str, str]) -> None:
        """Change messages colors."""

        self.info_color = self.colors.get(colors[0], self.info_color)
        self.name_color = self.colors.get(colors[1], self.name_color)
        self.content_color = self.colors.get(colors[2], self.content_color)

    def _print_messages(self, messages: list[tuple[str, str, str]]) -> None:
        """Print in the terminal the messages."""

        for msg in messages[:-1]:
            print(f"{self.info_color}{msg[0]}{self.name_color}{msg[1]} {self.content_color}{msg[2]}")
        
        print(f"{self.info_color}{messages[-1][0]}{self.name_color}{messages[-1][1]} {self.content_color}{messages[-1][2]}{Style.RESET_ALL}")

class terminal:
    def __init__(self, messages_parameters: file):
        
        print("Starting printer and terminal system...")
        self.print = PrintSystem(messages_parameters)
        print("Printer and terminal system done.")

    def print_messages(self, messages: list[tuple[str, str, str]]) -> None:
        """Print in the terminal the messages with the parameter's user."""

        self.print._print_messages(messages)

    def change_messages_colors(self, colors: tuple[str, str, str]) -> None:
        """Change parameters for messages colors."""

        self.print._change_msg_colors(colors)
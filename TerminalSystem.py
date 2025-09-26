
# for class type.
from dataFileSystem import file

# color system.
from colorama import Fore, Style
from prompt_toolkit import print_formatted_text, ANSI

class PrintSystem:
    def __init__(self, messages_parameters: file):

        print("-> Getting parameters...")

        self.file = messages_parameters
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

        self.note_info_color = self.params.get("note_info_color", "WHITE")
        self.note_content_color =self.params.get("note_content_color", "WHITE")

        self.note_info_color = self.colors.get(self.note_info_color)
        self.note_content_color = self.colors.get(self.note_content_color)

        self.notif_info_color = self.params.get("notif_info_color", "WHITE")
        self.notif_name_color = self.params.get("notif_name_color", "WHITE")
        self.notif_content_color = self.params.get("notif_content_color", "WHITE")

        self.notif_info_color = self.colors.get(self.notif_info_color)
        self.notif_name_color = self.colors.get(self.notif_name_color)
        self.notif_content_color = self.colors.get(self.notif_content_color)

    def _change_msg_colors(self, colors: tuple[str, str, str]) -> None:
        """Change messages colors."""

        self.info_color = self.colors.get(colors[0], self.info_color)
        self.name_color = self.colors.get(colors[1], self.name_color)
        self.content_color = self.colors.get(colors[2], self.content_color)

    def _change_notes_colors(self, colors: tuple[str, str]) -> None:
        """Change notes colors."""

        self.note_info_color = self.colors.get(colors[0], self.note_info_color)
        self.note_content_color = self.colors.get(colors[1], self.note_content_color)

    def change_notifs_colors(self, colors: tuple[str, str, str]) -> None:
        """Change notifs colors."""

        self.notif_info_color = self.colors.get(colors[0], self.notif_info_color)
        self.notif_notif_color = self.colors.get(colors[1], self.notif_name_color)
        self.notif_content_color = self.colors.get(colors[2], self.notif_content_color)

    def _print_notes(self, notes: list[tuple[str, str]]) -> None:
        """Print in the terminal the notes."""

        if notes == ["NO NOTES"]:
            print(f"{self.note_info_color}NO NOTES{Style.RESET_ALL}")
            return
        
        for note in notes[:-1]:
            print(f"{self.note_info_color}{note[0]} {self.note_content_color}{note[1]}")

        print(f"{self.note_info_color}{notes[-1][0]} {self.note_content_color}{notes[-1][1]}{Style.RESET_ALL}")

    def _print_messages(self, messages: list[tuple[str, str, str]]) -> None:
        """Print in the terminal the messages."""

        if messages == ["NO MESSAGES"]:
            print_formatted_text(ANSI(f"{self.info_color}NO MESSAGES{Style.RESET_ALL}"))
            return

        for msg in messages[:-1]:
            print_formatted_text(ANSI(f"{self.info_color}{msg[0]}{self.name_color}{msg[1]} {self.content_color}{msg[2]}"))
        
        print_formatted_text(ANSI(f"{self.info_color}{messages[-1][0]}{self.name_color}{messages[-1][1]} {self.content_color}{messages[-1][2]}"))

    def _print_notifs(self, notifs: list[tuple[str, str, str]]) -> None:
        """Print in the terminal the notifs."""

        if notifs == ["NO NOTIFS"]:
            print(f"{self.notif_info_color}NO NOTIFS{Style.RESET_ALL}")
            return

        for notif in notifs[:-1]:
            print(f"{self.notif_info_color}{notif[0]}{self.notif_name_color}{notif[1]} {self.notif_content_color}{notif[2]}")

        print(f"{self.notif_info_color}{notifs[-1][0]}{self.notif_name_color}{notifs[-1][1]} {self.notif_content_color}{notifs[-1][2]}{Style.RESET_ALL}")

    def _save_colors(self) -> None:
        """Save the colors."""

        colors_list = [self.info_color, self.name_color, self.content_color,
                        self.note_info_color, self.note_content_color,
                        self.notif_info_color, self.notif_name_color, self.notif_content_color]
        
        clean_colors = []

        for color in colors_list:

            clean_color = next((k for k, v in self.colors.items() if v == color), None)
            clean_colors.append(clean_color)

        self.file._save_colors(clean_colors)

class terminal:
    def __init__(self, messages_parameters: file):
        
        print("Starting printer and terminal system...")
        self.print = PrintSystem(messages_parameters)
        print("Printer and terminal system done.")

    def print_notes(self, notes: list[tuple[str, str]]) -> None:
        """Print in the terminal the notes with the parameter's user."""

        self.print._print_notes(notes)

    def print_messages(self, messages: list[tuple[str, str, str]]) -> None:
        """Print in the terminal the messages with the parameter's user."""

        self.print._print_messages(messages)

    def print_notifications(self, notifications: list[tuple[str, str, str]]) -> None:
        """Print in the terminal the notifications with the parameter's user."""

        self.print._print_notifs(notifications)

    def change_notes_colors(self, colors: tuple[str, str]) -> None:
        """Change parameters for notes colors."""

        self.print._change_notes_colors(colors)

    def change_messages_colors(self, colors: tuple[str, str, str]) -> None:
        """Change parameters for messages colors."""

        self.print._change_msg_colors(colors)

    def change_notifications_colors(self, colors: tuple[str, str, str]) -> None:
        """Change parameters for notifications colors."""

        self.print.change_notifs_colors(colors)

    def save_colors(self) -> None:
        """Return the colors parameters to save."""

        self.print._save_colors()
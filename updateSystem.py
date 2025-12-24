from os import remove
import logging
from datetime import datetime

# for finishing updates.
from subprocess import Popen
from sys import executable
from os import environ, path, getcwd
from pathlib import Path

class UpdateSystem:
    def __init__(self, message_system, file_handler) -> None:
        self.message_system = message_system
        self.file_handler = file_handler

    def _check_updates(self) -> bool:
        """Check for updates from the message system and get the current version."""
        self.infos = self.message_system.get_updates()
        self.my_version = self.file_handler._get_version()

        if self.my_version == "0.0.0":
            raise ValueError("Current version not found !")

        if self.infos is None:
            raise ValueError("No update information found from the message system !")

        latest_version = self.infos.get("version", "0.0.0")

        if latest_version == "0.0.0":
            raise ValueError("Latest version not found from the message system !")

        print(self.infos)

        return latest_version != self.my_version

    def __file_opener(self, filepath: str, mode: str):
        """Open a file with the given mode and return the file object."""
        try:
            file = open(filepath, mode)
            return file
        except Exception as e:
            raise IOError(f"Error opening file {filepath} with mode {mode}: {e}")

    def __process_command(self, command: dict) -> None:
        """Process a single update command."""

        to_exec = command.get("command", None)

        if to_exec is None:
            raise ValueError("No command to execute found !") # scary
        
        match to_exec:

            case "create":
                filepath = command.get("name", None)
                content = command.get("content", "")

                if filepath is None:
                    raise ValueError("No filepath provided for create command (1) !")

                base = Path(getcwd()).resolve()
                target = Path(filepath).resolve()

                if base not in target.parents:
                    raise PermissionError("Path escape detected ! Aborting creation.")

                with self.__file_opener(filepath, "w") as file:
                    file.write(content)

            case "change":
                filepath = command.get("name", None)
                content = command.get("content", "")

                if filepath is None:
                    raise ValueError("No filepath provided for change command (2) !")

                base = Path(getcwd()).resolve()
                target = Path(filepath).resolve()

                if base not in target.parents:
                    raise PermissionError("Path escape detected ! Aborting change.")

                with self.__file_opener(filepath, "w") as file:
                    file.write(content)

            case "delete":
                filepath = command.get("name", None)

                if filepath is None:
                    raise ValueError("No filepath provided for delete command (3) !")
                                
                base = Path(getcwd()).resolve()
                target = Path(filepath).resolve()

                if base not in target.parents:
                    raise PermissionError("Path escape detected ! Aborting deletion.")

                if not Path(filepath).exists():
                    raise FileNotFoundError(filepath)

                remove(filepath)

            case "handover":
                filepath = command.get("name", None)

                if filepath is None:
                    raise ValueError("No filepath provided for handover command (4) !")
                lpath = Path(filepath).resolve()

                env = environ.copy()
                env["PYTHONPATH"] = path.join(getcwd(), "libs")

                self.to_Popen = [executable, str(lpath)], lpath.parent, env

            case _:
                raise ValueError(f"Unknown command to execute: {to_exec} !")

    def __progress_bar(self, current: int, total: int, bar_length: int = 40) -> None:
        """Display a progress bar in the terminal."""

        fraction = current / total
        filled_length = int(bar_length * fraction)
        bar = '#' * filled_length + ' ' * (bar_length - filled_length)
        percent = round(fraction * 100, 1)
        print(f'\r  [{bar}] {percent}% complete: {current}/{total} steps. !!! dont touch anything !!!', end='\r')

        if current == total:
            print()

    def _update_process(self) -> None:
        """Process the update."""

        logging.basicConfig(
            filename=f'logs/update_{self.my_version}_{datetime.now().strftime("%Y%m%d-%H%M%S")}.log',
            format='[%(asctime)s][%(levelname)s]: %(message)s', 
            level=logging.DEBUG
        )

        logging.debug(f"Current version: {self.my_version}")
        logging.debug(f"Update information: {self.infos}")

        logging.info("Starting update process.")

        if self.infos is None:
            logging.error("No update information found from the message system !")
            raise ValueError("No update information found from the message system !")

        commands = self.infos.get("commands", None)

        if commands is None:
            logging.error("No commands found from the message system !")
            raise ValueError("No commands found from the message system !")

        self.__progress_bar(0, 100) # initialize progress bar

        for i, command in enumerate(commands):
            logging.info(f"Processing command {i + 1}/{len(commands)}: {command}")

            # Process each command
            try:          
                self.__process_command(command)

            except Exception as e:
                logging.error(f"Error processing command {i + 1}: {e}. Aborting update.")

                print(f"\nError processing command {i + 1}: {e}. Aborting update.")
                self.__abort_update()

                return

            # Update progress bar
            self.__progress_bar(i + 1, len(commands))


        logging.info("All commands processed successfully.")

        if hasattr(self, "to_Popen"):
            cmd, cwd, env = self.to_Popen

            logging.info(f"Starting handhover process with command: {cmd} in cwd: {cwd}")

            try:
                Popen(cmd, cwd=cwd, env=env)

                logging.info("Handhover process started successfully.")

            except Exception as e:
                logging.error(f"Error starting handhover process: {e}")

                print(f"\nError starting handhover process: {e}. Aborting update.")
                self.__abort_update()

                return

        logging.info("Update process completed successfully.")

    def __abort_update(self) -> None:
        """Abort the update process and log the event."""
        logging.info("Update process aborted.")
        print("Update process aborted. -> Aborting to the previous state...")

class update:
    def __init__(self, message_system, file_handler) -> None:
        self.message_system = message_system
        self.file_handler = file_handler

        self.updater = UpdateSystem(self.message_system, self.file_handler)

    def check_for_updates(self) -> bool:
        """Check for updates from the message system and get the current version."""

        return self.updater._check_updates()
    
    def perform_update(self) -> None:
        """Perform the update process."""

        self.updater._update_process()
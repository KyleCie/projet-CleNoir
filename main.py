from encryptionSystem import encryption
from messageSystem import message
from UserSystem import interpreter
from TerminalSystem import terminal
from dataFileSystem import file

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from threading import Thread, Event

from getpass import getpass
from time import sleep
from hashlib import sha256

if __name__ == "__main__":
    fhandler = file()
    encr = encryption(fhandler)
    printer = terminal(fhandler)
    msg = message(fhandler, encr, printer)
    itptr = interpreter()

    if fhandler._verify_pwd_file():
        pwd = fhandler._open_pwd()
        user_pwd = getpass("Enter your password: ")
        trys = 1

        while pwd != sha256(user_pwd.encode()).hexdigest() and trys < 4: # password verification loop.
            sleep(1)
            print("Wrong password, try again.")
            user_pwd = getpass("Enter your password: ")
            trys += 1

        if trys == 4: # too many wrong attempts.
            print("Too many wrong attempts, exiting...")
            exit()

    print("Starting...")
    sleep(1)

    example_msg = ("[DATE HOUR]", "[PSEUDO]", "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 1234567890 ,?;.:/!") # example message for parameters.
    example_note = ("[DATE HOUR]", "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 1234567890 ,?;.:/!") # example note for parameters.

    myself = msg.get_my_pseudo()    # my own pseudo.
    key_receiver = ""   # public key receiver for the message system.
    cov_reveiver = ""   # conversaton name for the message system.

    session = PromptSession("[message] >>> ") # PromptSession instance for messages.

    type_cmd = "command"
    itptr.run("clear")

    while True:

        command = input(f"[{type_cmd}] >>> ")

        if command == "":   # do nothing if it's empty.
            continue

        cmd = itptr.find_command(command)
        result = cmd(command)

        if isinstance(result, str):  # simple command

            match result:

                case "FIND_CONTACTS":   # find the contact in the system.
                    contacts = msg.get_contact()
                    print("Contacts :")

                    for c in contacts:
                        if c != myself:
                            print(f"-> {c}")

                    continue

                case "RESET_RSA_KEYS":  # reset the rsa keys.
                    encr.reset_keys() # TODO: put to True the `sure` to really reset.
                    key = encr.public_key_RSA()
                    msg.sendPublicKey(key)
                    continue

                case "RESET_NOTIF":
                    print("Deleting the notifications...")
                    msg.delete_notifications()
                    print("Done.")

                case "RESET_PASSWORD":
                    password = getpass("Enter your new password: ")
                    confirm_password = getpass("Confirm your new password: ")

                    if password != confirm_password:
                        print("Passwords do not match, aborting.")
                        continue

                    if password == "":
                        print("Password empty, removing the old one.")

                    print("Saving new password...")
                    hashed_pwd = sha256(password.encode()).hexdigest()
                    fhandler._save_password(hashed_pwd)
                    print("Password updated successfully.")

                case "SAY_PSEUDO":
                    print(f"pseudo: {myself}")
                    continue

                case "REFRESH":
                    print("refreshing...")
                    msg.refresh()
                    print("Done.")

                case "NOTIFICATIONS":
                    print("Getting the notifications...")
                    notifs = msg.get_notifications()
                    notifs = encr.decrypt_notifications(notifs)
                    notifs = msg.transform_notifications(notifs)
                    itptr.run("clearline")
                    printer.print_notifications(notifs)

                case "SAVE_COLORS":
                    print("Saving colors...")
                    printer.save_colors()
                    print("Done.")

                case "SAVE_PASSWORD":
                    new_pwd = getpass("Enter your new password: ")
                    confirm_pwd = getpass("Confirm your new password: ")

                    if new_pwd != confirm_pwd:
                        print("Passwords do not match, aborting.")
                        continue

                    hashed_pwd = sha256(new_pwd.encode()).hexdigest()
                    print("Saving new password...")
                    fhandler._save_password(hashed_pwd)
                    print("Password updated successfully.")

                case "EXIT":
                    print("Exiting...")
                    # remove the streams due to unstopping program.
                    msg.delete_message_stream()
                    msg.delete_notification_stream()
                    break

                case _:
                    continue

        if isinstance(result, tuple): # difficult command :/

            match result[0]:

                case "CONNECT_CONV":    # create and initiate all the parameters and variables for a conversation.
                    receiver = result[1]
                    print(f"Finding a conversation database with '{receiver}'...")

                    contacts = msg.get_contact()

                    if receiver not in contacts:
                        print(f"User : '{receiver}' doesn't exist !")
                        continue

                    cov_reveiver = msg.find_conversation(receiver)  # find user conv with the "_connect_conversation" result.
                    key_receiver = msg.get_PublicKey_from(receiver) # get public key from the receiver.
                    msg.set_conversation(cov_reveiver)              # add the conversation to msg to auto-remove notifs. 

                    print(f"'{cov_reveiver}' found.")
                    print("Connecting...")
                    type_cmd = "message"    # put in message mode.
                    itptr.run("clear")

                    conversation = msg.find_messages(cov_reveiver, stream=True) # get msgs and activate auto stream msgs.

                    print("loading the messages...")

                    # starting the loading message.
                    stop_event = Event()
                    th_spinner = Thread(target=printer.spinner_task, args=(stop_event, "decrypting"))
                    th_spinner.start()

                    # decrypt in the background.
                    conversation = encr.decrypt_messages(conversation, myself)

                    stop_event.set() # stop it.
                    th_spinner.join() # join it.

                    print("transforming...")
                    conversation = msg.transform_messages(conversation)

                    print("printing...")

                    sleep(0.1)
                    itptr.run("clear")

                    printer.print_messages(conversation)

                    while True:     # message system.

                        with patch_stdout(): # activate the prompt stream messages handler.
                            raw_msg = session.prompt() # get the message.

                        itptr.run("clear_line_message", raw_msg, 14)

                        match raw_msg:

                            case "$exit" | "$e":    # exit.
                                msg.delete_message_stream() # deactivate auto stream.
                                msg.set_conversation("") # remove the conv from msg.
                                break

                            case "":        # empty.
                                continue

                            case _:         # send.

                                encr_msg = encr.encrypt(raw_msg, key_receiver)
                                encr_notif = encr.encrypt_notif("New message", key_receiver)
                                msg.send(encr_msg, encr_notif, cov_reveiver, receiver)

                    type_cmd = "command"    # reput in command system.

                case "MYSPACE":     # connect with user's myspace.

                    my_space = result[1]

                    print(f"Finding a myspace with '{my_space}'...")
                    msg.find_myspace()
                    print("Getting the notes...")

                    type_cmd = "note"
                    itptr.run("clear")

                    notes = msg.find_notes_myspace(my_space)
                    notes = encr.decrypt_notes_myspace(notes)
                    notes = msg.transform_notes(notes)

                    printer.print_notes(notes)

                    while True:
                        raw_note = input(f"[{type_cmd}] >>> ")
                        itptr.run("clear_line_message", raw_note, 11)

                        match raw_note:

                            case "$exit" | "$e":   # exit.
                                break

                            case "":        # empty.
                                continue

                            case _:         # send.

                                encr_note = encr.encrypt_note(raw_note)
                                msg.send_note(encr_note, my_space)

                                last_note = msg.find_notes_myspace(my_space)
                                last_note = [last_note[-1]] # get the delta notes (new notes).

                                last_note = encr.decrypt_notes_myspace(last_note)
                                last_note = msg.transform_notes(last_note)

                                printer.print_notes(last_note) # print new conversation (notes).

                    type_cmd = "command"    # reput in command system.  

                case "CHANGE_MSG_COLOR":    # change colors messages parameters.

                    printer.change_messages_colors(result[1:])
                    print("RESULT :")
                    printer.print_messages([example_msg])

                case "CHANGE_NOTES_COLOR":  # change colors notes parameters.

                    printer.change_notes_colors(result[1:])
                    print("RESULT :")
                    printer.print_notes([example_note])

                case "CHANGE_NOTIFS_COLOR": # change colors notifs parameters.

                    printer.change_notifications_colors(result[1:])
                    print("RESULT :")
                    printer.print_notifications([example_msg])

                case _:     # can't find anything with it.
                    continue
    
    # while exit here
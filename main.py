from encryptionSystem import encryption
from messageSystem import message
from UserSystem import interpreter
from TerminalSystem import terminal
from dataFileSystem import file

from time import sleep

if __name__ == "__main__":
    fhandler = file()
    encr = encryption()
    msg = message(fhandler)
    itptr = interpreter()
    printer = terminal(fhandler)

    print("Starting...")

    example_msg = ("[DATE HOUR]", "[PSEUDO]", "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 1234567890 ,?;.:/!") # example message for parameters.
    example_note = ("[DATE HOUR]", "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 1234567890 ,?;.:/!") # example note for parameters.

    myself = msg.get_my_pseudo()    # my own pseudo.
    key_receiver = ""   # public key receiver for the message system.
    cov_reveiver = ""   # conversaton name for the message system.

    #sleep(1)   # TODO: remove this command to activate.

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
                        if c == myself:
                            print(f"-> {c}")
                            
                    continue

                case "RESET_RSA_KEYS":  # reset the rsa keys.
                    encr.reset_keys()
                    key = encr.public_key_RSA()
                    msg.sendPublicKey(key)
                    continue

                case "SAY_PSEUDO":
                    print(f"pseudo: {myself}")
                    continue

                case "REFRESH":
                    print("refreshing...")
                    msg.refresh()

                case "EXIT":
                    print("Exiting...")
                    exit()

                case _:
                    continue

        if isinstance(result, tuple): # difficult command :/

            match result[0]:

                case "CONNECT_CONV":    # create and initiate all the parameters and variables for a conversation.
                    print(f"Finding a conversation database with '{result[1]}'...")

                    contacts = msg.get_contact()

                    print(contacts)

                    if result[1] not in contacts:
                        print(f"User : '{result[1]}' doesn't exist !")
                        continue

                    cov_reveiver = msg.find_conversation(result[1]) # find user conv with the "_connect_conversation" result.
                    key_receiver = msg.get_PublicKey_from(result[1]) # get public key from the receiver.

                    print(f"'{cov_reveiver}' found.")
                    print("Connecting...")
                    type_cmd = "message"    # put in message mode.
                    itptr.run("clear")

                    conversation = msg.find_messages(cov_reveiver)
                    last_cov_index = len(conversation)  # get the base value to get the difference later.

                    conversation = encr.decrypt_messages(conversation, myself)
                    conversation = msg.transform_messages(conversation)                    

                    printer.print_messages(conversation) # print conversation
                    
                    while True:     # message system.
                        raw_msg = input(f"[{type_cmd}] >>> ")
                        itptr.run("clearline")

                        match raw_msg:

                            case "$exit":   # exit.
                                break

                            case "$e":      # exit.
                                break

                            case "":        # empty.
                                continue

                            case _:         # send.

                                encr_msg = encr.encrypt(raw_msg, key_receiver)
                                msg.send(encr_msg, cov_reveiver)

                                last_msg = msg.find_messages(cov_reveiver)
                                last_msg = last_msg[last_cov_index:]  # get the delta messages (new messages).
                                last_cov_index += len(last_msg)     # reindexing last messages.

                                last_msg = encr.decrypt_messages(last_msg, myself)
                                last_msg = msg.transform_messages(last_msg)

                                printer.print_messages(last_msg) # print new conversation (messages).

                    type_cmd = "command"    # reput in command system.

                case "MYSPACE":     # connect with user's myspace.

                    my_space = result[1]

                    print(f"Finding a myspace with '{my_space}'...")
                    msg.find_myspace()
                    print("Getting the notes...")

                    type_cmd = "message"
                    itptr.run("clear")

                    notes = msg.find_notes_myspace(my_space)
                    notes = encr.decrypt_notes_myspace(notes)
                    notes = msg.transform_notes(notes)
                    last_note_index = len(notes)

                    printer.print_notes(notes)

                    while True:
                        raw_note = input(f"[{type_cmd}] >>> ")
                        itptr.run("clearline")

                        match raw_note:

                            case "$exit":   # exit.
                                break

                            case "$e":      # exit.
                                break

                            case "":        # empty.
                                continue

                            case _:         # send.

                                encr_note = encr.encrypt_note(raw_note)
                                msg.send_note(encr_note, my_space)

                                last_note = msg.find_notes_myspace(my_space)
                                last_note = last_note[last_note_index:]  # get the delta notes (new notes).
                                last_note_index += len(last_note)     # reindexing last notes.

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

                case _:     # can't find anything with it.
                    continue
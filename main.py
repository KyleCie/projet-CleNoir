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

    example_msg = (["[DATE HEURE]", "[PSEUDO]", "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 1234567890 ,?;.:/!"]) # example message for parameters.
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
                                last_msg = last_msg[last_cov_index-1:]  # get the delta messages (new messages).
                                last_cov_index += len(last_msg)     # reindexing last messages.

                                last_msg = encr.decrypt_messages(last_msg, myself)
                                last_msg = msg.transform_messages(last_msg)

                                printer.print_messages(conversation) # print new conversation (messages).

                    type_cmd = "command"    # reput in command system.

                case "CHANGE_MSG_COLOR":

                    printer.change_messages_colors(result[1:])
                    print("EXEMPLE :")
                    printer.print_messages([example_msg])

                case _:     # can't find anything with it.
                    continue
# -*- coding: utf-8 -*-

##
# University of the West of Scotland
# Author: Guillermo Siesto Sanchez B00334584
# e-Mail: b00334684 at studentmail.uws.ac.uk
# Date: 2018
# Description: The purpose of this coursework is to develop a distributed chat
#   system without using any thrid party networking library.
#
# ===========
# S E R V E R
# ===========
##

##
# Imports
##
import datetime
import logging  # Generate a log file to record all the changes made
import socket
from sys import argv, stdout
import os   # For exiting of every thread
import re
import threading        # Threading
import string
import random
from pyftpdlib.authorizers import DummyAuthorizer   # FileTranferProtocol
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import glob     # For viewing files in a path

##
# Configuration of the log file
##
logging.basicConfig(level=logging.INFO,
                    filename='log/ChatApplication_server.log',
                    format='[%(levelname)s] %(asctime)s %(message)s', )

##
# Inicialization
##
host = '127.0.0.1'
buffer_size = 12800
n_connection = 100          # Number of possible connection
ftp_password = "ftpadmin"

active_connections = []     # User connected. [[username, grant, socket], ...
inactive_connections = []   # User inactive. [[username, grant, socket], ...
kick_connections = []       # Kicked users. [[username, grant, socket], ...

##
# lock
lock = threading.RLock()


##
# First iteration between the client and the server.
# The server will ask for the credentials of the user identifiying if it needs
# to be registered or logged
#
# @param client_sock Raw socket introduced as a parameter
# @param client_ip_and_port A list of two slots with the ip and the port
#        of the client
#
# @exception if the conecction with the socket is interrupted
def connect_client(client_sock, client_ip_and_port):
    client_sock.sendall('Connecting...\n')
    print '] A client [{}] is trying to connect...'.format(client_ip_and_port)
    client_ip = client_ip_and_port[0]

    credential_response = ask_credentials(client_sock)

    logging.info("User Login Info = {}".format(credential_response))

    user_name = credential_response[1][1]

    if (credential_response[0] == 'y'):     # REGISTER
        if (credential_response[1][0]):
            print '] USER:%s with IP:%s has join the room for the first time' % (credential_response[1][1], client_ip)
            client_sock.sendall('<Server>: You have entered the room')
            client_sock.sendall('================== < > ==================')
            # Add to the active user list
            user_data = [user_name, 1, client_sock]
            with lock:
                active_connections.append(user_data)
            # Loop
            open_connection(client_sock, user_name, 'l')
        else:
            print "ERROR 1 -> The username CAN'T exist in the database, try again"
            client_sock.sendall("<Server>: ERROR 1 -> The username CAN'T exist in the database, try again")
            connect_client(client_sock, client_ip_and_port)

    elif (credential_response[0] == 'n'):   # LOGIN
        if (credential_response[1][0]):
            print '] USER:%s with IP:%s has join the room' %(credential_response[1][1], client_ip)
            client_sock.sendall('<Server>: Welcome back {} \n'.format(credential_response[1][1]))
            client_sock.sendall('================== < > ==================')

            # Add to the active user list
            user_data = [user_name, get_user_grant(user_name), client_sock]
            with lock:
                active_connections.append(user_data)
            # Loop
            open_connection(client_sock, user_name, 'r')
        else:
            print "ERROR 2 -> The credentials are incorrect"
            client_sock.sendall("<Server>: ERROR 2 -> The credentials are incorrect")
            connect_client(client_sock, client_ip_and_port)

    else:
        print '] USER:%s with IP:%s has problems trying to connect. Please try again' %(credential_response[1][1], client_ip)
        client_sock.sendall('<Server>: You had problems to connect. Please try again')
        connect_client(client_sock, client_ip_and_port)


##
# Semi-infinite loop with the soket waiting to comunicate client and server
def open_connection(client_sock, user_name, direction):
    try:
        while (get_socket_index(client_sock) != -1):    # While exists
            message = client_sock.recv(buffer_size)
            msg = message
            check_message(client_sock, user_name, msg)
    except ():
        if direction == 'r':
            print "] Exception when receiving on REGISTER"
        else:
            print "] Exception when reciving on LOGIN"
        client_exit(client_sock)
        print "\nSever down ==================\n"
        os._exit(1)


##
# It is dedicated of asking the credential by command line to the user.
#
# @param client_sock Raw socket introduced as a parameter
#
# @return a list of list with the information:
#           [0] 'y' user wants to register / 'n' wants to login
#           [1]
#           [1][0] return of the method call create_user(client_sock)
#           [1][1] return of the  method call login_user(client_sock)
def ask_credentials(client_sock):
    try:
        client_sock.sendall('<Server>: Do you want to create a new user? [y/n]')
        response = client_sock.recv(buffer_size)
        if (response == 'y'):       # YES
            return ('y', create_user(client_sock))

        elif (response == 'n'):     # NO
            return ('n', login_user(client_sock))
        else:
            # Default
            client_sock.sendall('<Server>: Error, you must respond with "y" saying yes or "n" saying no')
            ask_credentials(client_sock)
    except ():
        print "] Exception while asking credentials"
        client_exit(client_sock)
        print "\nSever down ==================\n"
        os._exit(1)


##
# Create a user saving it in a text file. The server will ask for the
# credentials through the command line
#
# @param client_sock Raw socket introduced as a parameter
#
# @return A list with two elements:
#           [0] Boolean telling if was possible creating an username
#           [1] String with the username
def create_user(client_sock):
    client_sock.sendall('<Server>: (1/3) Write your user name:')
    user_name = client_sock.recv(buffer_size)
    client_sock.sendall('<Server>: (2/3) Write your password:')
    user_password = client_sock.recv(buffer_size)
    client_sock.sendall('<Server>: (3/3) Write your password:')
    user_password_2 = client_sock.recv(buffer_size)

    with open('database/users_credentials.txt', 'r') as rDoc:
        database_doc_list = rDoc.readlines()
    rDoc.close()
    answer = (False, user_name)
    if (not(user_name in database_doc_list)):
        if ((user_password == user_password_2)):    # 2 passwords math?
            with open('database/users_credentials.txt', 'a') as aDoc:
                aDoc.write('\n' + user_name + ';' + user_password + '#' + format(1))
                # TODO encrypt password

            print '] %s Has join the party.\n' % user_name
            answer = (True, user_name)
        else:
            client_sock.sendall('<Server>: The password are not the same, please try again')
            answer = (False, user_name)
    else:
        client_sock.sendall('<Server>: You must choose another username')
        answer = (False, user_name)
    return answer


##
# Check is the password introduced as parameter math with the user and
# password in the database doc
def check_password(user_name, password):
    answer = False
    salir = False
    with open('database/users_credentials.txt', 'r') as rDoc:
        database_doc_list = rDoc.readlines()
    # Eliminate '\n' from our list
    database_doc_list = map(lambda each: each.strip("\n"), database_doc_list)

    i = 0
    while (i < len(database_doc_list) and (not salir)):   # Working
        sublist = re.split('[;#]', database_doc_list[i])
        if (user_name == sublist[0]):
            if (password == sublist[1]):
                answer = True
            else:
                salir = True
        i = i + 1

    rDoc.close()    # Close document
    return answer


##
#
def id_generator(size=9, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


##
#
def file_transfer(client_sock, message, direction):

    user_name = active_connections[get_socket_index(client_sock)][0]

    authorizer = DummyAuthorizer()
    authorizer.add_user(user_name, ftp_password, "files_client/%s" % (user_name), perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer

    server = FTPServer(("localhost", 9797), handler)
    server.serve_forever()

    if (direction == 'u'):
        client_sock.sendall(">uploadfile")
    else:
        client_sock.sendall(">downloadfile")




##
#
def view_files(client_sock):
    list = glob.glob("files/*.*")
    client_sock.sendall("\n".join([str(x) for x in list]))
    print "************** FILES ****************"
    print "\n".join([str(x) for x in list])
    print "**************       ****************"


##
# The user is asked to introduce his data by parameter and it will be check if
# the data input is equal to the one saved in the txt file.
#
# @param: client_sock Raw socket
#
# @return: A list with a boolean telling if the input was found in the txt, and
#           the username inputed.
def login_user(client_sock):
    client_sock.sendall('<Server>: Write your user name:')
    user_name = client_sock.recv(buffer_size)
    client_sock.sendall('<Server>: Write your password:')
    user_password = client_sock.recv(buffer_size)

    answer = (False, user_name)

    with open('database/users_credentials.txt', 'r') as rDoc:
        database_doc_list = rDoc.readlines()

    database_doc_list = map(lambda each:each.strip("\n"), database_doc_list)    # Eliminate '\n' from our list

    i = 0
    while (not answer[0] and i < len(database_doc_list)):
            sublist = re.split('[; #]', database_doc_list[i])   # TODO GOOOD :)

            if ((user_name == "admin") or (user_name == sublist[0])):

                if (user_password == sublist[1]):
                    answer = (True, user_name)
            else:
                answer = (False, user_name)
            i = i + 1

    rDoc.close()    # Close the document
    return answer


def client_exit(client_sock):
    print "\n\n]---------ALL ACTIVE CONNECTIONS:---------\n"
    print format(active_connections)
    print "\n]-----------------------------------------\n\n"
    print "] Disconnecting: " + format(active_connections[get_socket_index(client_sock)])
    client_sock.sendall("<Server>: You are going to be disconnected by the server")
    stdout.flush()
    with lock:
        client_sock.sendall(">disconnect")

    with lock:
        inactive_connections.append(active_connections[get_socket_index(client_sock)])
        active_connections.pop(get_socket_index(client_sock))

    print "\n\n]---------ALL ACTIVE CONNECTIONS:---------\n"
    print format(active_connections)
    print "\n]-----------------------------------------\n\n"


def clients_exit(client_sock):
    stdout.flush()
    i = 0
    while i < len(active_connections):
        # Handle lists
        client_exit(active_connections[i][2])
        i += 1


##
# Check if the message introduced as a parameter is of the kind of "command"
# (calling to the specific method to check ir) or if its a typical one, showing
# it through the command line
#
# @param user_name
# @param message
def check_message(client_sock, user_name, message):
    if (message.startswith("/")):
        print "] Checkeado init"
        check_command(client_sock, user_name, message)
        print "] Checkeado exit"
    else:
        currentDT = datetime.datetime.now()
        # Print in every client screen
        for x in range(len(active_connections)):
            active_connections[x][2].sendall(currentDT.strftime("%I:%M %p | ") + user_name + ": " + message)
        # Show in server side
        print currentDT.strftime(" %I:%M %p | ") + user_name + ": " + message


##
# The message will be check in case on starting with '/' (the command
# Inicialization character), and in every case some specific method
# will be called
#
# @param message String with the text input
def check_command(client_sock, user_name, message):
    msg = message
    if msg.startswith("/viewusers"):
        print "] %s solicit /viewusers" % user_name
        print "================= ACTIVE CONNECTIONS"
        print_list_client(client_sock, active_connections)
    elif msg.startswith("/messageto"):
        print "] %s solicit /messageto" % user_name
        message_to(client_sock, message)
    elif msg.startswith("/changepassword"):
        print "] %s solicit /changepassword" % user_name
        print "e changepassword"
    elif msg.startswith("/busy"):
        print "] %s solicit /busy" % user_name
        client_sock.sendall(">busy")
    elif msg.startswith("/free"):
        print "] %s solicit /free" % user_name
        client_sock.sendall(">free")
    elif msg.startswith("/changegrant"):
        print "] %s solicit /changegrant" % user_name
        change_grant(client_sock, user_name, message)
    elif msg.startswith("/kickuser"):
        print "] %s solicit /kickuser" % user_name
        kick_user(client_sock, message)
    elif msg.startswith("/viewkickusers"):
        print "] %s solicit /viewkickusers" % user_name
        print "================= KICK CONNECTIONS"
        print_list_client(client_sock, kick_connections)
    elif msg.startswith("/restart"):
        print "] %s solicit /restart" % user_name
        print "e restart"
    elif msg.startswith("/senddata"):
        print "] %s solicit /senddata" % user_name
        print "e senddata"
    elif msg.startswith("/disconnect"):
        print "] %s solicit /disconnect" % user_name
        client_exit(client_sock)
    elif msg.startswith("/uploadfile"):
        file_transfer(client_sock, message, 'u')
    elif msg.startswith("/downloadfile"):
        file_transfer(client_sock, message, 'd')
    elif msg.startswith("/viewfiles"):
        view_files(client_sock)
    elif msg.startswith("/help"):
        print "] %s solicit /help" % user_name
        client_sock.sendall("You can type:\n /viewusers\n /messageto\n /changepassword\n /busy\n /free\n /changegrant\n /kickuser\n /viewkickusers\n /restart\n /senddata\n /disconnect")
    else:
        print "] %s solicit couldm't be resolved. Non existing commands" % user_name
        client_sock.sendall("<Server>: [Error typing] Type '/help' see all possible commands")


def message_to(client_sock, message):
    sublist = re.split(' ', message)    # It will end as ['/messageto', 'username', 'whatever', ...]
    index = get_user_index(sublist[1])

    if (index != -1):
        del sublist[0]      # Remove command
        print ' '.join(sublist)
        active_connections[index][2].sendall("] PM from: " + sublist[0] + "\n] <Message>")
        del sublist[0]      # Remove user_name
        active_connections[index][2].sendall(' '.join(sublist) + "\n] <End of message>")
    else:
        client_sock.sendall("Error 3 -> User not found")


def kick_user(client_sock, message):
    sublist = re.split(' ', message)    # It will end as ['/kickuser', 'username', 'whatever', ...]
    index = get_user_index(sublist[1])
    if (index != -1):
        if (active_connections[get_socket_index(client_sock)][1] == '0'):     # Only if the origin user is a superuser
            active_connections[index][2].sendall(">kick")
            user_data = [active_connections[index][0], active_connections[index][1], active_connections[index][2]]      # Add to kick list
            kick_connections.append(user_data)

            client_sock.sendall("================= KICK CONNECTIONS")
            print_list_client(client_sock, kick_connections)

            client_exit(active_connections[index][2])
        else:
            client_sock.sendall("Error 3 -> You don't have the grant to make that operation")
    else:
        client_sock.sendall("Error 4 -> User not found")


def change_grant(client_sock, user_name, message):
    # message = command + " " + user_targer + " " + grant
    possible = False
    if (get_user_grant(user_name) == 0):    # If the solicitor is superuser
        msg_splited = re.split('[" "]', message)
        possible = set_user_grant(msg_splited[1], msg_splited[2])
        client_sock.sendall(msg_splited[0] + " " + msg_splited[2])
    else:
        client_sock.sendall("] You have no grant to make that operation")
    return possible


def get_user_grant(user_name):
    with open('database/users_credentials.txt', 'r') as rDoc:
        database_doc_list = rDoc.readlines()
    database_doc_list = map(
                            lambda each: each.strip("\n"),
                            database_doc_list)  # Eliminate '\n'
    grant = -1
    i = 0
    while ((i < len(database_doc_list)) and (grant < 0)):   # Working
        sublist = re.split('[;#]', database_doc_list[i])
        if (user_name == sublist[0]):
            grant = int(sublist[2])
        i = i + 1
    rDoc.close()        # Closing document
    print "GRANT: " + format(grant)
    return grant

def set_user_grant(user_name, new_grant):
    # READING
    with open('database/users_credentials.txt', 'r') as rDoc:
        database_doc_list = rDoc.readlines()
    database_doc_list = map(
                            lambda each: each.strip("\n"),
                            database_doc_list)  # Eliminate '\n'
    found = False
    i = 0
    index_parent_list = 0
    while ((i < len(database_doc_list)) and (not found)):   # Working
        sublist = re.split('[;#]', database_doc_list[i])
        if (user_name == sublist[0]):
            index_parent_list = i
            found = True
            user_data = [user_name, sublist[1], new_grant]
        i = i + 1
    rDoc.close()        # Closing document

    # WRITING If found
    if (found):
        # Delete line
        database_doc_list.append('\n' + user_data[0] + ';' + user_data[1] + '#' + user_data[2])
        # Add line
        database_doc_list.pop(index_parent_list)
        wDoc = open("database/users_credentials.txt", "w")
        for line in database_doc_list:
            wDoc.write(line + "\n")       # Rewrite again all the list minus target
        wDoc.close()

    return found    # Know if find


##
# Will search in the active_connections list to look for the appearance of
# the username
#
# @param: user_name
#
# @Return: (-1) if not found, (position) if found
def get_user_index(user_name):
    i = 0
    encontrado = False
    while (i < len(active_connections) and (not encontrado)):
        if (user_name == active_connections[i][0]):
            encontrado = True
        else:
            i = i + 1
    if encontrado:
        return i
    else:
        return -1


def get_socket_index(socket):
    i = 0
    encontrado = False
    while (i < len(active_connections) and (not encontrado)):
        if (socket == active_connections[i][2]):
            encontrado = True
        else:
            i = i + 1
    if encontrado:
        return i
    else:
        return -1


##
# Print a list in a formated way
#
# @param list A list inputed as parameter
def print_list_client(client_sock, list):
    client_sock.sendall("\n\n---------------------------------\n")
    client_sock.sendall(" N | User      | Grant  \n")

    i = 0
    while (i < len(list)):
        client_sock.sendall(" " + format(i) + " | " + format(list[i][0]) + " | " + format(list[i][1]) + "\n")
        i = i + 1
    client_sock.sendall("---------------------------------\n\n")


##
# Main
def main(argv):
    server_port = 9797
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((host, server_port))
    sock.listen(n_connection)

    print '] Server on port ' + str(server_port)
    logging.info("Server on port {}".format(server_port))

    stdout.flush()      # Clean

    try:
        while 1:
            client_connection, addr = sock.accept()
            print '] Client connected on '  + str(addr[0]) + ':' + str(addr[1]) + '\n'
            logging.info("Chat Client Connected on IP {} & Port {}".format(host, server_port))

            stdout.flush()      # Clean

            # THREADIND
            server_t = threading.Thread(target=connect_client, args=(client_connection, addr))
            server_t.start()

    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        # For every ip we must close the socket
        clients_exit(sock)
        print "\nSever down ==================\n"
        os._exit(1)


main(argv)

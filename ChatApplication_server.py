# University of the West of Scotland
# Author: Guillermo Siesto Sanchez B00334584
# Date: 2018
# Description: The purpose of this coursework is to develop a distributed chat system using a networking library.

# ===========
# S E R V E R
# ===========

# Imports
import datetime
import logging # Generate a log file to record all the changes made
import socket
from sys import argv, stdout, exit
import re
from threading import Thread #Threading

#Config
logging.basicConfig(level=logging.INFO, filename='log/ChatApplication_server.log', format='[%(levelname)s] %(asctime)s %(message)s', )


# Inicialization
host = '127.0.0.1'
buffer_size = 12800
n_conection = 100 # Number of possible connection

logged_connections = {} # User connected
kick_connections = {} # Users that has been kicked
expired_connections = {}

def connect_client(client_sock, client_ip_and_port):
    client_sock.sendall('Connecting...\n')
    print 'A client is trying to connect...\n'
    client_ip = client_ip_and_port[0]
    client_port = client_ip_and_port[1]

    if (not kick_connections.has_key(client_ip)):
        kick_connections[client_ip] = []

    try:
        while 1:
            credential_response = ask_credentials(client_sock)

            logging.info("User Login Info = {}".format(credential_response))

            if (credential_response[0] == 'created'):
                print 'USER with IP:%(client_ip) and USER:%(credential_response[2])  has join the room for the first time\n'

            elif (credential_response[0] == 'logged'):
                print 'USER with IP has join the room\n'

            else:
                client_sock.sendall('Login failed too many times. Please try again\n')
    except:
        client_exit(client_sock, client_ip, client_port)

def ask_credentials(client_sock): #TODO ADD (client_ip, client_port) in parameters for a timer
    client_sock.sendall('Do you want to create a new user? [y/n]\n')
    response = client_sock.recv(buffer_size)

    if (response == "y"):
        #YES
        return (created, create_user(client_sock) )

    elif (response =="n"):
        #NO
        return (logged, login_user(client_sock))
    else:
        #Default
        client_sock.sendall('Error, you must respond with "y" saying yes or "n" saying no.\n')
        ask_credentials(client_sock, client_ip, client_port)

def create_user(client_sock):

    client_sock.sendall('write your user name:\n')
    user_name = client_sock.recv(buffer_size)
    client_sock.sendall('write your password:\n')
    user_password = client_sock.recv(buffer_size)
    client_sock.sendall('write your password:\n')
    user_password_2 = client_sock.recv(buffer_size)

    database_doc = open('database/', 'r').read().split('\n')[6].split(';')
    if (not(user_name == "admin") or not(user_name in database_doc)):
        if (user_password == user_password_2):
            with open('/database/users_credentials.txt', 'a') as aFile:
                aFile.write('\n' + new_user + ' ' + new_pass) #TODO encrypt password

            client_sock.sendall('%(user_name) have been welcome.\n')
            print '%(user_name) Has join the party.\n'
            return (True, user_name)

        else:
            client_sock.sendall('The password are not the same, please try again\n')
            create_user(client_sock)
    else:
        client_sock.sendall('You must choose another username\n')
        ask_credentials(client_sock)
        return (False, user_name)

def login_user(client_sock):
    client_sock.sendall('write your user name:\n')
    user_name = client_sock.recv(buffer_size)
    client_sock.sendall('write your password:\n')
    user_password = client_sock.recv(buffer_size)

    #TODO
    database_doc = open('database/', 'r').read().split('\n')[6].split(';')
    if ((user_name == "admin") OR (user_name not in database_doc)):
        if (user_password in database_doc):
            return (True, user_login)
    else
        return (False, user_login)


def client_exit(client, client_ip, client_port):
    #TODO
    print 'Client on %s : %s disconnected' %(client_ip, client_port)
    stdout.flush()
    client.close()

# Main
def main(argv):

    server_port = 9797
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((host, server_port))
    sock.listen(n_conection)

    print 'Server on port ' + str(server_port) + '\n'
    logging.info("Server on port {}".format(server_port))

    stdout.flush()

    try:
        while 1:
            client_connection, addr = sock.accept()
            print 'Client connected on '  + str(addr[0]) + ':' + str(addr[1]) +'\n'
            logging.info("Chat Client Connected on IP {} & Port {}".format(host, server_port))
            stdout.flush()

            #THREADIND
            server_t = Thread(target=connect_client, args=(client_connection, addr))
            server_t.start()

    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        print "\nSever down\n"

main(argv)

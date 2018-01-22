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
from sys import argv
from sys import stdout
import re

#Config
logging.basicConfig(level=logging.INFO, filename='log/ChatApplication_server.log', format='[%(levelname)s] %(asctime)s %(message)s', )


# Inicialization
host = '127.0.0.1'
buffer_size = 12800
n_conection = 100 # Number of possible connection

logged_connections = {} # User connected
kick_connections = {} # Users that has been kicked
expired_connections = {}

# Connection with the client
def connect_client(client_sock, client_ip_and_port):
    client_ip = client_ip_and_port[0]
    client_port = client_ip_and_port[1]

    if (not kick_connections.has_key(client_ip)):
        kick_connections[client_ip] = []

    create_user(client_sock)

    try:
        while 1:
            user_login = prompt_login(client_sock, client_ip, client_port)

            logging.info("User Login Info = {}".format(user_login))

            if (user_login[0]):
                print 'USER with IP has join the room\n'

            else:

                client_sock.sendall('Login failed too many times. Please try again\n')
                block(client_ip, client_sock, user_login[1])
                Timer(block_time, unblock, (client_ip, user_login[1])).start()
    except:
        client_exit(client_sock, client_ip, client_port)

def create_user(client_sock):
    client_sock.sendall('Do you want to create a new user? [y/n]\n')
    response = ""
    response = cliente_sock.recv(buffer_size)
    if response == 'y': #yes
            #Register
            client_sock.sendall('write your user name:\n')
            user_name = ""
            user_name = cliente_sock.recv(buffer_size)
            client_sock.sendall('write your password:\n')
            user_password = ""
            user_password = cliente_sock.recv(buffer_size)
            client_sock.sendall('write your password:\n')
            user_password_2 = ""
            user_password_2 = cliente_sock.recv(buffer_size)

            database = ""
            database = open('database/', 'r').read().split('\n')[6].split(';')
            if (user_name == "admin" or user_name in database)
            #TODO NO EXISTE EN LA LISTA DE USUARIOS
                if (user_password == user_password_2)
                    with open('/database/users_credentials.txt', 'a') as aFile:
                        aFile.write('\n' + new_user + ' ' + new_pass) #TODO encrypt password

                    client_sock.sendall('%(user_name) Has join the party.\n')
                else
                    client_sock.sendall('The password are not the same, please try again\n')
                    create_user(client_sock)
            else
                client_sock.sendall('You must choose another username\n')
                create_user(client_sock)

    elif response =='n': #no
            #Login
            login(client_sock)

    else
        client_sock.sendall('Error, you must respond with "y" saying yes or "n" saying no.\n')) #Default
        create_user(client_sock)



def login(client_sock):
    client_sock.sendall('write your user name:\n')
    user_name = cliente_sock.recv(buffer_size)
    client_sock.sendall('write your password:\n')
    user_password = cliente_sock.recv(buffer_size)

    #Buscar en la lista si el usuario y la contraseña existen

# Main
def main(argv):

    server_port = 9797
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((host,server_port)) #Bind
    sock.listen(n_conection)

    print 'Server on port ' + str(server_port) + '\n'
    logging.info("Server on port {}".format(server_port))

    stdout.flush()

    try:
        while 1:
            client_connection, addr = sock.accept()
            print 'Client connected on '  + str(addr[0]) + ':' + str(addr[1] +'\n')
            logging.info("Chat Client Connected on IP {} & Port {}".format(host, server_port))
            stdout.flush()

            handle_client()

    except (KeyboardInterrupt, SystemExit):
        stdout.flush()

main(argv)

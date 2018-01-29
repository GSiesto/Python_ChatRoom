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
    print 'A client [{}] is trying to connect...\n'.format(client_ip_and_port)
    client_ip = client_ip_and_port[0]
    client_port = client_ip_and_port[1]

    # if (not kick_connections.has_key(client_ip)):
    #     kick_connections[client_ip] = []

    #ask_credentials(client_sock)
    credential_response = ask_credentials(client_sock)

    logging.info("User Login Info = {}".format(credential_response))
    print format(credential_response)

    if (credential_response[0] == 'y'):
        print 'AAAAAA'
        print 'USER with IP:%s and USER:  has join the room for the first time\n' %(client_ip)#, credential_response[1[1]])
        client_sock.sendall('You have entered the room\n')

        #TODO def of normal_mensaje Mas tarde sera el modulo que comprueba si es comando o no, y por defecto llevara a mensaje
        try:
            while 1:
                message = client_sock.recv(buffer_size)
                print (message)
        except:
            logout(client_sock)
            client_exit(client_sock, client_ip, client_port)

    elif (credential_response[0] == 'n'):
        print 'USER with IP has join the room\n'
        client_sock.sendall('Welcome back %s \n' %credential_response[1[1]]) #TODO comprobar
        try:
            while 1:
                message = client_sock.recv(buffer_size)
                print (message)
        except:
            client_exit(client_sock, client_ip, client_port)

    else:
        print 'OOOOOOO'
        print 'USER with IP:%s and USER:  has problems trying to connect. Please try again\n' %(client_ip)
        client_sock.sendall('Login failed too many times. Please try again\n')
        ask_credentials(client_sock)


def ask_credentials(client_sock): #TODO ADD (client_ip, client_port) in parameters for a timer
    client_sock.sendall('Do you want to create a new user? [y/n]\n')
    response = client_sock.recv(buffer_size)

    if (response == 'y'):
        #YES
        return ('y', create_user(client_sock) )

    elif (response == 'n'):
        #NO
        return ('n', login_user(client_sock))
    else:
        #Default
        client_sock.sendall('Error, you must respond with "y" saying yes or "n" saying no.\n')
        ask_credentials(client_sock)

def create_user(client_sock):
    client_sock.sendall('>(1/3) Write your user name:')
    user_name = client_sock.recv(buffer_size)
    client_sock.sendall('>(2/3) Write your password:')
    user_password = client_sock.recv(buffer_size)
    client_sock.sendall('>(3/3) Write your password:')
    user_password_2 = client_sock.recv(buffer_size)

    retorno = (False, user_name)

    with open('database/users_credentials.txt', 'r') as rDoc:
        data = rDoc.readlines()

        for line in data:
            words = line.split('\n') #.split(';')
        print words

    if (not(user_name == "admin") or not(user_name in database_doc)):
        if (user_password == user_password_2):
            with open('database/users_credentials.txt', 'a') as aDoc:
                aDoc.write('\n' + user_name + ';' + user_password) #TODO encrypt password

            print '%s Has join the party.\n' %user_name
            client_sock.sendall('You has been welcome.\n')
            retorno = (True, user_name)
        else:
            client_sock.sendall('The password are not the same, please try again\n')
            retorno = (False, user_name)
            ask_credentials(client_sock)
    else:
        client_sock.sendall('You must choose another username\n')
        retorno = (False, user_name)
        ask_credentials(client_sock)
    rDoc.close() #Close document
    return retorno

def login_user(client_sock):
    client_sock.sendall('write your user name:\n')
    user_name = client_sock.recv(buffer_size)
    client_sock.sendall('write your password:\n')
    user_password = client_sock.recv(buffer_size)

    #TODO
    database_doc = open('database/', 'r').read().split('\n')[6].split(';')
    if ((user_name == "admin") or (user_name in database_doc)):
        if (user_password in database_doc):
            return (True, user_login)
    else:
        return (False, user_login)


def clietn_logout(client_sock):
    client_sock.sendall("You has been disconnected by the server")
    client_sock.close()

def client_exit(client_sock, client_ip, client_port):
    print 'Client on %s : %s disconnected' %(client_ip, client_port)
    stdout.flush()
    client_sock.close()

# Main
def main(argv):

    server_port = 9797
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((host, server_port))
    sock.listen(n_conection)

    print 'Server on port ' + str(server_port)
    logging.info("Server on port {}".format(server_port))

    stdout.flush() # Clean

    try:
        while 1:
            client_connection, addr = sock.accept()
            print 'Client connected on '  + str(addr[0]) + ':' + str(addr[1]) +'\n'
            logging.info("Chat Client Connected on IP {} & Port {}".format(host, server_port))

            stdout.flush() # Clean

            #THREADIND
            server_t = Thread(target=connect_client, args=(client_connection, addr))
            server_t.start()

    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        print "\nSever down ==================\n"
        exit(1) #TODO comprobar

main(argv)

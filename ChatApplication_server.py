# -*- coding: utf-8 -*-
##
# University of the West of Scotland
# Author: Guillermo Siesto Sanchez B00334584
# Date: 2018
# Description: The purpose of this coursework is to develop a distributed chat system using a networking library.
#
# ===========
# S E R V E R
# ===========
##

##
# Imports
import datetime
import logging # Generate a log file to record all the changes made
import socket
from sys import argv, stdout
import os # For exiting of every thread
import re
from threading import Thread #Threading

##
# Configuration of the log file
logging.basicConfig(level=logging.INFO, filename='log/ChatApplication_server.log', format='[%(levelname)s] %(asctime)s %(message)s', )

##
# Inicialization
host = '127.0.0.1'
buffer_size = 12800
n_conection = 100 # Number of possible connection

active_connections = [] # User connected
inactive_connections = []
kick_connections = [] # Users that has been kicked

##
# First iteration between the client and the server.
# The server will ask for the credentials of the user identifiying if it needs
# to be registered or logged
#
# @param client_sock Raw socket introduced as a parameter
# @param client_ip_and_port A list of two slots with the ip and the port
#        of the client
#
# @exception if the conecction with the socket is interrupted
def connect_client(client_sock, client_ip_and_port):
    client_sock.sendall('Connecting...\n')
    print 'A client [{}] is trying to connect...\n'.format(client_ip_and_port)
    client_ip = client_ip_and_port[0]
    client_port = client_ip_and_port[1]

    # if (not kick_connections.has_key(client_ip)):
    #     kick_connections[client_ip] = []

    credential_response = ask_credentials(client_sock)

    logging.info("User Login Info = {}".format(credential_response))

    user_name = credential_response[1]
    user_name = user_name[1]

    if (credential_response[0] == 'y'):
        if (credential_response[1][0] == True):
            print 'USER:%s with IP:%s has join the room for the first time\n' %(credential_response[1][1], client_ip)
            client_sock.sendall('<Server>: You have entered the room\n')
            client_sock.sendall('==================< >==================')

            try:
                while 1:
                    message = client_sock.recv(buffer_size)
                    check_message(user_name, message)
            except:
                client_logout(client_sock)
                client_exit(client_sock, client_ip, client_port)
        else:
            client_sock.sendall("<Server>: ERROR 1 -> The username CAN'T exist in the database, try again")
            connect_client(client_sock, client_ip_and_port)


    elif (credential_response[0] == 'n'):
        if (credential_response[1][0] == True):
            print 'USER with IP has join the room\n'
            client_sock.sendall('<Server>: Welcome back {} \n'.format(credential_response[1][1]))
            client_sock.sendall('==================< >==================')
            try:
                while 1:
                    message = client_sock.recv(buffer_size)
                    check_message(user_name, message)
            except:
                client_logout(client_sock)
                client_exit(client_sock, client_ip, client_port)
        else:
            client_sock.sendall("<Server>: ERROR 2 -> The credentials are incorrect")
            connect_client(client_sock, client_ip_and_port)

    else:
        print 'USER:%s with IP:%s has problems trying to connect. Please try again\n' %(credential_response[1][1], client_ip)
        client_sock.sendall('<Server>: You had problems to connect. Please try again\n')
        connect_client(client_sock, client_ip_and_port)

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
def ask_credentials(client_sock): #TODO Add (client_ip, client_port) in parameters for a timer
    client_sock.sendall('<Server>: Do you want to create a new user? [y/n]')
    response = client_sock.recv(buffer_size)

    if (response == 'y'): #YES
        return ('y', create_user(client_sock) )

    elif (response == 'n'): #NO
        return ('n', login_user(client_sock))
    else:
        #Default
        client_sock.sendall('<Server>: Error, you must respond with "y" saying yes or "n" saying no.\n')
        ask_credentials(client_sock)

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

    answer = (False, user_name)

    with open('database/users_credentials.txt', 'r') as rDoc:
        data = rDoc.readlines()
        words = ['Void']
        for line in data:
            words = line.split('\n')
        print words

    if (not(user_name == "admin") or not(user_name in database_doc)):
        if (user_password == user_password_2):
            with open('database/users_credentials.txt', 'a') as aDoc:
                aDoc.write('\n' + user_name + ';' + user_password) #TODO encrypt password

            print '%s Has join the party.\n' %user_name
            answer = (True, user_name)
        else:
            client_sock.sendall('<Server>: The password are not the same, please try again')
            answer = (False, user_name)
            ask_credentials(client_sock)
    else:
        client_sock.sendall('<Server>: You must choose another username')
        answer = (False, user_name)
        ask_credentials(client_sock)
    aDoc.close() # Close document
    return answer

def login_user(client_sock):
    client_sock.sendall('<Server>: Write your user name:')
    user_name = client_sock.recv(buffer_size)
    client_sock.sendall('<Server>: Write your password:')
    user_password = client_sock.recv(buffer_size)

    answer = (False, user_name)

    with open('database/users_credentials.txt', 'r') as rDoc: #TODO
        database_doc_list = rDoc.readlines()

    database_doc_list = map(lambda each:each.strip("\n"), database_doc_list) # Eliminate '\n' from our list
    #print database_doc_list

    i = 0
    while (answer[0]==False and i < len(database_doc_list) ):
            sublist = database_doc_list[i].split(';')
            #print "SUBLIST: " + format(sublist)
            if ((user_name == "admin") or (user_name == sublist[0])):
                if (user_password == sublist[1]):
                    answer = (True, user_name)
            else:
                answer = (False, user_name)
            i = i + 1

    rDoc.close() # Close the document
    return answer


def client_logout(client_sock):
    client_sock.sendall("<Server>: You has been disconnected by the server")
    client_sock.sendall(">exit")
    stdout.flush()
    client_sock.close()

def client_exit(client_sock, client_ip, client_port):
    print 'Client on %s : %s disconnected' %(client_ip, client_port)
    stdout.flush()
    client_sock.close()

def check_message(user_name, message):
    if (message.startswith('/')):
        check_command(message)
    else:
        currentDT = datetime.datetime.now()
        print currentDT.strftime("%I:%M %p | ")+ user_name + ": "+ message

def check_command(message):
    if (message.startswith('/viewusers')):
        print_list(active_connections)
    elif (message.startswith('/messageto')):
        print e
    elif (message.startswith('/changepassword')):
        print e
    elif (message.startswith('/busy')):
        print e
    elif (message.startswith('/free')):
        print e
    elif (message.startswith('/seegrant')):
        print e
    elif (message.startswith('/kickuser')):
        print e
    elif (message.startswith('/restart')):
        print e
    elif (message.startswith('/senddata')):
        print e
    elif (message.startswith('/disconnect')):
        print e
    elif (message.startswith('/help')):
        print e
    else:
        print "<Server>: [Error typing] Type '/help' see all possible commands"

##
# Print a list in a formated way
#
# @list A list inputed as parameter
# TODO: Change output format
def print_list(list):
    i = 0
    while (len(list)):
        print format(list[i])
        i = i + 1

##
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

            # Adding the client in the list of conecction
            client_data = [addr[0], addr[1]]
            active_connections.append(client_data)

            stdout.flush() # Clean

            #THREADIND
            server_t = Thread(target=connect_client, args=(client_connection, addr))
            server_t.start()

    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        #TODO for every ip we must close the socket. We can see them in one of the conecction arrays
        client_exit(sock, addr[0], addr[1])
    #    sock.shutdown(1)
        sock.close()
        print "\nSever down ==================\n"
        os._exit(1)

main(argv)

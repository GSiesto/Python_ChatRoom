# -*- coding: utf-8 -*-
##
# University of the West of Scotland
# Author: Guillermo Siesto Sanchez B00334584
# Date: 2018
# Description: The purpose of this coursework is to develop a distributed chat system using a networking library.
#
# ===========
# C L I E N T
# ===========
##

##
# Imports
import logging # Generate a log file to record all the changes made
from socket import socket, AF_INET, SOCK_STREAM
from sys import argv, stdout
import os # For exiting of every thread
from threading import Thread #Threading

##
# Config
logging.basicConfig(level=logging.INFO, filename='log/ChatApplication_client.log', format='[%(levelname)s] %(asctime)s %(message)s', )

##
# Inicialization
free = True
kick = False
grant = 1 # 0 = Superuser ; 1 = Normaluser
connected = False # We must control if the conecction is on for exiting the thread if neccesary
buffer_size = 12800

##
# Send a general message to the common room
def send_message(sock, server_ip):
    try:
        while 1:
            message = raw_input()
            sock.sendall(message)
    except:
        # ^C Control
        print "] Forced exit when sending message"
        connected = False
        exit()

##
# Receive a message thought the socket and process it
def receive_message(sock, server_ip):
    try:
        while (1) and  (kick == False) and (free == True):
            message = sock.recv(buffer_size)
            if (message.startswith(">")):
                check_command(sock, message)
                stdout.flush() # Clean
            else:
                print message
                stdout.flush() # Clean
    except:
        # ^C Control
        print "] Forced exit when receiving message"
        connected = False
        exit()

def check_command(sock, message):
    if (message.startswith(">kick")):
        kick = True
        print "] You have been Kicked by an administrator"

    elif (message.startwith(">busy")):
        Free = False
        print "] You declared yourself as: Busy"

    elif (message.startwith(">free")):
        Free = True
        print "] You declared yourself as: Free"

    elif (message.startwith(">changegrant")):
        if (message.startwith(">changegrant 0")):
            grant = 0
            print "] Grant chages to: SuperUser"
        elif (message.startwith(">changegrant 1")):
            grant = 1
            print "] Grant chages to: Normaluser"
        else:
            print "] ERROR with commands *changegrant* in client side"

    else:
        print "] ERROR handling commands in client side"

def exit():
    print "] Exit function"
    connected = False
    stdout.flush()
    os._exit(1)

##
# Main
def main(argv):
    server_ip = argv[1]
    server_port = int(argv[2])

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((server_ip, server_port))
    connected = True

    #============== 2 Active Threads
    #THREADIND
    #Thread for Sendind
    sending_t = Thread(target=send_message, args=(sock, server_ip))
    sending_t.start()
    #Thread for Receiving
    receiving_t = Thread(target=receive_message, args=(sock, server_ip))
    receiving_t.start()

    try:
        while True:
            if (connected == False):
                print "] Exit because disconnection"
                exit()
                os._exit(1) #Exit on Keyboard Interrupt
    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        print "] Forced exit by (KeyboardInterrupt or SystemExit) exception"
        logging.info("] Forced exit by (KeyboardInterrupt or SystemExit) exception")
        exit()


main(argv)

# University of the West of Scotland
# Author: Guillermo Siesto Sanchez B00334584
# Date: 2018
# Description: The purpose of this coursework is to develop a distributed chat system using a networking library.

# ===========
# C L I E N T
# ===========

# Imports
import logging # Generate a log file to record all the changes made
from socket import socket, AF_INET, SOCK_STREAM
from sys import argv, stdout
import os # For exiting of every thread
from threading import Thread #Threading

# Config
logging.basicConfig(level=logging.INFO, filename='log/ChatApplication_client.log', format='[%(levelname)s] %(asctime)s %(message)s', )

# Inicialization
free = True
kick = False
grant = 1 # 0 = Superuser ; 1 = Normaluser
connected = False # We must control if the conecction is on for exiting the thread if neccesary
buffer_size = 12800

def send_message(sock, server_ip):
    try:
        while 1:
            message = raw_input()
            sock.sendall(message)
    except:
        # ^C Control
        stdout.flush()
        sock.close()
        connected = False
        os._exit(1)

def receive_message(sock, server_ip):
    try:
        while 1:
            message = sock.recv(buffer_size)
            print message
            stdout.flush() # Clean
    except:
        # ^C Control
        stdout.flush()
        sock.close()
        connected = False
        os._exit(1)

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
            if (not connected):
                os._exit(1) #Exit on Keyboard Interrupt
    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        sock.close()
        print '\nConnection to server closed' #Close server
        logging.info("Connection to server closed")
        os._exit(1)


main(argv)

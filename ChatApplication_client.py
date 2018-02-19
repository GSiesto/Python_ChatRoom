# -*- coding: utf-8 -*- #

##
# University of the West of Scotland
# Author: Guillermo Siesto Sanchez B00334584
# e-Mail: b00334684 at studentmail.uws.ac.uk
# Date: 2018
# Description: The purpose of this coursework is to develop a distributed
#   chat system using a networking library.
#
# ===========
# C L I E N T
# ===========
##

##
# Imports
import logging      # Generate a log file to record all the changes made
from socket import socket, AF_INET, SOCK_STREAM
from sys import argv, stdout
import os           # For exiting of every thread
from threading import Thread    # Threading
import threading

##
# Config
logging.basicConfig(level=logging.INFO,
                    filename='log/ChatApplication_client.log',
                    format='[%(levelname)s] %(asctime)s %(message)s', )

##
# Inicialization
free = True
grant = 1               # 0 = Superuser ; 1 = Normaluser
connected = False       # For wxiting the thread
buffer_size = 12800

##
# Locks ⚩
lock = threading.RLock()


##
# Send a general message to the common room
def send_message(sock, server_ip):
    try:
        global connected
        with lock:
            tmp = connected
        while (tmp):     # TODO connected and ...
            message = raw_input()
            msg = message
            sock.sendall(msg)
    except ():
        # ^C Control
        print "] Forced exit when sending message"
        with lock:      # =========================== ⚩
            connected = False
            print "} ESTATE of connected:" + format(connected)
        exit()


##
# Receive a message thought the socket and process it
def receive_message(sock, server_ip):
    try:
        global connected
        with lock:
            tmp = connected
        while (tmp):
            message = sock.recv(buffer_size)
            msg = message
            if (msg.startswith(">")):
                print "] Command received"
                check_command(sock, msg)
                stdout.flush()      # Clean
            else:
                if (free):
                    print msg
                    stdout.flush()  # Clean
                else:
                    stdout.flush()  # Clean
    except ():
        # ^C Control
        print "] Forced exit when receiving message"
        with lock:      # =========================== ⚩
            connected = False
            print "} ESTATE of connected:" + format(connected)
        exit()


def check_command(sock, message):
    try:
        global free
        global grant
        with lock:
            msg = message
            print "MESSAGE: " + msg
            if msg.startswith(">kick"):     # Also using disconnect
                print "] You have been Kicked by an administrator"
            elif msg.startswith(">info"):
                print "SOY UNA INFORMACION MUY BONITA"
                stdout.flush()      # Clean
            elif msg.startswith(">disconnect"):
                with lock:      # =========================== ⚩
                    global connected
                    connected = False
                    print "} ESTATE of connected:" + format(connected)
                    print "] You have been disconnected"
            elif msg.startswith(">busy"):
                print "] You declared yourself as: Busy"
                free = False
            elif msg.startswith(">free"):
                print "] You declared yourself as: Free"
                free = True
            elif msg.startswith(">changegrant"):
                if msg.startswith(">changegrant 0"):
                    grant = 0
                    print "] Grant chages to: SuperUser"
                elif msg.startswith(">changegrant 1"):
                    grant = 1
                    print "] Grant chages to: Normaluser"
                else:
                    print "] ERROR with commands *changegrant* in client side"
            else:
                print "] ERROR typing commands in client side from server side"
    except ():
        print "] Exception on command checking"


def exit():
    print "] Exit function"
    with lock:      # =========================== ⚩
        global connected
        connected = False
        print "} ESTATE of connected:" + format(connected)
    stdout.flush()
    os._exit(1)


##
# Main
def main(argv):
    server_ip = argv[1]
    server_port = int(argv[2])

    sock = socket(AF_INET, SOCK_STREAM)

    sock.connect((server_ip, server_port))
    with lock:      # =========================== ⚩
        global connected
        connected = True
        print "} ESTATE of connected:" + format(connected)

    print "****PRIMER LOCK SUELTITO HIHIHI!"

    # ============== 2 Active Threads
    # THREADIND
    # Thread for Sendind
    sending_t = Thread(target=send_message, args=(sock, server_ip))
    sending_t.start()
    # Thread for Receiving
    receiving_t = Thread(target=receive_message, args=(sock, server_ip))
    receiving_t.start()

    try:
        while (1):
            if (not connected):
                print "] Exit because disconnection"
                exit()
                os._exit(1)     # Exit on Keyboard Interrupt
    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        print "] Forced exit by (KeyboardInterrupt or SystemExit) exception"
        logging.info(
            "] Forced exit by (KeyboardInterrupt or SystemExit) exception")
        exit()


main(argv)

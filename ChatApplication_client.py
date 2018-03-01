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
import threading    # Threading
from ftplib import FTP

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
server_ip = "localhost"
server_port = 9797

##
# Lock
lock = threading.RLock()



##
# Send a general message to the common room
def send_message(sock):
    global connected
    try:
        while connected:
            message = raw_input()
            with lock:
                sock.sendall(message)
        print "\Sending finished"
    except ():
        print "] Forced exit when sending message"
        connected = False
        print "} ESTATE of connected:" + format(connected)
        exit()


##
# Receive a message thought the socket and process it
def receive_message(sock):
    global connected
    try:
        while connected:
            message = sock.recv(buffer_size)
            if (message.startswith(">")):
                print "] Command received"
                with lock:
                    check_command(sock, message)
            else:
                if (free):
                    print message
            stdout.flush()
        print "\Receiving finished"

    except ():
        print "] Forced exit when receiving message"
        connected = False
        print "} ESTATE of connected:" + format(connected)
        exit()


def transfer_file(message, direction):
    output_path = 'files'
    try:
        ftp = FTP('')
        global server_ip
        global server_port
        ftp.connect(server_ip, server_port)
        ftp.login()
        ftp.cwd(output_path)    # Output irectory
        ftp.retrlines('LIST')

        if (direction == 'u'):
            upload_file(protocol=ftp, location=message)
        else:
            download_file(protocol=ftp, name=message)

    except ():
        print "] Forced exit in transfer_file()"
        connected = False
        print "} ESTATE of connected:" + format(connected)
        exit()


def upload_file(protocol, path2file):
    input_path = location
    try:
        file = open(input_path, 'rb')
        protocol.storbinary('STOR '+input_path, file)
        print "] STORING the file: " + input_path
        protocol.quit()
        file.close()
    except():
        print "] Forced exit in upload_file()"
        connected = False
        print "} ESTATE of connected:" + format(connected)
        exit()

def download_file(protocol, name):
    try:
        filename = 'files/%s' % (name)   # Path of file
        localfile = open(filename, 'wb')
        protocol.retrbinary('RETR ' + filename, localfile.write, 1024)
        protocol.quit()
        localfile.close()
    except():
        print "] Forced exit in dowanload_file()"
        connected = False
        print "} ESTATE of connected:" + format(connected)
        exit()

def check_command(sock, message):
    global connected
    global free
    global grant
    try:
        msg = message
        print "MESSAGE: " + msg
        if msg.startswith(">kick"):     # Also using disconnect
            print "] You have been Kicked by an administrator"
        elif msg.startswith(">info"):
            print "SOY UNA INFORMACION MUY BONITA"
            stdout.flush()      # Clean
        elif msg.startswith(">disconnect"):
            connected = False
            print "} ESTATE of connected:" + format(connected)
            print "] You have been disconnected"
        elif msg.startswith(">uploadfile"):
            file_t = threading.Thread(target=transfer_file, args=(msg, 'u')).start()
            # Maybe Daemon
        elif msg.startswith(">downloadfile"):
            file_t = threading.Thread(target=transfer_file, args=(msg, 'd')).start()
            # Maybe Daemon
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
    try:
        print "] Exit function"
        print "} ESTATE of connected:" + format(connected)
    except (SystemExit, SystemError):
        print "] Forced exit because of (SystemExit) or (SystemError)"
    # os._exit(1)


##
# Main
def main(argv):
    try:
        global server_ip
        global server_port
        server_ip = argv[1]
        server_port = int(argv[2])

        sock = socket(AF_INET, SOCK_STREAM)

        sock.connect((server_ip, server_port))

        global connected
        connected = True
        print "} ESTATE of connected:" + format(connected)

        # ============== 2 Active Threads
        # Thread for Sendind
        sending_t = threading.Thread(target=send_message, args=(sock,))
        # sending_t.daemon = True
        sending_t.start()

        # Thread for Receiving
        receiving_t = threading.Thread(target=receive_message, args=(sock,))
        # receiving_t.daemon = True
        receiving_t.start()

        sending_t.join()
        receiving_t.join()

        with lock:
            sock.close()

        exit()

    except (KeyboardInterrupt):     # ^C Control
        print "] Forced exit by (KeyboardInterrupt) exception"
        stdout.flush()
        logging.info(
            "] Forced exit by (KeyboardInterrupt) exception")


main(argv)

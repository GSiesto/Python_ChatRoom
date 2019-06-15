# Chat Room forged in Python

Client Server Architecture

Author: Guillermo Siesto Sánchez

*Client Server Architecture, Computer Science,
University of the West of Scotland
Paisley, Scotland. 2018*

[TOC]

## Project description

The structure of the project is divided in **two main python programs**, one for the *server* and other for the *client* or clients (each client will execute the client). In addicHon it has been added a log for beWer understanding of system failures, and a database with an encrypted file for the record of the users and password that use the system. 

**A lot of users can connect** and communicate with the server while it is acHve. As it has been using ***threading***, it would be a big problem for efficiency.

![Estructure](https://user-images.githubusercontent.com/6242946/59555000-3f42cc80-8fac-11e9-9380-03a0c95189c8.png)

## Chat diagram

### Server

![Server](https://user-images.githubusercontent.com/6242946/59555004-436eea00-8fac-11e9-82b3-f61c39af6fb5.png)

The server start **connecting the client**, prepare the socket and check if the connection is possible. Then **the credentials will be asked**, for differencing if a user is going to **login** **or** to **register**. The program will **check if the user exist**, **read or write** in an **encryption** mode into the database file (user_credentials.enc). **The connection will be open** and the server will be prepared to start receiving and handling process between the different client connected. **Each connection is a thread** for performance help. When the server want to exit, first it will close all the open connection notifying each client, and then the program will *exit* without leaving open sockets.

### Client

![Client](https://user-images.githubusercontent.com/6242946/59555008-4669da80-8fac-11e9-9988-7c72efeac528.png)

**Two thread will be running simultaneously for sending and receiving** messages and specific character of information. The receiving method at the same time will be **checking if the message receive is a command** for calling to the server specific methods. When the client decide to live, all the tread will die and the connection will be closed.

## Design Process

1. Analyze the information given by the teacher in the lecture classes.

2. Study the steps and layers that our server and client should have:

3. 1. Communication layers.
   2. Protocols.
   3. Message control.
   4. Command control.
   5. File Control (Writing/Reading).

4. Document all the process.

*The decision of which part should contain the client and the server was seen as trying to put all the weight on the server side, the client will only receive and send message or special symbols to communicate with the functions stored in the server. The diagram contains information about how it was though when developing each part of the project.*

## Documentation

### Client

| **Client functions**         |                                                              |
| ---------------------------- | ------------------------------------------------------------ |
| send_message(sock)           | *INPUT: socket with the connection.* *Waiting in a loop checking if a message is input in the command line.* |
| receive_message(sock)        | *INPUT: socket with the connection.* *Checking in a loop if message is receive though the socket.* |
| check_command(sock, message) | *INPUT: socket with the connection, Message received.* *The function will check if the message is a command starting by the symbol ‘>’.* |
| exit()                       | *INPUT: none* *The threads will die, and the application will be closed.* |

### Server

| **Server functions**                               |                                                              |
| -------------------------------------------------- | ------------------------------------------------------------ |
| connect_client(client_sock, client_ip_and_port)    | *INPUT: socket with the connection, IP direction and port where the client is.* *The connection with the socket will be stabilized.* |
| open_connection(client_sock, user_name, direction) | *INPUT: socket with the connection, name of the user connected, IP direction where the client is.* *The connection will be open.* |
| ask_credentials(client_sock)                       | *INPUT: socket with the connection.* *A message will appear in the client console asking for a response:* *‘y’: He want to create a new username (register).* *’n’: He has a username and want to login.* **RETURN***:* *(char, Boolean)*  *Char. ‘y’ or ’n’* *The return of the functions*  *Create_user()* *Login_user()* |
| create_user(client_sock)                           | *INPUT: socket with the connection.* *A user will be created and written in the database. it will be stored with encryption.* **RETURN***:*  *TRUE: If possible to create a user.* *FALSE: If not possible (it is not allowed to have more than one user).* |
| encrypt_txt(p_text)                                | *INPUT: plain text to encrypt.* *The text will be encrypted*  **RETURN***:*  *Encrypted text* |
| decrypt_list(p_list):                              | *INPUT: p_list is a list with pain text.* *Every element on the list will be encrypted* **RETURN***:* *A list with all the element encrypted.* |
| check_password(user_name, password)                | *INPUT: user name, password of the user.* **RETURN***:*  *False: if the information is not the same on the database* *True: if the information is correct.* |
| login_user(client_sock)                            | *INPUT: socket with the connection.* **RETURN***:*  *False: if the information is not the same on the database* *True: if the information is correct.* |
| client_exit(client_sock):                          | *INPUT: socket with the connection.* *The socket will be closed.* |
| clients_exit(client_sock)                          | *INPUT: socket with the connection.* *All the client connected will be disconnected closing the sockets in the process.* |
| check_message(client_sock, user_name, message)     | *INPUT: socket with the connection. Username, message.* *Check what is being introduced.* |
| check_command(client_sock, user_name, message)     | *INPUT: socket with the connection.* *Check if the input is a command starts with ‘/‘* |
| message_to(client_sock, message)                   | *INPUT: socket with the connection. Message inputed in raw.* *A private message will be send to a specific user (it is still in the message parameter)* |
| kick_user(client_sock, message)                    | *INPUT: socket with the connection.* *A user will be disconnected and added to the kick connection list.* |
| change_grant(client_sock, user_name, message)      | *INPUT: socket with the connection, username, message in raw with the username to change and grant to put.* *The role of a specific user will be change.* |
| get_user_grant(user_name)                          | *INPUT: Username.* **RETUN***: Grant of the user (role).*    |
| set_user_grant(user_name, new_grant)               | *INPUT: username, new role to put.* *This function will set the role of the user to the new introduced as a parameter.* |
| get_user_index(user_name)                          | *INPUT: socket with the connection.* **RETURN***: the index in the active connection list where the user is stored temporally (RAM).* |
| get_socket_index(socket)                           | *INPUT: socket with the connection.* **RETURN***: the index in the socket connection list where the user is stored temporally (RAM).* |
| print_list_client(client_sock, list)               | *INPUT: socket with the connection.* *It will print in the client screen a list of connected users formatted.* |

### External Libraries

Library of cryptography (External): *(c) 2012-2015 Andrew Cooke,* [*andrew@acooke.org*](/var/folders/gv/m9qg9mxx595fr2xd3y3lt03c0000gn/T/abnerworks.Typora/2E4EDAD5-9FF5-4AB2-A2C2-C45569CE62B0/mailto:andrew@acooke.org)*; 2013* [*d10n*](https://github.com/d10n)*,* [*david@bitinvert.com*](/var/folders/gv/m9qg9mxx595fr2xd3y3lt03c0000gn/T/abnerworks.Typora/2E4EDAD5-9FF5-4AB2-A2C2-C45569CE62B0/mailto:david@bitinvert.com)*. Released into the public domain for any use, but with absolutely no warranty.* Available at: https://github.com/andrewcooke/simple-crypt Accessed on 24 of March of 2018.

## How to use

### Running the program

Firstly, the server

```python ChatApplication_server.py```

*It will run on **port 9797** by default*

Then the client, each time for each client you want to run

```python CharApplication_client.py [IP] [PORT]```

### Commands

```
/help
/viewusers
/messageto (username) (message)
/busy
/free
/changegrant (username) (0/1)
/kickuser (username)
/viewkickusers
/restart
/disconnect
```

## Example

Two clients communicating in one server

![Example](https://user-images.githubusercontent.com/6242946/59555011-4d90e880-8fac-11e9-826f-c774569a8ede.png)
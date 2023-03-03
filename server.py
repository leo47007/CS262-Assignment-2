'''
This file implements server functionality of chat application.

Usage: python3 server.py
'''
# Import relevant python packages
from collections import defaultdict
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
import random

# Constants/configurations
ENCODING    = 'utf-8' # message encoding
BUFFER_SIZE = 2048 # fixed 2KB buffer size
PORT        = 1234 # fixed application port

SERVER_IP      = '10.250.59.1' # REPLACE ME with output of ipconfig getifaddr en0
MAX_CLIENTS    = 100
LOGIN_ATTEMPTS = 3

# Record the socket for each client
client_socket = {}
# Remove sock from active sockets
def remove_connection(sock, active_sockets):
    assert sock in active_sockets, 'ERROR: remove_connection encountered corrupted active_sockets'
    active_sockets.remove(sock)
    sock.close()
    print('Removed Client {}from active sockets'.format(client_num))

# Thread for server socket to interact with each client user in chat application
def client_thread(sock, client_num, active_sockets):
    # Send client if to the client
    # sock.send('{}\n'.format(client_num).encode(encoding=ENCODING))
    while True:
        try:
            message = sock.recv(BUFFER_SIZE).decode(encoding=ENCODING)
            if message:
                recipient = int(message[0])
                print("Client {} send to client {}: {}".format(client_num, recipient, message[1:]))
                client_socket[recipient].send(message[1:].encode(encoding=ENCODING))            
        except:
            no_message = True
        # If we're unable to send a message, close connection.  
        # except:
        #     remove_connection(sock, addr, active_sockets)
        #     return

def main():
    # Creates server socket with IPv4 and TCP
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # allow for multiple clients

    # Remember to run 'ipconfig getifaddr en0' and update SERVER_IP
    server.bind((SERVER_IP, PORT))
    server.listen(MAX_CLIENTS) # accept up to MAX_CLIENTS active connections
    
    active_sockets = [] # running list of active client sockets
    '''
    'users' is a hashmap to store all client data
        - key: username
        - values: 'password', 'socket', 'mailbox'
    '''
    users = defaultdict(dict)
    client_num = 0
    while True:
        sock, client_addr = server.accept()
        active_sockets.append(sock) # update active sockets list
        print ('{}:{} connected'.format(client_addr[0], client_addr[1]))
        client_socket[client_num] = sock
        # Start new thread for each client user
        Thread(target=client_thread, args=(sock, client_num, active_sockets)).start()
        client_num += 1

if __name__ == '__main__':
    main()
'''
This file implements a single model machine.

Usage: python3 machine.py MACHINE_NUMBER
'''
# Import relevant python packages
from collections import deque
from random import randint
from select import select
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_SNDBUF
import sys
from threading import Thread
from time import sleep, time

# Constants/configurations
ENCODING           = 'utf-8' # message encoding
BUFFER_SIZE        = 2048 # fixed 2KB buffer size
IP_ADDRESS         = '10.250.189.114' # REPLACE ME with output of ipconfig getifaddr en0
BASE_PORT          = 1234 # base port of the first model machine
TOTAL_NUM_MACHINES = 3 # total number of model machines

assert TOTAL_NUM_MACHINES < BASE_PORT, 'BASE_PORT needs to be higher for more model machines'

# Creates server sockets for model machines that have higher machine number than you.
def create_server_sockets(my_machine_number):
    server_sockets = []
    for num in range(my_machine_number+1, TOTAL_NUM_MACHINES):
        port   = BASE_PORT * (my_machine_number+1) + num
        server = socket(AF_INET, SOCK_STREAM) # creates server socket with IPv4 and TCP
        server.bind((IP_ADDRESS, port))
        server.listen()
        server_sockets.append(server)
        print('({}-{}) server socket established @ {}:{}.'.format(my_machine_number, num, IP_ADDRESS, port))
    return server_sockets

# Creates and connects client sockets for model machines that have lower machine number than you.
def create_client_sockets(my_machine_number):
    client_sockets = []
    for num in range(my_machine_number):
        port   = BASE_PORT * (num+1) + my_machine_number
        client = socket(family=AF_INET, type=SOCK_STREAM) # creates client socket with IPv4 and TCP
        # client.setsockopt(SOL_SOCKET, SO_SNDBUF, BUFFER_SIZE)
        client.connect((IP_ADDRESS, port)) # connect to server socket
        client_sockets.append(client)
        print('({}-{}) client socket established @ {}:{}.'.format(num, my_machine_number, IP_ADDRESS, port))
    return client_sockets

# Listens for messages from sock and appends messages to network queue
def socket_thread(sock, message_queue, log_file):
    while True:
        message = sock.recv(BUFFER_SIZE)
        if message:
            clock_list = message.decode(encoding=ENCODING).split('.')
            for clock in clock_list[:-1]:
                message_queue.append(clock)
            # print('Message_Queue: {}'.format(message_queue))
        else:
            sys.exit('Connection lost with a model machine!')
# Main function for client functionality
def main():
    # Get machine number
    if len(sys.argv) != 2:
        print('Usage: python3 client.py MACHINE_NUMBER')
        sys.exit('machine.py exiting')

    machine_number = int(sys.argv[1])

    assert machine_number < TOTAL_NUM_MACHINES, 'Model machine number greater than expected total number of model machines'

    server_sockets = create_server_sockets(machine_number)
    client_sockets = create_client_sockets(machine_number)

    # Local data structures
    log_file      = open("log_{}.txt".format(machine_number), "w")
    clock_rate    = randint(1, 6)
    print ('Clock Rate is {}'.format(clock_rate))
    log_file.write('Clock Rate is {}\n'.format(clock_rate))
    message_queue = deque()
    logical_clock = 0

    # Make sure all server-client connections are made.
    for server_sock in server_sockets:
        client_sock, client_addr = server_sock.accept()
        # client_sock.setsockopt(SOL_SOCKET, SO_SNDBUF, BUFFER_SIZE)   
        client_sockets.append(client_sock)
        print ('{}:{} connected'.format(client_addr[0], client_addr[1]))

    for sock in client_sockets:
        Thread(target=socket_thread, args=(sock, message_queue, log_file)).start()

    while True:
        t_start = time()
        for _ in range(clock_rate):
            if message_queue:
                message = message_queue.popleft()
                message_clock = int(message)
                # print('Message, MSG_CLK, L_CLK: {}, {}, {}'.format(message, message_clock, logical_clock))
                logical_clock = max(logical_clock, message_clock) + 1
                # print("Received message. Global Time: {}, Message Queue Length: {}, Logical Clock Time: {}\n".format(time(), len(message_queue), logical_clock))
                # log_file.write("Received message. Global Time: {}, Message Queue Length: {}, Logical Clock Time: {}\n".format(time(), len(message_queue), logical_clock))
                log_file.write("{},{},{}\n".format(logical_clock, time(), len(message_queue)))
            else:
                dice = randint(1, 10)
                if dice == 1:
                    try:
                        # log_file.write('Clock I\'m Sending: '+str(logical_clock)+'\n')
                        client_sockets[0].send('{}.'.format(logical_clock).encode(encoding=ENCODING))
                    except:
                        print('DICE 1 ERROR')
                    logical_clock += 1
                    # log_file.write("Sent client 0. System Time: {}, Logical Clock Time: {}\n".format(time(), logical_clock))
                elif dice == 2:
                    try:
                        client_sockets[1].send('{}.'.format(logical_clock).encode(encoding=ENCODING))
                    except:
                        print('DICE 2 ERROR')
                    logical_clock += 1
                    # log_file.write("Sent client 1. System Time: {}, Logical Clock Time: {}\n".format(time(), logical_clock))
                elif dice == 3:
                    try:
                        client_sockets[0].send('{}.'.format(logical_clock).encode(encoding=ENCODING))
                        client_sockets[1].send('{}.'.format(logical_clock).encode(encoding=ENCODING))
                    except:
                        print('DICE 3 ERROR')
                    logical_clock += 1
                    # log_file.write("Sent to clients 0, 1. System Time: {}, Logical Clock Time: {}\n".format(time(), logical_clock))
                else:
                    logical_clock += 1
                    # log_file.write("Internal event. System Time: {}, Logical Clock Time: {}\n".format(time(), logical_clock))
                log_file.write("{},{},{}\n".format(logical_clock, time(), len(message_queue)))
        t_end = time()
        t_sleep = 1.0 - (t_end - t_start)
        sleep(t_sleep)
        log_file.flush()

if __name__ == '__main__':
    main()
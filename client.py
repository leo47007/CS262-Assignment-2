'''
This file implements client functionality of chat application.

Usage: python3 client.py IP_ADDRESS
'''
# Import relevant python packages
from select import select
from socket import socket, AF_INET, SOCK_STREAM
import sys
import random
import time



# Constants/configurations
ENCODING    = 'utf-8' # message encoding
BUFFER_SIZE = 2048 # fixed 2KB buffer size
PORT        = 1234 # fixed application port
TOTAL_NUM_MACHINES = 3
# Main function for client functionality
def main():
    # Get IP address and port number of server socket
    if len(sys.argv) != 3:
        print('Usage: python3 client.py IP_ADDRESS client_number')
        sys.exit('client.py exiting')
    ip_address = str(sys.argv[1])

    # Creates client socket with IPv4 and TCP
    client = socket(family=AF_INET, type=SOCK_STREAM)
    # Connect to server socket
    client.connect((ip_address, PORT))
    print('Successfully connected to server @ {}:{}'.format(ip_address, PORT))

    '''
    Inputs can come from either:
        1. server socket via 'client'
        2. client user input via 'sys.stdin'
    '''
    sockets_list = [sys.stdin, client]

    logical_clock = 0
    # FIFO queue
    message_q = []
    clock = random.randint(1, 2)
    initialize = False
    client_num = int(sys.argv[2])
    f = open("log_{}.txt".format(client_num), "w")

    while True:
        read_objects, _, _ = select(sockets_list, sockets_list, []) # do not use wlist, xlist
        for read_object in read_objects:
            # Recieved message from client user input

            message = read_object.recv(BUFFER_SIZE)
            message_q.append(message)
            # # Server socket has disconnected
            # if not message:
            #     print('Server @ {}:{} disconnected!'.format(ip_address, PORT))
            #     client.close()
            #     sys.exit('Closing application.')
            # else:
            #     print(message.decode(encoding=ENCODING))
            print(message.decode(encoding=ENCODING))
        # if not initialize:
        if len(message_q) > 0:
            message = message_q.pop()
            print(message.decode(encoding=ENCODING))
            # char = str(message[-1])
            # index = len(message)
            # while char.isdigit():
            #     index -= 1
            #     char = str(message[index])
            
            logical_clock  = max(logical_clock, int(message.decode(encoding=ENCODING))) + 1
            #  received a message, the global time (gotten from the system), the length of the message queue, and the logical clock time.
            print("Received message; global time: {}, the length of message queue: {}, logical clock time: {}\n".format(time.time(), len(message_q), logical_clock))
            f.write("Received message; global time: {}, the length of message queue: {}, logical clock time: {}\n".format(time.time(), len(message_q), logical_clock))
        else:
            dice = random.randint(1, 10)
            if dice == 1:
                recipient = (client_num + 1) % TOTAL_NUM_MACHINES
                client.send('{}{}'.format(recipient, logical_clock).encode(encoding=ENCODING))
                f.write("Send client {}; system time: {}, logical clock time: {}\n".format(recipient, time.time(), logical_clock))
            elif dice == 2:
                recipient = (client_num - 1) % TOTAL_NUM_MACHINES
                client.send('{}{}'.format(recipient, logical_clock).encode(encoding=ENCODING))
                f.write("Send client {}; system time: {}, logical clock time: {}\n".format(recipient, time.time(), logical_clock))
            elif dice == 3:
                recipient_1 = (client_num + 1) % TOTAL_NUM_MACHINES
                client.send('{}{}'.format(recipient_1, logical_clock).encode(encoding=ENCODING))
                recipient_2 = (client_num - 1) % TOTAL_NUM_MACHINES
                client.send('{}{}'.format(recipient_2, logical_clock).encode(encoding=ENCODING))
                f.write("Send to both client {} and client {}; system time: {}, logical clock time: {}\n".format(recipient_1, recipient_2, time.time(), logical_clock))
            else:
                f.write("Internal event; system time: {}, logical clock time: {}\n".format(time.time(), logical_clock))
            
            logical_clock += 1
        time.sleep(float(1/clock))
    f.close()

if __name__ == '__main__':
    main()
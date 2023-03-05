'''
This file launches an asynchronous distributed system with individual model machines.

Usage: python3 distributed_system.py NUM_MACHINES
'''
# Import relevant python packages
import os, sys
from subprocess import Popen

# Main function for distributed system functionality
def main():
    # Get number of machines
    if len(sys.argv) != 2:
        print('Usage: python3 distribued_system.py NUM_MACHINES')
        sys.exit('distributed_system.py exiting')

    num_machines = int(sys.argv[1])

    for num in range(num_machines):
        Popen(['python3', 'machine.py', '{}'.format(num)])

if __name__ == '__main__':
    main()
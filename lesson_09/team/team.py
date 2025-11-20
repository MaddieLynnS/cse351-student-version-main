""" 
Course: CSE 351
Team  : 
File  : Week 9 team.py
Author:  Luc Comeau
"""

# Include CSE 351 common Python files. 
from cse351 import *
import time
import random
import multiprocessing as mp

# number of cleaning staff and hotel guests
CLEANING_STAFF = 2
HOTEL_GUESTS = 5

# Run program for this number of seconds
TIME = 60

STARTING_PARTY_MESSAGE =  'Turning on the lights for the party vvvvvvvvvvvvvv'
STOPPING_PARTY_MESSAGE  = 'Turning off the lights  ^^^^^^^^^^^^^^^^^^^^^^^^^^'

STARTING_CLEANING_MESSAGE =  'Starting to clean the room >>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
STOPPING_CLEANING_MESSAGE  = 'Finish cleaning the room <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'

def cleaner_waiting():
    time.sleep(random.uniform(0, 2))

def cleaner_cleaning(id):
    print(f'Cleaner: {id}')
    time.sleep(random.uniform(0, 2))

def guest_waiting():
    time.sleep(random.uniform(0, 2))

def guest_partying(id, count):
    print(f'Guest: {id}, count = {count}')
    time.sleep(random.uniform(0, 1))

def cleaner(id, start_time: time, room_lock, clean_lock, cleaned_count):
    """
        get access to the room
    """
    while(time.time() < start_time + TIME):
        cleaner_waiting()
        with room_lock:
            print(STARTING_CLEANING_MESSAGE)
            cleaner_cleaning(id)
            print(STOPPING_CLEANING_MESSAGE)
            with clean_lock:
                cleaned_count.value += 1

def guest(id, start_time : time, room_lock, party_lock, party_people_lock, current_party_people, party_count):
    """
        get access to the room
        display message STARTING_PARTY_MESSAGE if this guest is the first one in the room
        Take some time partying (call guest_partying())
        display message STOPPING_PARTY_MESSAGE if the guest is the last one leaving in the room
    """
    while(time.time() < start_time + TIME):
        guest_waiting()
        # with room_lock:
        if (current_party_people.value == 0):
            room_lock.acquire()
            print(STARTING_PARTY_MESSAGE)
        with party_people_lock:
            current_party_people.value += 1
        guest_partying(id, current_party_people.value)
        with party_people_lock:
            current_party_people.value -= 1
        if (current_party_people.value == 0):
            print(STOPPING_PARTY_MESSAGE)
            room_lock.release()
            with party_lock:
                party_count.value += 1


def main():
    # Start time of the running of the program.
    start_time = time.time()

    # Create values to increment (globals won't work because processes do their own thing)
    cleaned_count = mp.Value('i', 0)
    party_count = mp.Value('i', 0)
    current_party_people = mp.Value('i', 0)

    # Create locks
    room_lock = mp.Lock()
    clean_lock = mp.Lock()
    party_lock = mp.Lock()
    party_people_lock = mp.Lock()

    # Create processes for cleaners and guests

    cleaner_threads = []
    for i in range(CLEANING_STAFF):
        p = mp.Process(target=cleaner, args=(i+1, start_time, room_lock, clean_lock, cleaned_count))
        p.start()
        cleaner_threads.append(p)

    party_threads = []
    for i in range(HOTEL_GUESTS):
        p = mp.Process(target=guest, args=(i+1, start_time, room_lock, party_lock, party_people_lock, current_party_people, party_count))
        p.start()
        party_threads.append(p)

    # TODO - add any variables, data structures, processes you need
    # TODO - add any arguments to cleaner() and guest() that you need
    # TODO - add two locks and figure out when to use them
    for p in cleaner_threads:
        p.join()

    for p in party_threads:
        p.join()


    # Results
    print(f'Room was cleaned {cleaned_count.value} times, there were {party_count.value} parties')


if __name__ == '__main__':
    main()

""" 
Course: CSE 351
Team  : Week 04
File  : team.py
Author: <Student Name>

See instructions in canvas for this team activity.

"""

import random
import threading

# Include CSE 351 common Python files. 
from cse351 import *

# Constants
MAX_QUEUE_SIZE = 10
PRIME_COUNT = 1000
FILENAME = 'primes.txt'
PRODUCERS = 3
CONSUMERS = 5

# ---------------------------------------------------------------------------
def is_prime(n: int):
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# ---------------------------------------------------------------------------
class Queue351():
    """ This is the queue object to use for this class. Do not modify!! """

    def __init__(self):
        self.__items = []
   
    def put(self, item):
        assert len(self.__items) <= 10
        self.__items.append(item)

    def get(self):
        return self.__items.pop(0)

    def get_size(self):
        """ Return the size of the queue like queue.Queue does -> Approx size """
        extra = 1 if random.randint(1, 50) == 1 else 0
        if extra > 0:
            extra *= -1 if random.randint(1, 2) == 1 else 1
        return len(self.__items) + extra

# ---------------------------------------------------------------------------
def producer(q: Queue351, space_available_sempaphore: threading.Semaphore, can_consume_semaphore: threading.Semaphore, barrier: threading.Barrier):
    for i in range(PRIME_COUNT):
        number = random.randint(1, 1_000_000_000_000)
        # TODO - place on queue for workers
        space_available_sempaphore.acquire()
        q.put(number)
        can_consume_semaphore.release()

    # TODO - select one producer to send the "All Done" message
    if barrier.wait() == 0:
        space_available_sempaphore.acquire()
        #for _ in range (Consumers):
        #q.put(None)
        q.put(None)
        can_consume_semaphore.release()

# ---------------------------------------------------------------------------
def consumer(q: Queue351, space_available: threading.Semaphore, can_consume: threading.Semaphore, f):
    while True:
    # TODO - get values from the queue and check if they are prime
        can_consume.acquire()
        item = q.get()
        space_available.release()
    # TODO - if "All Done" message, exit the loop
        if item is None:
         break
    # TODO - if prime, write to the file
        if is_prime(item):
            f.write(f"{item}\n")

    space_available.acquire()
    q.put(None)
    can_consume.release()

# ---------------------------------------------------------------------------
def main():

    random.seed(102030)

    que = Queue351()

    # TODO - create semaphores for the queue (see Queue351 class)
    space_available = threading.Semaphore(MAX_QUEUE_SIZE)
    consumer_spaces = threading.Semaphore(0)

    # TODO - create barrier
    b = threading.Barrier(PRODUCERS)

    # TODO - create producers threads (see PRODUCERS value)
    producer_threads = [threading.Thread(target=producer, args=(que, space_available, consumer_spaces, b)) for _ in range(PRODUCERS)]

    with open(FILENAME, 'w') as f:
    # TODO - create consumers threads (see CONSUMERS value)
        consumer_threads = [threading.Thread(target=consumer, args=(que, space_available, consumer_spaces, f)) for _ in range(CONSUMERS)]
        for t in producer_threads + consumer_threads:
            t.start() 
        for t in producer_threads + consumer_threads:
            t.join()

    

    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as f:
            primes = len(f.readlines())
    else:
        primes = 0
    print(f"Found {primes} primes. Must be 108 found.")



if __name__ == '__main__':
    main()

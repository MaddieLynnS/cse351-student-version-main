""" 
Course: CSE 351
Lesson: L01 Team Activity
File:   team.py
Author: Maddie Smith :)
Purpose: Find prime numbers

Instructions:

- Don't include any other Python packages or modules
- Review and follow the team activity instructions (team.md)


TODO 4) change range_count to 100007.  Does your program still work?  Can you fix it?
Question: if the number of threads and range_count was random, would your program work?
"""

from datetime import datetime, timedelta
import threading
import random

# Include cse 351 common Python files
from cse351 import *

# Global variable for counting the number of primes found
prime_count = 0
numbers_processed = 0

def is_prime(n):
    """
        Primality test using 6k+-1 optimization.
        From: https://en.wikipedia.org/wiki/Primality_test
    """
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

# class PrimeChecker(threading.Thread):
#     def __init__ (self, #insert all args from the original function):
#         threading.Thread.__init__(self)
#         #OR all of this:
#         super().__init__() --> This is making a new object of the super class
          #set all arguments from above
          #self.start = start
          #self.num_processed = 0
          #self.prime_count = 0
#     def run(self):
        #this is what happens when you do "t.start()"
        #pass in all arguments from above
        #process_range(self.start, self.end, etc) but very simplified:
        #update result, which you can get at the end

# this allows you to do t = PrimeChecker(//Insert all args from original function below)


def process_range(start, end, prime_lock, processed_lock):
    global prime_count                  # Required in order to use a global variable
    global numbers_processed            # Required in order to use a global variable
    # local_numbers_processed removes need for a lock here
    for i in range(start, end):
        processed_lock.acquire()
        numbers_processed += 1
        processed_lock.release()
        if is_prime(i):
            prime_lock.acquire()
            prime_count += 1
            prime_lock.release()
            print(i, end=', ', flush=True)
    print(flush=True)

    #you could use local things for each thread, then update the global variable down here:
    # with processed_lock: numbers_processed += local_numbers_processed
    # this one only has to lock once because it's outside of the range - only runs once per thread vs for each number up to 100_000

def main():

    log = Log(show_terminal=True)
    log.start_timer()

    start = 10000000000
    range_count = 100007
    incremement = range_count // 10
    #list of all threads
    threads = []

    # locks for critical sections that are being incremented
    prime_count_lock = threading.Lock()
    processed_nums_lock = threading.Lock()

    for i in range(0, 10):
        t = threading.Thread(target=process_range, args=(start, start + incremement, prime_count_lock, processed_nums_lock))
        #range_count/10, start + (range_count / 10 * i), which means I don't need an increment or to change start at all
    #iterate through list and start them all
        t.start()
        threads.append(t)
        start += incremement

    #iterate through list and join them all
    for t in threads:
        t.join()

    # Should find 4306 primes
    log.write(f'Numbers processed = {numbers_processed}')
    log.write(f'Primes found      = {prime_count}')
    log.stop_timer('Total time')


if __name__ == '__main__':
    main()

"""
Course: CSE 351 
Week: 8 Team
File:   team.py
Author: <Add name here>

Purpose: Solve the Dining philosophers problem to practice skills you have learned so far in this course.

Problem Statement:

Five silent philosophers sit at a round table with bowls of spaghetti. Forks
are placed between each pair of adjacent philosophers.

Each philosopher must alternately think and eat. However, a philosopher can
only eat spaghetti when they have both left and right forks. Each fork can be
held by only one philosopher and so a philosopher can use the fork only if it
is not being used by another philosopher. After an individual philosopher
finishes eating, they need to put down both forks so that the forks become
available to others. A philosopher can only take the fork on their right or
the one on their left as they become available and they cannot start eating
before getting both forks.  When a philosopher is finished eating, they think 
for a little while.

Eating is not limited by the remaining amounts of spaghetti or stomach space;
an infinite supply and an infinite demand are assumed.

The problem is how to design a discipline of behavior (a concurrent algorithm)
such that no philosopher will starve

Instructions:

        ****************************************************************
        ** DO NOT search for a solution on the Internet! Your goal is **
        ** not to copy a solution, but to work out this problem using **
        ** the skills you have learned so far in this course.         **
        ****************************************************************

Requirements you must Implement:

- [NEW] This is the same problem as last team activity, but with this new requirement: You will now implement a waiter.  
  When a philosopher wants to eat, it will ask the waiter if it can. If the waiter indicates that a
  philosopher can eat, the philosopher will pick up each fork and eat. There must not be a issue
  picking up the two forks since the waiter is in control of the forks and when philosophers eat.
  When a philosopher is finished eating, they will inform the waiter that he/she is finished. If the
  waiter indicates to a philosopher that they can not eat, the philosopher will wait between 1 to 3
  seconds and try to eat again.
- Use threads for this problem.
- Start with the PHILOSOPHERS being set to 5.
- Philosophers need to eat for a random amount of time, between 1 to 3 seconds, when they get both forks.
- Philosophers need to think for a random amount of time, between 1 to 3 seconds, when they are finished eating.
- You want as many philosophers to eat and think concurrently as possible without violating any rules.
- When the number of philosophers has eaten a combined total of MAX_MEALS_EATEN times, stop the
  philosophers from trying to eat; any philosophers already eating will put down their forks when they finish eating.
    - MAX_MEALS_EATEN = PHILOSOPHERS x 5

Suggestions and team Discussion:

- You have Locks and Semaphores that you can use:
    - Remember that lock.acquire() has arguments that may be useful: `blocking` and `timeout`.  
- Design your program to handle N philosophers and N forks after you get it working for 5.
- When you get your program working, how do you prove that no philosopher will starve?
  (Just looking at output from print() statements is not enough!)
- Are the philosophers each eating and thinking the same amount?
    - Modify your code to track how much eat philosopher is eating.
- Using lists for the philosophers and forks will help you in this program. For example:
  philosophers[i] needs forks[i] and forks[i+1] to eat (the % operator helps).
"""

import time
import threading
import queue
import random

PHILOSOPHERS = 5
MAX_MEALS_EATEN = PHILOSOPHERS * 5 # NOTE: Total meals to be eaten, not per philosopher!
MEALS_EATEN = 0

#controls whether it can eat or not
class Waiter():
    def __init__(self):
        pass

    def can_eat(self, left_fork: threading.Lock, right_fork: threading.Lock):
        #return true if both forks are available
        if left_fork.acquire() and right_fork.acquire():
            return True
        return False


class Philosopher(threading.Thread):
    def __init__(self, phil_index, forks_list, waiter: Waiter, meals_lock: threading.Lock):
        threading.Thread.__init__(self)
        self.phil_index = phil_index
        self.forks_list = forks_list
        self.waiter = waiter
        self.meals_lock = meals_lock
        # self.phil_queue = phil_queue
        #waiter lock

    def run(self):
        global MEALS_EATEN
        while MEALS_EATEN < MAX_MEALS_EATEN:
          #attempt to acquire both forks. If so, eat. If not, think
          #ask the Waiter class if they can eat
          left_fork : threading.Lock = self.forks_list[self.phil_index]
          right_fork : threading.Lock = self.forks_list[(self.phil_index + 1) % PHILOSOPHERS]
          if self.waiter.can_eat(left_fork, right_fork):
              # left_fork.acquire()
              # right_fork.acquire()
              self.eat()
              self.meals_lock.acquire()
              MEALS_EATEN += 1
              self.meals_lock.release()
              left_fork.release()
              right_fork.release()
              self.think()
          else:
              print("Does this even happen?")
    
    def eat(self):
        print(f'{self.phil_index} is eating')
        time.sleep(random.randint(1,3))
    
    def think(self):
        print(f'{self.phil_index} is thinking')
        time.sleep(random.randint(1,3))

def main():
    #Get an instance of the Waiter.
    waiter = Waiter()

    # Create the forks???
    forks_list = []
    for _ in range(PHILOSOPHERS):
        fork = threading.Lock()
        forks_list.append(fork)

    #Create lock for incrementing meals eaten
    meals_lock = threading.Lock()

    # Create PHILOSOPHERS philosophers.
    # phil_queue = queue.Queue
    phil_list = []
    for p in range(PHILOSOPHERS):
        t = Philosopher(p, forks_list, waiter, meals_lock)
        phil_list.append(t)

    # Start them eating and thinking.
    for t in phil_list:
        t.start()

    for t in phil_list:
        t.join()

    # TODO - Display how many times each philosopher ate.
    print(f"Finished!! We ate {MEALS_EATEN} times")


if __name__ == '__main__':
    main()

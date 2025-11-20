"""
Course: CSE 351 
Week: 07 Team
File:   team.py
Author: Maddie Smith :)

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
- When you get your program working, how to you prove that no philosopher will starve?
  (Just looking at output from print() statements is not enough!)
- Are the philosophers each eating and thinking the same amount?
    - Modify your code to track how much each philosopher is eating.
- Using lists for the philosophers and forks will help you in this program. For example:
  philosophers[i] needs forks[i] and forks[(i+1) % PHILOSOPHERS] to eat (the % operator helps).
"""

import time
import random
import threading
import queue

PHILOSOPHERS = 5
MAX_MEALS_EATEN = PHILOSOPHERS * 5 # NOTE: Total meals to be eaten, not per philosopher!
MEALS_EATEN = 0


# TODO - Make Philosopher a threaded class??
class Philosopher(threading.Thread):
    def __init__(self, phil_index, forks_list):
        super().__init__
        self.phil_index = phil_index
        self.forks_list = forks_list
        self.eat_times = 0
    # def __init__(self, first_fork: threading.Lock, second_fork: threading.Lock):
    #     self.first_fork = first_fork
    #     self.second_fork = second_fork

    def run(self):
        while True:
          if self.eat():
              self.eat_times +=1
          self.think()

    def eat(self):
        first_fork: threading.Lock = self.forks_list[self.phil_index]
        second_fork: threading.Lock = self.forks_list[(self.phil_index + 1) % PHILOSOPHERS]
        #attempt to acquire the forks that they need
        acquire_first_fork = first_fork.acquire(random.randint(1,3))
        acquire_second_fork = second_fork.acquire(random.randint(1,3))
        #if acquire both, eat for random amount of time, then release locks
        if(acquire_first_fork and acquire_second_fork):
            time.sleep(random.randint(1,3))
            first_fork.release()
            second_fork.release()
        #return true if they were able to eat, false if not
            return True
        return False

    def think():
        time.sleep(random.randint(1,3))
        


def main():
    # TODO - Create the forks.
    forks_list = []
    for _ in range(PHILOSOPHERS):
        fork = threading.Lock()
        print(f"{_}: fork")
        forks_list.append(fork)

    # TODO - Create PHILOSOPHERS philosophers and add them to a priority queue.
    philosopher_queue = queue.PriorityQueue()
    for _ in range(PHILOSOPHERS):
        t = Philosopher(_, forks_list)
        philosopher_queue.put(t)
        
    # TODO - Start them eating and thinking.
    for t in philosopher_queue:
        t.start()

    while (MEALS_EATEN < MAX_MEALS_EATEN):
        for t in philosopher_queue:
            MEALS_EATEN += t.eat_times
    

    # TODO - Display how many times each philosopher ate.
    for t in philosopher_queue:
        t.join()
        print(t.eat_times)
        


if __name__ == '__main__':
    main()

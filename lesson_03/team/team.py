"""
Course: CSE 351 
Lesson: L03 team activity
File:   team.py
Author: <Add name here>

Purpose: Retrieve Star Wars details from a server

Instructions:

- This program requires that the server.py program be started in a terminal window.
- The program will retrieve the names of:
    - characters
    - planets
    - starships
    - vehicles
    - species

- the server will delay the request by 0.5 seconds

TODO
- Create a threaded function to make a call to the server where
  it retrieves data based on a URL.  The function should have a method
  called get_name() that returns the name of the character, planet, etc...
- The threaded function should only retrieve one URL.
- Create a queue that will be used between the main thread and the threaded functions

- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""
#sentinel?? 

from datetime import datetime, timedelta
import threading
import concurrent.futures
import queue
from common import *

# Include cse 351 common Python files
from cse351 import *

class ServerRequest(threading.Thread):
    def __init__ (self, url):
        super().__init__()
        self.url = url
        self.call_count = 0
        self.name = ''

    def run(self):
        item = get_data_from_server(self.url)
        self.name = item['name']
        print(self.name)
        self.call_count += 1


def get_urls(q, print_lock, call_count):

    threads = []
    while True:
        curr_url = q.get()
        if curr_url is None:
            break
        t = ServerRequest(curr_url)
        t.start()
        threads.append(t)

    #then join all the threads
    #what if we want them to actually print according to group? We're gonna need a lock unfortunately

    print_lock.acquire()
    for t in threads:
        t.join()
        call_count +=1
    print_lock.release()
    return call_count

def add_urls_to_queue(q, film, category):
    for url in film[category]:
        q.put(url)
    #q.put(None) -> Wrong place to have this- it will add the None after every category

def main():
    call_count = 0
    # THREADS = 100 -- experiment with this and make sure I understand it
    q = queue.Queue()
    print_lock = threading.Lock()

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film6 = get_data_from_server(f'{TOP_API_URL}/films/6')
    call_count += 1
    print_dict(film6)
    # threads = [threading.Thread(target=read_queue, args=(q,)) for _ in range(THREADS)]
    # when doing it this way, you'll need None for every single thread

    for x in ['characters','planets','starships','vehicles','species']:
        add_urls_to_queue(q, film6, x)
    q.put(None)

    end_call_count = get_urls(q,print_lock,call_count)

    #THIS IS HOW TO DO THREAD POOLS
    # with concurrent.futures.ThreadPoolExecutory(max_workers=10) as executor:
    #     executor.map(get_urls, [(film6,'characters', print_lock),
    #                             (film6,'planets', print_lock)]) #second argument is the iterables, so you have to pass args as one tuple in the list
        #could implement a function that handles the params and does this: film, kind, lock = params /n get_urls(film,kind,lock)

    #ALTERNATIVELYYYY
    #you need a lock so that you can actually have it show stuff in order: 
    # threads = [threading.Thread(target=get_urls, args=(film6,x,print_lock)) for x in ['characters','planets','starships','vehicles','species']]

    log.stop_timer('Total Time To complete')
    log.write(f'There were {end_call_count} calls to the server')

if __name__ == "__main__":
    main()

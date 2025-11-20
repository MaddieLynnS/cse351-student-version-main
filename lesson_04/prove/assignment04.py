"""
Course    : CSE 351
Assignment: 04
Student   : Maddie Smith :)

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}

where:

name: name of the city
recno: record number starting from 0

"""

import time
from common import *

from cse351 import *

import queue

THREADS = 300
WORKERS = 10
MAX_QUEUE_SIZE = 10
RECORDS_TO_RETRIEVE = 5000  # Don't change


# ---------------------------------------------------------------------------
def retrieve_weather_data(commands_queue: queue, weather_data_queue: queue, commands_q_available: threading.Semaphore, 
        consume_commands_q: threading.Semaphore, weather_q_available: threading.Semaphore, consume_weather_q: threading.Semaphore, b: threading.Barrier):
    # TODO - fill out this thread function (and arguments)
    #get data from data file, add it to the queue, queue is limited to ten so we'll need semaphores too
    while True:

        consume_commands_q.acquire()
        current_record = commands_queue.get()
        commands_q_available.release()

        if current_record is None:
            break

        # file = f"{current_record[0]}.dat"
        # #ChatGPT helped me with this part because I don't know how to read files, link to chat in assignment comments
        # with open(file, "r") as f:
        #     line = f.readline()
        #     data = ast.literal_eval(line)
        #maybe I'm supposed to get data from the server instead?
        #record = data[current_record[1]]

        name = current_record[0]
        record_num = current_record[1]

        #jk here is the right thing... took me way too long to figure it out...
        #record = get_data_from_server(current_record)
        #took me even longer to figure out that THIS is the right thing... sometimes life is not fun
        record = get_data_from_server(f'{TOP_API_URL}/record/{name}/{record_num}')

        # add info to weather queue
        weather_q_available.acquire()
        weather_data_queue.put(record)
        consume_weather_q.release()

    #re-add none so the queue will not break anything when it's empty
    commands_q_available.acquire()
    commands_queue.put(None)
    consume_commands_q.release()

    #FINALLY five hours in I figured out where the barrier goes! :)
    if b.wait() == 0:
        weather_q_available.acquire()
        weather_data_queue.put(None)
        consume_weather_q.release()



# ---------------------------------------------------------------------------
# TODO - Complete this class
class NOAA:

    def __init__(self):
        self.city_information = {}

    def add_city_information(self, record):
        city = record['city']
        city_info = (record['date'], record['temp'])
        if city not in self.city_information:
            self.city_information[city] = []
        self.city_information[city].append(city_info)

    def get_temp_details(self, city):
        total_temps = 0.0
        record_count = 0
        for record in self.city_information[city]:
            total_temps += record[1]
            record_count += 1
        return total_temps / record_count


# ---------------------------------------------------------------------------
# TODO - Create Worker threaded class
class Worker(threading.Thread):
    def __init__(self, weather_data_queue: queue, weather_q_available: threading.Semaphore, consume_weather_q: threading.Semaphore, noaa: NOAA):
        super().__init__()
        self.weather_data_queue = weather_data_queue
        self.weather_q_available = weather_q_available
        self.consume_weather_q = consume_weather_q
        self.noaa = noaa

    #functions like a consumer as well, so needs to re-add a none
    def run(self):
        while True:
            self.consume_weather_q.acquire()
            item = self.weather_data_queue.get()
            self.weather_q_available.release()

            if item is None:
                break

            self.noaa.add_city_information(item)

        self.weather_q_available.acquire()
        self.weather_data_queue.put(None)
        self.consume_weather_q.release()


# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f'{TOP_API_URL}/start')

    print(data)

    # Get all cities number of records
    print('Retrieving city details')
    city_details = {}
    name = 'City'
    print(f'{name:>15}: Records')
    print('===================================')
    for name in CITIES:
        city_details[name] = get_data_from_server(f'{TOP_API_URL}/city/{name}')
        print(f'{name:>15}: Records = {city_details[name]['records']:,}')
    print('===================================')

    records = RECORDS_TO_RETRIEVE

    #for city in cities, for i in range to add stuff to queue?
    #Four semaphores
    #for loop of records
    #two queues
    #locks aren't needed either, they're just for data being changed
    #data in a queue is thread-safe
    #barrier in retrieve-weather-data?
    #no pipes or pools
    #run multiple times cuz it might turn up errors
    # TODO - Create any queues, pipes, locks, barriers you need
    commands_queue = queue.Queue()
    weather_data_queue = queue.Queue()
    commands_q_available = threading.Semaphore(MAX_QUEUE_SIZE)
    consume_commands_q = threading.Semaphore(0)
    weather_q_available = threading.Semaphore(MAX_QUEUE_SIZE)
    consume_weather_q = threading.Semaphore(0)
    b = threading.Barrier(THREADS)

    #ChatGPT said to put this before I start adding to the first queue, because it was deadlocking the other way
    # retrieve_weather_data is like my consumer functions, that's where we'll get()
    # I need to pass like everything to make sure data is getting taken from first queue and added to second queue correctly, plus barrier
    weather_threads = [threading.Thread(target=retrieve_weather_data, args=(commands_queue, weather_data_queue, commands_q_available, consume_commands_q, weather_q_available, consume_weather_q, b)) for _ in range(THREADS)]
    for t in weather_threads:
        t.start()

    #worker class getting called 
    worker_threads = []
    for t in range(WORKERS):
        t = Worker(weather_data_queue, weather_q_available, consume_weather_q, noaa)
        t.start()
        worker_threads.append(t)

    #Add initial records to the commands_queue
    print("Starting to add records...")
    for name in CITIES:
        for i in range(records):
            commands_q_available.acquire()
            commands_queue.put((name, i))
            consume_commands_q.release()

    commands_q_available.acquire()
    commands_queue.put(None)
    consume_commands_q.release()

    

    for t in weather_threads + worker_threads:
        t.join()

    


    # End server - don't change below
    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()


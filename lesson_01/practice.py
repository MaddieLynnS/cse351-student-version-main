from cse351 import *
import threading

def printHello(mutex, name):
    mutex.acquire()
    print(f"Hello world! {name}")
    mutex.release()

    # or you can use with mutex:

mutex = threading.Lock()
t = threading.Thread(target=printHello, args=(mutex, "Jeff"))
t.start()
mutex.acquire()
print("Cool stuff too")

# wait until the thread terminates
t.join()

print("This is the END!")


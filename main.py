import time
import os, signal
from multiprocessing import Process, Pipe
from threading import Thread

CLOSE_MESSAGE = "\n\n"

def child(conn, length=10, sleep_for_secs=1):
    cpid = os.getpid()
    print(f"child pid: {cpid}")
    for i in range(length):
        data = {
            "pid": cpid,
            "idx": i,
        }
        conn.send(data)
        time.sleep(sleep_for_secs)
    conn.send(CLOSE_MESSAGE)
    conn.close()
    os.kill(cpid, signal.SIGTERM)
    

def main_reader(read_pipe):
    while True:
        try:
            val = read_pipe.recv()
            if val == CLOSE_MESSAGE:
                break
            print(val)
        except Exception as e:
            print(e)


def main(num_of_workers=3, length=10, sleep_for_secs=1):
    print(f"parent pid: {os.getpid()}")

    workers = []

    for i in range(num_of_workers):
        read_conn, write_conn = Pipe()
        p = Process(target=child, args=(write_conn,))
        workers.append({
            "pipes": (read_conn,write_conn),
            "process": Process(target=child, args=(write_conn,length, sleep_for_secs))
        })

    readers = []
    for w in workers:
        w["process"].start()
        
        t = Thread(target=main_reader, args=(w["pipes"][0],))
        t.start()
        readers.append(t)

    for r in readers:
        r.join()
    
    for r in readers:
        r.join()

    Thread()
    
    for w in workers:
        w["pipes"][0].close()
        w["process"].join()
        w["process"].close()
        w["process"].close()


if __name__ == '__main__':
    num_of_workers = int(input("Enter number of workers (int): "))
    length = int(input("Enter length of work i.e. how long to work (int): "))
    sleep_for_secs = float(input("Enter sleep interval for each worker (float): "))

    main(num_of_workers, length, sleep_for_secs)
    
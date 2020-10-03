import time
import os
import signal
from multiprocessing import Process, Pipe
from threading import Thread

CLOSE_MESSAGE = "\n\n"


def child_func(conn, length=10, sleep_for_secs=1):
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


def pipe_reader(read_pipe):
    while True:
        try:
            val = read_pipe.recv()
            if val == CLOSE_MESSAGE:
                break
            print(val)
        except Exception as e:
            print(e)


def parent_func(num_of_children=3, length=10, sleep_for_secs=1):
    print(f"parent pid: {os.getpid()}")

    children = []
    for i in range(num_of_children):
        read_conn, write_conn = Pipe()
        children.append({
            "pipes": (read_conn, write_conn),
            "process": Process(
                target=child_func,
                args=(write_conn, length, sleep_for_secs)
            )
        })

    readers = []
    for child in children:
        child["process"].start()
        t = Thread(target=pipe_reader, args=(child["pipes"][0],))
        t.start()
        readers.append(t)

    for reader in readers:
        reader.join()

    for child in children:
        child["pipes"][0].close()
        child["process"].join()
        child["process"].close()
        child["process"].close()


if __name__ == '__main__':
    num_of_children = int(input("Enter number of workers (int): "))
    length = int(input("Enter length of work i.e. how long to work (int): "))
    sleep_for_secs = float(
        input("Enter sleep interval in seconds for each worker (float): "))

    parent_func(num_of_children, length, sleep_for_secs)

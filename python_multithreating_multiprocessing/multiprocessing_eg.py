import multiprocessing
import time

# CPU-bound task
def calculate_square(n):
    return n * n

def worker(start, end):
    for i in range(start, end):
        calculate_square(i)

if __name__ == "__main__":
    start = time.time()
    processes = []
    
    for i in range(4):  # 4 processes
        p = multiprocessing.Process(target=worker, args=(i*25000, (i+1)*25000))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    end = time.time()
    print(f"Time taken with multiprocessing: {end*1000 - start*1000} milli-seconds")

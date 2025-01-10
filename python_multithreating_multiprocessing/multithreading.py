import threading
import time

# CPU-bound task
def calculate_square(n):
    return n * n

def worker(start, end):
    for i in range(start, end):
        calculate_square(i)

start = time.time()
threads = []
for i in range(4):  # 4 threads
    t = threading.Thread(target=worker, args=(i*25000, (i+1)*25000))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

end = time.time()
print(f"Time taken with threading: {end*1000 - start*1000} milli-seconds")

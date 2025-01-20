Below is an example Python script for implementing a message queue in Inter-Process Communication (IPC) using the `multiprocessing` module.

### Example: Message Queue in IPC
```python
import multiprocessing
import time

def producer(queue):
    """Producer function to generate messages and put them in the queue."""
    for i in range(5):
        message = f"Message {i}"
        print(f"Producer: Putting {message} in queue")
        queue.put(message)
        time.sleep(1)  # Simulate delay

    # Send a signal to indicate the producer is done
    queue.put("DONE")
    print("Producer: Finished sending messages")

def consumer(queue):
    """Consumer function to process messages from the queue."""
    while True:
        message = queue.get()  # Get a message from the queue
        if message == "DONE":
            print("Consumer: Received DONE signal, exiting")
            break
        print(f"Consumer: Processed {message}")

if __name__ == "__main__":
    # Create a Queue object for IPC
    queue = multiprocessing.Queue()

    # Create producer and consumer processes
    producer_process = multiprocessing.Process(target=producer, args=(queue,))
    consumer_process = multiprocessing.Process(target=consumer, args=(queue,))

    # Start the processes
    producer_process.start()
    consumer_process.start()

    # Wait for processes to complete
    producer_process.join()
    consumer_process.join()

    print("Main: All processes completed")
```

### Explanation:
1. **Queue Object**:
   - A `multiprocessing.Queue` is used for passing messages between the producer and consumer processes.
   
2. **Producer Process**:
   - The producer generates messages and puts them into the queue.
   - A "DONE" message is sent at the end to indicate that the producer has finished its task.

3. **Consumer Process**:
   - The consumer retrieves and processes messages from the queue.
   - It exits when it receives the "DONE" signal.

4. **Main Function**:
   - The main function initializes the queue, creates the producer and consumer processes, starts them, and waits for them to finish using `join()`.

This structure ensures proper synchronization and communication between the producer and consumer processes using a message queue.
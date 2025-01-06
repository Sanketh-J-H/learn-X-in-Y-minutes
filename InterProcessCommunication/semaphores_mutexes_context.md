Certainly! Below are examples of using semaphores and mutexes in C. These examples demonstrate their usage in thread synchronization to control access to shared resources in a multithreading environment.

### 1. Example Using Semaphore (`semaphore.h`)

A **semaphore** is typically used to control access to a resource that has a limited number of instances (e.g., a pool of resources).

Here’s an example of using a semaphore to control access to a resource pool with multiple threads.

```c
#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>

#define MAX_RESOURCES 3  // Maximum resources available

sem_t sem;

void* thread_func(void* arg) {
    int thread_id = *((int*)arg);
    printf("Thread %d: Trying to access resource...\n", thread_id);

    // Wait (decrement the semaphore count)
    sem_wait(&sem);

    printf("Thread %d: Accessed resource!\n", thread_id);
    sleep(2);  // Simulate some work with the resource

    // Signal (increment the semaphore count)
    printf("Thread %d: Releasing resource...\n", thread_id);
    sem_post(&sem);

    return NULL;
}

int main() {
    pthread_t threads[5];
    int thread_ids[5];

    // Initialize the semaphore with the maximum number of resources
    sem_init(&sem, 0, MAX_RESOURCES);

    // Create threads
    for (int i = 0; i < 5; i++) {
        thread_ids[i] = i + 1;
        pthread_create(&threads[i], NULL, thread_func, &thread_ids[i]);
    }

    // Wait for all threads to finish
    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }

    // Destroy the semaphore
    sem_destroy(&sem);

    return 0;
}
```

### Explanation:
- **sem_wait(&sem)**: Decrements the semaphore's value. If the semaphore value is zero, the thread is blocked until it is positive again.
- **sem_post(&sem)**: Increments the semaphore's value, signaling that a resource has been released.

In this example, there are 5 threads, but only 3 resources available. Threads will need to wait for a resource to be released before they can proceed.

---

### 2. Example Using Mutex (`pthread.h`)

A **mutex** (short for mutual exclusion) is used to ensure that only one thread at a time can access a critical section of code. It is commonly used to prevent race conditions when multiple threads access shared resources.

Here’s an example of using a mutex to protect a shared resource (counter) between multiple threads:

```c
#include <stdio.h>
#include <pthread.h>

#define NUM_THREADS 5

pthread_mutex_t mutex;
int counter = 0;

void* increment_counter(void* arg) {
    pthread_mutex_lock(&mutex);  // Lock the mutex before accessing shared resource
    int temp = counter;
    temp++;
    counter = temp;
    printf("Counter: %d\n", counter);
    pthread_mutex_unlock(&mutex);  // Unlock the mutex

    return NULL;
}

int main() {
    pthread_t threads[NUM_THREADS];

    // Initialize the mutex
    pthread_mutex_init(&mutex, NULL);

    // Create multiple threads that will increment the counter
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, increment_counter, NULL);
    }

    // Wait for all threads to finish
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // Destroy the mutex
    pthread_mutex_destroy(&mutex);

    return 0;
}
```

### Explanation:
- **pthread_mutex_lock(&mutex)**: Acquires the lock on the mutex to ensure that only one thread can access the critical section at a time.
- **pthread_mutex_unlock(&mutex)**: Releases the lock on the mutex, allowing other threads to enter the critical section.
- **pthread_mutex_init(&mutex, NULL)**: Initializes the mutex before usage.
- **pthread_mutex_destroy(&mutex)**: Destroys the mutex once it's no longer needed.

In this example, multiple threads increment a shared counter. The mutex ensures that only one thread can modify the counter at a time, preventing race conditions.

---

### Summary:
- **Semaphores** are typically used when there are a fixed number of resources, and you want to control access to those resources across multiple threads.
- **Mutexes** are used to ensure exclusive access to a resource by only one thread at a time, which is useful when protecting critical sections of code from concurrent access.

Both techniques help ensure thread synchronization and prevent issues such as race conditions or deadlocks.
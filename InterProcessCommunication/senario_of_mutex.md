Certainly! Let's consider a **real-life scenario** where we can use a **mutex** for synchronization: **accessing a shared bank account**. 

### Scenario: Bank Account with Mutex

Imagine a scenario where multiple people (threads) are trying to deposit or withdraw money from a shared bank account. The bank account balance needs to be updated safely by only one thread at a time to prevent **race conditions**.

In this case, we will use a **mutex** to ensure that only one thread can modify the account balance at a time. This prevents the situation where two threads simultaneously try to update the balance, leading to an incorrect result.

### C Code Example:

```c
#include <stdio.h>
#include <pthread.h>

#define NUM_THREADS 5   // Number of threads attempting to modify the account balance

pthread_mutex_t account_mutex;  // Mutex to ensure exclusive access to the bank account
int account_balance = 1000;     // Initial balance in the bank account

// Function to simulate a deposit operation
void* deposit(void* arg) {
    pthread_mutex_lock(&account_mutex);  // Lock the mutex before modifying the balance
    int amount = *((int*)arg);
    
    printf("Depositing %d to account. Current balance: %d\n", amount, account_balance);
    account_balance += amount;
    printf("New balance after deposit: %d\n", account_balance);
    
    pthread_mutex_unlock(&account_mutex);  // Unlock the mutex after modification
    return NULL;
}

// Function to simulate a withdrawal operation
void* withdraw(void* arg) {
    pthread_mutex_lock(&account_mutex);  // Lock the mutex before modifying the balance
    int amount = *((int*)arg);
    
    if (account_balance >= amount) {
        printf("Withdrawing %d from account. Current balance: %d\n", amount, account_balance);
        account_balance -= amount;
        printf("New balance after withdrawal: %d\n", account_balance);
    } else {
        printf("Insufficient funds for withdrawal of %d. Current balance: %d\n", amount, account_balance);
    }
    
    pthread_mutex_unlock(&account_mutex);  // Unlock the mutex after modification
    return NULL;
}

int main() {
    pthread_t threads[NUM_THREADS];
    int amounts[NUM_THREADS] = {200, 150, 300, 400, 100};  // Deposit/withdraw amounts

    // Initialize the mutex
    pthread_mutex_init(&account_mutex, NULL);

    // Create threads for deposits and withdrawals
    for (int i = 0; i < NUM_THREADS; i++) {
        if (i % 2 == 0) {
            pthread_create(&threads[i], NULL, deposit, &amounts[i]);  // Even index threads perform deposit
        } else {
            pthread_create(&threads[i], NULL, withdraw, &amounts[i]);  // Odd index threads perform withdrawal
        }
    }

    // Wait for all threads to finish
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // Destroy the mutex
    pthread_mutex_destroy(&account_mutex);

    return 0;
}
```

### Explanation:

1. **Shared Resource (Bank Account)**:
   - We have a shared resource, `account_balance`, which represents the bank account balance.
   - Multiple threads are trying to either deposit or withdraw money from this account.

2. **Mutex (`account_mutex`)**:
   - The mutex `account_mutex` ensures that only one thread can modify the `account_balance` at a time.
   - This prevents race conditions, where two threads might read and modify the balance simultaneously, leading to incorrect results.

3. **Deposit and Withdraw Functions**:
   - The `deposit` function increases the account balance by a specified amount.
   - The `withdraw` function decreases the account balance if there are sufficient funds.
   
   Both functions are protected by the mutex to ensure that no two threads can modify the balance concurrently.

4. **Mutex Locking and Unlocking**:
   - Before modifying the account balance, the thread locks the mutex using `pthread_mutex_lock(&account_mutex)`.
   - After modifying the balance, the thread releases the lock using `pthread_mutex_unlock(&account_mutex)`.

5. **Threads**:
   - The `main` function creates several threads to simulate deposits and withdrawals. The threads perform their respective actions (deposit or withdraw) based on their index (even-indexed threads deposit, odd-indexed threads withdraw).

### Expected Output:
```
Depositing 200 to account. Current balance: 1000
New balance after deposit: 1200
Withdrawing 150 from account. Current balance: 1200
New balance after withdrawal: 1050
Depositing 300 to account. Current balance: 1050
New balance after deposit: 1350
Withdrawing 400 from account. Current balance: 1350
New balance after withdrawal: 950
Depositing 100 to account. Current balance: 950
New balance after deposit: 1050
```

### Key Points:
- **Mutex Locking and Unlocking**: The mutex ensures that only one thread can modify the bank account balance at any given time. When one thread locks the mutex, all other threads that try to lock the mutex are blocked until the first thread releases it.
  
- **Race Condition Prevention**: Without the mutex, if two threads tried to modify the balance at the same time, they might read the same initial value, and both could end up modifying the balance based on the same data, resulting in an incorrect final balance.

### Conclusion:
This example demonstrates how to use a **mutex** to ensure safe access to a shared resource (the bank account) in a multithreaded environment. The mutex guarantees that only one thread can modify the shared resource at any given time, preventing race conditions and ensuring consistency in the program’s output.
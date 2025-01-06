In C, **pipes** are a way to allow one process to communicate with another, using a mechanism that acts as a conduit for data. Pipes are commonly used for inter-process communication (IPC) in Unix-based operating systems like Linux. Here's how you can implement pipes in C:

### 1. **Creating a Pipe**
You can create a pipe using the `pipe()` system call. This creates a unidirectional data channel that can be used for communication between processes.

- **pipe()** takes an array of two file descriptors:
  - `pipefd[0]` for reading from the pipe.
  - `pipefd[1]` for writing to the pipe.

### 2. **Parent and Child Process Communication**
The common use of pipes involves a **parent process** creating a pipe, then **forking** a child process. The parent can write data to the pipe, and the child can read from it (or vice versa).

### Example: **Parent writes to Pipe and Child Reads from Pipe**
```c
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main() {
    int pipefd[2];
    pid_t pid;
    char message[] = "Hello from parent process!";
    char buffer[100];

    // Create the pipe
    if (pipe(pipefd) == -1) {
        perror("pipe failed");
        return 1;
    }

    // Fork a child process
    pid = fork();

    if (pid < 0) {
        // Error occurred in fork
        perror("fork failed");
        return 1;
    }

    if (pid > 0) {
        // Parent process: writes to the pipe
        close(pipefd[0]);  // Close the read end of the pipe
        write(pipefd[1], message, strlen(message) + 1);  // Write to the pipe
        close(pipefd[1]);  // Close the write end after writing

        printf("Parent sent message: %s\n", message);
    } else {
        // Child process: reads from the pipe
        close(pipefd[1]);  // Close the write end of the pipe
        read(pipefd[0], buffer, sizeof(buffer));  // Read from the pipe
        close(pipefd[0]);  // Close the read end after reading

        printf("Child received message: %s\n", buffer);
    }

    return 0;
}
```

### Key Points in the Code:
1. **pipefd[2]**: This array holds the file descriptors for the pipe.
2. **pipe()**: The `pipe(pipefd)` function creates the pipe, where `pipefd[0]` is the read end and `pipefd[1]` is the write end.
3. **fork()**: The `fork()` system call creates a new child process. After `fork()`, there are two processes (parent and child).
4. **close()**: Close the ends of the pipe that are not being used:
   - The **parent** process writes to the pipe, so it closes the read end (`pipefd[0]`).
   - The **child** process reads from the pipe, so it closes the write end (`pipefd[1]`).
5. **write() and read()**: The `write()` function writes data to the pipe, and the `read()` function reads data from the pipe.

### 3. **Pipes and Bidirectional Communication (Two-way Communication)**
For bidirectional communication, two pipes are needed, one for sending data from parent to child, and the other for sending data back from child to parent.

### Example: **Two-way Communication**
```c
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main() {
    int pipefd1[2], pipefd2[2];
    pid_t pid;
    char message_from_parent[] = "Hello from parent!";
    char message_from_child[] = "Hello from child!";
    char buffer[100];

    // Create two pipes
    if (pipe(pipefd1) == -1 || pipe(pipefd2) == -1) {
        perror("pipe failed");
        return 1;
    }

    pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return 1;
    }

    if (pid > 0) {
        // Parent process: writes to pipe1 and reads from pipe2
        close(pipefd1[0]);  // Close the read end of pipe1
        close(pipefd2[1]);  // Close the write end of pipe2

        write(pipefd1[1], message_from_parent, strlen(message_from_parent) + 1);  // Send to child
        close(pipefd1[1]);

        read(pipefd2[0], buffer, sizeof(buffer));  // Read from child
        printf("Parent received: %s\n", buffer);

        close(pipefd2[0]);
    } else {
        // Child process: reads from pipe1 and writes to pipe2
        close(pipefd1[1]);  // Close the write end of pipe1
        close(pipefd2[0]);  // Close the read end of pipe2

        read(pipefd1[0], buffer, sizeof(buffer));  // Read from parent
        printf("Child received: %s\n", buffer);

        write(pipefd2[1], message_from_child, strlen(message_from_child) + 1);  // Send to parent
        close(pipefd2[1]);

        close(pipefd1[0]);
    }

    return 0;
}
```

### Explanation of Two-Way Communication:
- We create **two pipes** (`pipefd1` and `pipefd2`) to enable bidirectional communication.
  - The **parent** writes to `pipefd1[1]` and reads from `pipefd2[0]`.
  - The **child** writes to `pipefd2[1]` and reads from `pipefd1[0]`.
- Each process closes the file descriptors that it does not use.
  
### Important Considerations:
- **Blocking behavior**: If a process tries to read from an empty pipe or write to a full pipe, it will block (wait) until data is available or space is freed.
- **Pipe size**: Pipes have a limited buffer size. If the buffer is full, writing will block until there is space available. Similarly, reading from an empty pipe will block.

### Conclusion:
Using pipes in C is a straightforward way to enable communication between processes. The examples above show how to use a pipe for one-way and two-way communication, and how to manage file descriptors to avoid unnecessary blocking. If you need more advanced IPC techniques (like named pipes, message queues, shared memory), you can explore other methods in Unix/Linux systems.
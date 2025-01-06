#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>

#define MAX_BUFFER 128

int main()
{
    int pipefd[2]; // file descriptors for the pipe
    pid_t pid;
    char buffer[MAX_BUFFER];

    // Create a pipe
    if (pipe(pipefd) == -1)
    {
        perror("Pipe failed");
        return 1;
    }

    pid = fork(); // Create a child process

    if (pid < 0)
    {
        // Fork failed
        perror("Fork failed");
        return 1;
    }

    if (pid > 0)
    {
        // Parent process
        close(pipefd[0]); // Close the read end of the pipe, not needed in parent

        // Write a message to the pipe
        const char *message = "Hello from parent process!";
        write(pipefd[1], message, strlen(message) + 1);
        printf("Parent sent message: %s\n", message);

        // Close the write end after sending
        close(pipefd[1]);

        // Wait for the child to finish
        wait(NULL);
    }
    else
    {
        // Child process
        close(pipefd[1]); // Close the write end of the pipe, not needed in child

        // Read from the pipe
        read(pipefd[0], buffer, MAX_BUFFER);
        printf("Child received message: %s\n", buffer);

        // Close the read end after receiving
        close(pipefd[0]);
    }

    return 0;
}

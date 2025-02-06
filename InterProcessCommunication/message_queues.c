#include <stdio.h>
#include <stdlib.h>
#include <mqueue.h>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pthread.h>

#include <signal.h>

#define PRINT_STATEMENT

#define NUM_QUEUES 4
#define CAN_FRAME_SIZE 10

// Queue names for different CAN message types
const char *QUEUE_NAMES[NUM_QUEUES] = {
    "/mq_hv_active",
    "/mq_b2v_st2",
    "/mq_b2v_st4",
    "/mq_b2v_st5",
};
static mqd_t mq_hv_active, mq_b2v_st2, mq_b2v_st4, mq_b2v_st5;

struct mq_attr mq_attributes = {
    .mq_flags = 0,
    .mq_maxmsg = 100, // Max messages per queue, this might cause the code to crash if the system limits are reached.
    /*Maximum messages per queue=messagesizekernel.msgmnb​=16384/1024​=16 */
    .mq_msgsize = CAN_FRAME_SIZE,
    .mq_curmsgs = 0};

void create_and_open_message_queues(void)
{

    // Open the message queue (create if it doesn't exist)
    mq_hv_active = mq_open(QUEUE_NAMES[0], O_CREAT | O_RDWR, 0644, &mq_attributes);
    if (mq_hv_active == (mqd_t)-1)
    {
        perror("mq_open");
        exit(1);
    }
    mq_b2v_st2 = mq_open(QUEUE_NAMES[1], O_CREAT | O_RDWR, 0644, &mq_attributes);
    if (mq_b2v_st2 == (mqd_t)-1)
    {
        perror("mq_open");
        exit(1);
    }
    mq_b2v_st4 = mq_open(QUEUE_NAMES[2], O_CREAT | O_RDWR, 0644, &mq_attributes);
    if (mq_b2v_st4 == (mqd_t)-1)
    {
        perror("mq_open");
        exit(1);
    }
    mq_b2v_st5 = mq_open(QUEUE_NAMES[3], O_CREAT | O_RDWR, 0644, &mq_attributes);
    if (mq_b2v_st5 == (mqd_t)-1)
    {
        perror("mq_open");
        exit(1);
    }
}

void send_message_to_queue(mqd_t mq)
{
    while (1)
    {
        // Send a message to the queue
        // char message[CAN_FRAME_SIZE];
        // snprintf(message, sizeof(message), "Hello from sender %d!", mq);
        // printf("Length of sent message %ld\n",strlen(message) + 1);
        int8_t message[CAN_FRAME_SIZE] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07}; // Message to send
        if (mq_send(mq, message, sizeof(message), 0) == -1)
        {
            perror("mq_send");
            exit(1);
        }
#ifdef PRINT_STATEMENT
        printf("Parent: Message sent successfully\n");
#endif
        sleep(0.01);
    }
}

void receive_message_from_queue(mqd_t mq)
{
    char buffer[CAN_FRAME_SIZE]; // Buffer to hold received messages

    while (1)
    {
        // Receive a message from the queue
        ssize_t bytes_received = mq_receive(mq, buffer, sizeof(buffer), NULL);
        if (bytes_received == -1)
        {
            perror("mq_receive");
            exit(1);
        }
        // Print the received message (for demonstration)
        printf("Child: Received message: ");
        for (int i = 0; i < bytes_received; i++)
        {
            printf("0x%02x ", buffer[i]);
        }
        printf("\n");
    }
}

// Wrapper functions for threading
void *send_to_queue(void *arg)
{
    mqd_t queue = *(mqd_t *)arg;
    send_message_to_queue(queue);
    return NULL;
}

void *receive_from_queue(void *arg)
{
    mqd_t queue = *(mqd_t *)arg;
    receive_message_from_queue(queue);
    return NULL;
}

// Function to be called when SIGINT is received (Ctrl+C)
void handle_sigint(int sig)
{
    printf("\nCaught signal %d (Ctrl+C pressed). Executing custom actions...\n", sig);

    // Execute your custom functions here
    // For example, a function to clean up resources or shutdown gracefully
    // cleanup_resources();
    printf("Cleaning up resources...\n");
    // Close the message queue
    if (mq_close(mq_hv_active) == -1)
    {
        perror("mq_close");
        exit(1);
    }
    if (mq_close(mq_b2v_st2) == -1)
    {
        perror("mq_close");
        exit(1);
    }
    if (mq_close(mq_b2v_st4) == -1)
    {
        perror("mq_close");
        exit(1);
    }
    if (mq_close(mq_b2v_st5) == -1)
    {
        perror("mq_close");
        exit(1);
    }

    // Unlink the message queue (removes it from the system)
    if (mq_unlink(QUEUE_NAMES[0]) == -1)
    {
        perror("mq_unlink 0");
        exit(1);
    }
    if (mq_unlink(QUEUE_NAMES[1]) == -1)
    {
        perror("mq_unlink 1");
        exit(1);
    }
    if (mq_unlink(QUEUE_NAMES[2]) == -1)
    {
        perror("mq_unlink 2");
        exit(1);
    }
    if (mq_unlink(QUEUE_NAMES[3]) == -1)
    {
        perror("mq_unlink 3");
        exit(1);
    }

    printf("Main thread finished.\n");
    // Optionally, exit the program
    exit(0); // You can choose whether to exit or not.
}

int main()
{
    pid_t pid;
    pthread_t thread1, thread2, thread3, thread4;

    // Register the signal handler
    if (signal(SIGINT, handle_sigint) == SIG_ERR)
    {
        perror("Error in signal handler registration");
        return 1;
    }

    create_and_open_message_queues();

    pid = fork(); // Create a child process

    if (pid < 0)
    {
        // Fork failed
        perror("Fork failed");
        return 1;
    }
    printf("Fork Created\n");

    if (pid > 0)
    {
        // Parent Process
        // Create threads to run the functions concurrently
        if (pthread_create(&thread1, NULL, send_to_queue, &mq_hv_active) != 0)
        {
            perror("Failed to create thread1");
            return 1;
        }
        if (pthread_create(&thread2, NULL, send_to_queue, &mq_b2v_st2) != 0)
        {
            perror("Failed to create thread2");
            return 1;
        }
        if (pthread_create(&thread3, NULL, send_to_queue, &mq_b2v_st4) != 0)
        {
            perror("Failed to create thread2");
            return 1;
        }
        if (pthread_create(&thread4, NULL, send_to_queue, &mq_b2v_st5) != 0)
        {
            perror("Failed to create thread2");
            return 1;
        }
        // Detach the threads
        if (pthread_detach(thread1) != 0)
        {
            perror("Failed to detach thread1");
            return 1;
        }
        if (pthread_detach(thread2) != 0)
        {
            perror("Failed to detach thread2");
            return 1;
        }
        if (pthread_detach(thread3) != 0)
        {
            perror("Failed to detach thread2");
            return 1;
        }
        if (pthread_detach(thread4) != 0)
        {
            perror("Failed to detach thread2");
            return 1;
        }
    }
    else
    {
        // child process
        // Create threads to run the functions concurrently
        if (pthread_create(&thread1, NULL, receive_from_queue, &mq_hv_active) != 0)
        {
            perror("Failed to create thread1");
            return 1;
        }
        if (pthread_create(&thread2, NULL, receive_from_queue, &mq_b2v_st2) != 0)
        {
            perror("Failed to create thread2");
            return 1;
        }
        if (pthread_create(&thread3, NULL, receive_from_queue, &mq_b2v_st4) != 0)
        {
            perror("Failed to create thread2");
            return 1;
        }
        if (pthread_create(&thread4, NULL, receive_from_queue, &mq_b2v_st5) != 0)
        {
            perror("Failed to create thread2");
            return 1;
        }
        // Detach the threads
        if (pthread_detach(thread1) != 0)
        {
            perror("Failed to detach thread1");
            return 1;
        }
        if (pthread_detach(thread2) != 0)
        {
            perror("Failed to detach thread2");
            return 1;
        }
        if (pthread_detach(thread3) != 0)
        {
            perror("Failed to detach thread2");
            return 1;
        }
        if (pthread_detach(thread4) != 0)
        {
            perror("Failed to detach thread2");
            return 1;
        }
    }
    // Keep the main thread alive to allow other threads to run
    while (1)
    {
        sleep(1);
    }

    return 0;
}

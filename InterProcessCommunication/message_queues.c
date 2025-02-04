#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mqueue.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

#define QUEUE_NAME "/example_queue"

#define NUM_QUEUES 5
#define CAN_FRAME_SIZE 1024

// Queue names for different CAN message types
const char *QUEUE_NAMES[NUM_QUEUES] = {
    "/can_queue_0",
    "/can_queue_1",
    "/can_queue_2",
    "/can_queue_3",
    "/can_queue_4"};

struct mq_attr mq_attributes = {
    .mq_flags = 0,
    .mq_maxmsg = 10, // Max messages per queue
    .mq_msgsize = CAN_FRAME_SIZE,
    .mq_curmsgs = 0};

void send_message_to_queue(void)
{
    mqd_t mq;
    // Open the message queue (create if it doesn't exist)
    mq = mq_open(QUEUE_NAMES[0], O_CREAT | O_RDWR, 0644, &mq_attributes);
    if (mq == (mqd_t)-1)
    {
        perror("mq_open");
        exit(1);
    }

    while (1)
    {
        // Send a message to the queue
        char message[] = "Hello from sender!";
        if (mq_send(mq, message, strlen(message) + 1, 0) == -1)
        {
            perror("mq_send");
            exit(1);
        }
        printf("Sent: %s\n", message);
        sleep(0.01);
    }
}

void receive_message_from_queue(void)
{
    char buffer[CAN_FRAME_SIZE]; // Buffer to hold received messages
    
    mqd_t mq;
    // Open the message queue (create if it doesn't exist)
    mq = mq_open(QUEUE_NAMES[0], O_CREAT | O_RDWR, 0644, &mq_attributes);
    if (mq == (mqd_t)-1)
    {
        perror("mq_open");
        exit(1);
    }

    while (1)
    {
        // Receive a message from the queue
        ssize_t bytes_received = mq_receive(mq, buffer, sizeof(buffer), NULL);
        if (bytes_received == -1)
        {
            perror("mq_receive");
            exit(1);
        }
        printf("Received: %s\n", buffer);
    }
}

int main()
{
    pid_t pid;

    // // Set attributes for the message queue
    // attr.mq_flags = 0;
    // attr.mq_maxmsg = 10;   // Maximum number of messages
    // attr.mq_msgsize = 256; // Maximum message size
    // attr.mq_curmsgs = 0;

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
        send_message_to_queue();
    }
    else
    {
        // Child process
        receive_message_from_queue();
    }

    return 0;
}

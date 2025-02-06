#include "message_queues.h"

const char *QUEUE_NAMES[NUM_QUEUES] = {
    "/mq_hv_active",
    "/mq_b2v_st2",
    "/mq_b2v_st4",
    "/mq_b2v_st5",
};

struct mq_attr mq_attributes = {
    .mq_flags = 0,
    .mq_maxmsg = 100, // Max messages per queue, this might cause the code to crash if the system limits are reached.
    /*Maximum messages per queue=messagesizekernel.msgmnb​=16384/1024​=16 */
    .mq_msgsize = CAN_DATA_FRAME_SIZE,
    .mq_curmsgs = 0};

mqd_t message_queue_descripters[NUM_QUEUES];

void create_and_open_message_queues(void)
{

// Open the message queue (create if it doesn't exist)
#define NUM_QUEUES 4

    for (int i = 0; i < NUM_QUEUES; i++)
    {
        message_queue_descripters[i] = mq_open(QUEUE_NAMES[i], O_CREAT | O_RDWR, 0644, &mq_attributes);
        if (message_queue_descripters[i] == (mqd_t)-1)
        {
            perror("mq_open");
            exit(1);
        }
    }
}


void send_message_to_queue(mqd_t mq,uint8_t *data)
{

    if (mq_send(mq, data, 8, 0) == -1)
    {
        perror("mq_send");
        exit(1);
    }
#ifdef PRINT_STATEMENT
    printf("Parent: Message sent successfully\n");
#endif
}

void send_message_to_queue_hv_active(uint8_t *data)
{

    if (mq_send(message_queue_descripters[0], data, 8, 0) == -1)
    {
        perror("mq_send");
        exit(1);
    }
#ifdef PRINT_STATEMENT
    printf("Parent: Message sent successfully\n");
#endif
}

void send_message_to_queue_b2v_st2(uint8_t *data)
{

    if (mq_send(message_queue_descripters[1], data, 8, 0) == -1)
    {
        perror("mq_send");
        exit(1);
    }
#ifdef PRINT_STATEMENT
    printf("Parent: Message sent successfully\n");
#endif
}

void send_message_to_queue_b2v_st4(uint8_t *data)
{
    if (mq_send(message_queue_descripters[2], data, 8, 0) == -1)
    {
        perror("mq_send");
        exit(1);
    }
#ifdef PRINT_STATEMENT
    printf("Parent: Message sent successfully\n");
#endif
}

void send_message_to_queue_b2v_st5(uint8_t *data)
{

    if (mq_send(message_queue_descripters[3], data, 8, 0) == -1)
    {
        perror("mq_send");
        exit(1);
    }
#ifdef PRINT_STATEMENT
    printf("Parent: Message sent successfully\n");
#endif
}

void receive_message_from_queue(mqd_t mq,uint8_t *data)
{
    // Receive a message from the queue
    ssize_t bytes_received = mq_receive(mq, data, CAN_DATA_FRAME_SIZE, NULL);
    if (bytes_received == -1)
    {
        perror("mq_receive");
        exit(1);
    }

// Print the received message (for demonstration)
#ifdef PRINT_STATEMENT
    printf("Child: Received message: ");
    for (int i = 0; i < bytes_received; i++)
    {
        printf("0x%02x ", data[i]);
    }
    printf("\n");
#endif
}

void receive_message_from_queue_hv_active(uint8_t *data)
{
    // Receive a message from the queue
    ssize_t bytes_received = mq_receive(message_queue_descripters[0], data, CAN_DATA_FRAME_SIZE, NULL);
    if (bytes_received == -1)
    {
        perror("mq_receive");
        exit(1);
    }

// Print the received message (for demonstration)
#ifdef PRINT_STATEMENT
    printf("Child: Received message: ");
    for (int i = 0; i < bytes_received; i++)
    {
        printf("0x%02x ", data[i]);
    }
    printf("\n");
#endif
}

void receive_message_from_queue_b2v_st2(uint8_t *data)
{
    // Receive a message from the queue
    ssize_t bytes_received = mq_receive(message_queue_descripters[1], data, CAN_DATA_FRAME_SIZE, NULL);
    if (bytes_received == -1)
    {
        perror("mq_receive");
        exit(1);
    }
// Print the received message (for demonstration)
#ifdef PRINT_STATEMENT
    printf("Child: Received message: ");
    for (int i = 0; i < bytes_received; i++)
    {
        printf("0x%02x ", data[i]);
    }
    printf("\n");
#endif
}

void receive_message_from_queue_b2v_st4(uint8_t *data)
{
    // Receive a message from the queue
    ssize_t bytes_received = mq_receive(message_queue_descripters[2], data, CAN_DATA_FRAME_SIZE, NULL);
    if (bytes_received == -1)
    {
        perror("mq_receive");
        exit(1);
    }
// Print the received message (for demonstration)
#ifdef PRINT_STATEMENT
    printf("Child: Received message: ");
    for (int i = 0; i < bytes_received; i++)
    {
        printf("0x%02x ", data[i]);
    }
    printf("\n");
#endif
}

void receive_message_from_queue_b2v_st5(uint8_t *data)
{
    // Receive a message from the queue
    ssize_t bytes_received = mq_receive(message_queue_descripters[3], data, CAN_DATA_FRAME_SIZE, NULL);
    if (bytes_received == -1)
    {
        perror("mq_receive");
        exit(1);
    }
// Print the received message (for demonstration)
#ifdef PRINT_STATEMENT
    printf("Child: Received message: ");
    for (int i = 0; i < bytes_received; i++)
    {
        printf("0x%02x ", data[i]);
    }
    printf("\n");
#endif
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
    if (mq_close(message_queue_descripters[0]) == -1)
    {
        perror("mq_close");
        exit(1);
    }
    if (mq_close(message_queue_descripters[1]) == -1)
    {
        perror("mq_close");
        exit(1);
    }
    if (mq_close(message_queue_descripters[2]) == -1)
    {
        perror("mq_close");
        exit(1);
    }
    if (mq_close(message_queue_descripters[3]) == -1)
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
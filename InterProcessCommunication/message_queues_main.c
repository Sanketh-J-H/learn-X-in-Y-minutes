#include "message_queues.h"

int main()
{
    pid_t pid;
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
        uint8_t data0[8] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07};
        send_message_to_queue(message_queue_descripters[0], data0);
        uint8_t data1[8] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
        send_message_to_queue(message_queue_descripters[1], data1);
        uint8_t data2[8] = {0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01};
        send_message_to_queue(message_queue_descripters[2], data2);
        uint8_t data3[8] = {0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02};
        send_message_to_queue(message_queue_descripters[3], data3);
    }
    else
    {
        // Child Process
        uint8_t data0[8], data1[8], data2[8], data3[8];
        receive_message_from_queue(message_queue_descripters[0], data0);
        receive_message_from_queue(message_queue_descripters[1], data1);
        receive_message_from_queue(message_queue_descripters[2], data2);
        receive_message_from_queue(message_queue_descripters[3], data3);
    }

    while (1)
    {
        sleep(1);
    }

    return 0;
}
#ifndef MESSAGE_QUEUES
#define MESSAGE_QUEUES

#include <stdio.h>
#include <stdlib.h>
#include <mqueue.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <signal.h>


#define PRINT_STATEMENT
#define NUM_QUEUES 4
#define CAN_DATA_FRAME_SIZE 8

/**
 * @brief Queue names for different CAN messages.
 *
 * This array holds the descriptors of message queues used for handling
 * different types of CAN messages. These queues facilitate inter-process 
 * communication between different system components.
 *
 * Queue names: 
 * 0 - "/mq_hv_active"
 * 1 - "/mq_b2v_st2"
 * 2 - "/mq_b2v_st4"
 * 3 - "/mq_b2v_st5"
 */
extern const char *QUEUE_NAMES[NUM_QUEUES];

extern mqd_t message_queue_descripters[NUM_QUEUES];

void create_and_open_message_queues(void);

void send_message_to_queue(mqd_t mq,uint8_t *data);

void receive_message_from_queue(mqd_t mq,uint8_t *data);

void handle_sigint(int sig);

#endif
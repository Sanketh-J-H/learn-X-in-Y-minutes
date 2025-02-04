#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main() {
    int sockfd;
    int recv_buf_size = 4096;  // 4 KB for receive buffer
    int send_buf_size = 4096;  // 4 KB for send buffer
    int optval;
    socklen_t optlen = sizeof(optval);

    // Create a socket (IPv4, TCP)
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    // Set receive buffer size (SO_RCVBUF)
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &recv_buf_size, sizeof(recv_buf_size)) < 0) {
        perror("setsockopt SO_RCVBUF failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    // Set send buffer size (SO_SNDBUF)
    if (setsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &send_buf_size, sizeof(send_buf_size)) < 0) {
        perror("setsockopt SO_SNDBUF failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    // Get and print the current receive buffer size
    if (getsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &optval, &optlen) < 0) {
        perror("getsockopt SO_RCVBUF failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }
    printf("Receive buffer size set to: %d bytes\n", optval);

    // Get and print the current send buffer size
    if (getsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &optval, &optlen) < 0) {
        perror("getsockopt SO_SNDBUF failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }
    printf("Send buffer size set to: %d bytes\n", optval);

    // Close the socket
    close(sockfd);
    return 0;
}

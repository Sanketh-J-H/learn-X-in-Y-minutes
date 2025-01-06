#include <stdio.h>

// Define an enum for traffic light states
typedef enum
{
    RED,
    YELLOW,
    GREEN
} TrafficLightState;

// Function to print the current state of the traffic light
void printTrafficLightState(TrafficLightState state)
{
    switch (state)
    {
    case RED:
        printf("The traffic light is RED.\n");
        break;
    case YELLOW:
        printf("The traffic light is YELLOW.\n");
        break;
    case GREEN:
        printf("The traffic light is GREEN.\n");
        break;
    default:
        printf("Unknown state.\n");
        break;
    }
}

int main()
{
    TrafficLightState currentState = RED;

    // Print the current state
    printTrafficLightState(currentState);

    // Change the state
    currentState = GREEN;
    printTrafficLightState(currentState);

    return 0;
}

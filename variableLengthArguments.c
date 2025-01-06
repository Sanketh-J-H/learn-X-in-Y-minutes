#include <stdio.h>
#include <stdarg.h>
#include <stdint.h>

// Function to calculate the sum of variable-length arguments
int sum(int count, ...)
{
    int total = 0;
    va_list args; // Declare a variable to hold the list of arguments

    // Initialize the va_list with the number of arguments
    va_start(args, count);

    // Loop through the arguments and sum them
    for (int i = 0; i < count; i++)
    {
        total += va_arg(args, char); // Retrieve the next argument
    }

    // Clean up the va_list
    va_end(args);

    return total;
}

int main()
{
    // Call the sum function with different numbers of arguments
    printf("Sum of 3, 5, 7: %d\n", sum(3, 3, 5, 7));             // Output: 15
    printf("Sum of 10, 20: %d\n", sum(2, 10, 20));               // Output: 30
    printf("Sum of 1, 2, 3, 4, 5: %d\n", sum(5, 1, 2, 3, 4, 5)); // Output: 15

    return 0;
}

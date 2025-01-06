#include <stdio.h>

void count_calls()
{
    static int call_count = 0; // This variable persists across calls
    call_count++;
    printf("This function has been called %d times.\n", call_count);
}

int main()
{
    for (int count = 1; count < 11; count++)
    {
        count_calls();
    }
    return 0;
}
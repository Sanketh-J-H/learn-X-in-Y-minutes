#include <stdio.h>
#include <assert.h>
#include <stdint.h>

void processValue(int value)
{
    // Assert that the value should not be negative
    assert(value >= 0);

    // Process the value (for example, print it)
    printf("Processing value: %d\n", value);
}

int main()
{
    processValue(10); // This is fine
    // processValue(-5); // This will trigger the assertion
    uint32_t a = 0x01 << 31;
    size_t size = sizeof(a);
    printf("%d\n", (unsigned char)257);
    printf("%d\n", __SCHAR_MAX__);
    printf("%zu\n", SIZE_MAX);
    printf("%d\n", INT8_MAX);
    printf("%ld\n", INT64_MAX);
    return 0;
}
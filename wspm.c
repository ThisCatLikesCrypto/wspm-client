#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
    // Construct the command to execute the Python script
    char command[1000] = "python3 wspm.py";
    for (int i = 1; i < argc; i++) {
        strcat(command, " ");
        strcat(command, argv[i]);
    }

    // Execute the command and store return value
    int returnCode = system(command);
    
    return 0;
}

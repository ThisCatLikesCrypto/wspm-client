#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
    // Check if the command is "wspm new"
    int useNewPackage = (argc >= 2 && strcmp(argv[1], "new") == 0);

    // Construct the command to execute the appropriate Python script
    char command[1000];
    if (useNewPackage) {
        strcpy(command, "python3 wspm-newpackage.py");
        // Add remaining arguments if any
        for (int i = 3; i < argc; i++) {
            strcat(command, " ");
            strcat(command, argv[i]);
        }
    } else {
        strcpy(command, "python3 wspm.py");
        for (int i = 1; i < argc; i++) {
            strcat(command, " ");
            strcat(command, argv[i]);
        }
    }

    // Execute the command and store return value
    int returnCode = system(command);
    
    return returnCode;
}

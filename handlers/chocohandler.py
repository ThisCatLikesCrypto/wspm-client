import pyuac
import os
import sys
from userinteraction import pront

packageName = sys.argv[1]

def chocoinstall():
    pront("Using Chocolatey")
    if not pyuac.isUserAdmin():
        pront("Running as admin (prompts for admin)")
        pyuac.runAsAdmin()
    else:        
        os.system("choco install " + packageName)
        input()

if __name__ == "__main__":
    chocoinstall()
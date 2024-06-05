import pyuac
import os
import sys
from userinteraction import pront

packageName = sys.argv[2]

def chocoinstall():
    pront("Using Chocolatey")
    if not pyuac.isUserAdmin():
        pront("Running as admin (prompts for admin)")
        pyuac.runAsAdmin()
    else:        
        os.system("choco install " + packageName)
        input()

def chocoremove():
    pront("Using chocolatey")
    if not pyuac.isUserAdmin():
        pront("Running as admin (prompts for admin)")
        pyuac.runAsAdmin()
    else:
        os.system("choco uninstall " + packageName)
        input()

if __name__ == "__main__":
    if sys.argv[1] == "install":
        chocoinstall()
    elif sys.argv[1] == "remove":
        chocoremove()
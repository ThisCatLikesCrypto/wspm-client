import os
import subprocess
from handlers.userinteraction import *

def install(packageName):
    if input("Do you want to use winget? y/n ").lower() == "y":
        pront("Using winget", BLUE)
        os.system("winget install " + packageName)
    elif input("Do you want to use chocolatey (requires admin)? y/n ").lower() == "y":
        subprocess.call("python3 handlers/chocohandler.py install " + packageName) #test this cuz im not sure what the paths are relative to

def remove(packageName):
    if input("Do you want to use winget? y/n ").lower() == "y":
        pront("Using winget", BLUE)
        os.system("winget remove " + packageName)
    elif input("Do you want to use chocolatey (requires admin)? y/n ").lower() == "y":
        subprocess.call("python3 handlers/chocohandler.py remove " + packageName)
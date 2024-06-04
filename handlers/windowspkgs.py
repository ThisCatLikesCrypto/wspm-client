import os
import subprocess
from handlers.userinteraction import *

def install(packageName):
    if input("Do you want to use winget? y/n ").lower() == "y":
        pront("Using winget", BLUE)
        os.system("winget install " + packageName)
    elif input("Do you want to use chocolatey (requires admin)? y/n ").lower() == "y":
        subprocess.call("python3 handlers/chocohandler.py " + packageName) #test this cuz im not sure what the paths are relative to

#add remove
import os
import distro
from handlers.userinteraction import *

def apt(packageName, command, get=""):
    pront("Using apt")
    os.system(f"sudo apt{get} {command} {packageName}")

def install(packageName):
    distname = distro.name()
    if distname.startswith("Deb") or "untu" in distname or "mint" in distname:
        if input("Do you want to use apt? y/n ").lower() == "y":
            apt(packageName, "install", "-get")

def remove(packageName):
    distname = distro.name()
    if distname.startswith("Deb") or "untu" in distname or "mint" in distname:
        if input("Do you want to remove with apt? y/n ").lower() == "y":
            apt(packageName, "remove")
#!/usr/bin/python3
#TODO: Add backup secondary and ability to recognise when package was installed as a dependency, plus which source it was installed from

import requests
import json
import os
import sys
import shutil
import zipfile
import time
import platform
import semver
import re
from handlers.userinteraction import *

#Define variables
listURL = "https://wspm.pages.dev/package-list"
secondaryListURL = "https://thiscatlikescrypto.github.io/wspm2/package-list"
backupListURL = "https://cdn.jsdelivr.net/gh/ThisCatLikesCrypto/wspm@main/package-list"
baseURL = "https://cdn.jsdelivr.net/gh/ThisCatLikesCrypto/wspm@main/packages/"
secondaryBaseURL = "https://thiscatlikescrypto.github.io/wspm2/packages/"
backupBaseURL = "https://wspm.pages.dev/packages/"
yestoall = False
usebackup = False
wspmcwd = os.getcwd()

if os.name == "nt":
    installdir = os.getenv('USERPROFILE') + "\\.wspm"
else:
    installdir = os.path.expanduser('~') + "/.wspm"

#Check that the packages dir exists, if not create it and inform the user
if os.path.isdir(os.path.join(installdir, "packages")):
    pass
else:
    print("No packagedir found. Making "+os.path.join(installdir, "packages"))
    os.mkdir(installdir)
    os.mkdir(os.path.join(installdir, "packages"))

packagedir = os.path.join(installdir, "packages")
packageListDir = os.path.join(installdir, "package-list")
packageListDir2 = os.path.join(installdir, "secondary-list")

def checka(inp):
    global yestoall
    if inp == "a":
        yestoall = True
        return True
    elif inp == "y":
        return True
    else:
        return False

def indexExists(dictionary: dict, argument: str):
    try:
        dictionary[argument]
        return True
    except:
        return False

def metaSave(path, data):
    data = str(data).replace("'", '"')
    try:
        with open(os.path.join(path, "metadata"), 'w') as f:
            f.write(data)
    except OSError:
        os.mkdir(path)
        with open(os.path.join(path, "metadata"), 'w') as f:
            f.write(data)

def saveFile(path, data, name=None):
    if name is not None:
        directory = os.path.join(path, name)
    else:
        directory = path
    try:
        with open(directory, 'wb') as f:
            f.write(data)
    except OSError:
        os.mkdir(path)
        with open(directory, 'wb') as f:
            f.write(data)

def convertToSemver(non_semver_str):
    # Default semver parts
    major, minor, patch = 0, 0, 0

    # Extract numbers from the non-semver string
    numbers = re.findall(r'\d+', str(non_semver_str))
    
    if len(numbers) > 0:
        major = int(numbers[0])
    if len(numbers) > 1:
        minor = int(numbers[1])
    if len(numbers) > 2:
        patch = int(numbers[2])
    
    # Construct the semver string
    semver_str = f"{major}.{minor}.{patch}"
    
    return semver_str

def readCurrentVersion(packageName: str) -> dict:
    try:
        with open(os.path.join(packagedir, packageName, "metadata"), "r") as f:
            data = f.read()
            return json.loads(data)["version"]
    except FileNotFoundError:
        return 0

def hasNewerVer(packageName, metadata):
    installedver = convertToSemver(readCurrentVersion(packageName))
    if semver.compare(str(installedver), str(convertToSemver(metadata['version']))) == -1:
        return True
    else:
        return False

def download_file(url: str, backupType="base"):
    if url.endswith("/packages/"):
        pront("Tried to retrieve packages/ (bug, need to figure out why in future)", YELLOW)
    else:
        pront("Retrieving " + url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            pront("Failed to download file.", RED)
    except requests.exceptions.ConnectionError:
        global usebackup
        if usebackup == 0 and backupType == "base":
            usebackup = 1
            try:
                download_file(backupBaseURL)
            except requests.exceptions.ConnectionError:
                pass
        elif usebackup == 0 and backupType == "list":
            usebackup = 1
            try:
                download_file(backupListURL)
            except requests.exceptions.ConnectionError:
                pass
        pront("Failed to connect. Maybe check your internet connection?", RED)
        sys.exit()

def getMetadata(name: str, baseURL=baseURL) -> list:
    rawdl = download_file(f"{baseURL}{name}/metadata")
    return json.loads(rawdl)

def extract(packageName):
    pront("Extracting " + packageName, BLUE)
    path = os.path.join(packagedir, packageName)
    files = os.listdir(path)
    for file in files:
        if file.endswith('.zip'):
            file_path = os.path.join(path, file)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(path)
                pront("Extracted "+ file_path, GREEN)
            os.remove(file_path)


def installp2(metadata, packageName, baseURL):
    pront(f"Files: {metadata['files']}")
    files = metadata['files'].split(", ")
    oses = metadata['oses'].split(", ")
    if os.name not in oses and "universal" not in oses:
        raise OSError("Unsupported OS for this package.")
    try:
        metaSave(os.path.join(packagedir, packageName), metadata)
        for file in files:
            dl = download_file(f"{baseURL}{packageName}/{file}")
            saveFile(os.path.join(packagedir, packageName), dl, file)
        extract(packageName)
    except Exception as e:
        pront("Installation failed.\n " + str(e), RED)

def installp3(metadata, packageName):
    if indexExists(metadata, 'installscript'):
        pront("Running program's installer...")
        os.chdir(os.path.join(packagedir, packageName))
        os.system(f"python3 {metadata['installscript']}")
        os.chdir(wspmcwd)
    pront(f"Installation of package {packageName} success!", GREEN)

def installDeps(deps, packages, dependentPackage, baseURL): 
    pront("Found dependencies", GREEN)
    pront(f"Dependencies: {deps}", BLUE)
    deps = deps.split(", ")
    for dep in deps:
        metadata = getMetadata(dep)
        if hasNewerVer(dep, metadata):
            if dependentPackage in metadata["dependencies"]:
                pront(f"Circular dependency: {dependentPackage} is a dependency of {dep}", RED)
                pront(f"Attempting to go directly to installp2. This means {dep} will be installed without ANY dependencies, except {dependentPackage}", YELLOW)
                installp2(metadata, dep, baseURL)
                installp3(metadata, dep)
            else: 
                install(dep, packages, metadata, baseURL)
        else:
            pront(f"Dependency {dep} is already up to date.", GREEN)

def install(packageName: str, packages, metadata=None, baseURL=baseURL):
    pront("Downloading " + packageName)
    try:
        if metadata is None:
            metadata = getMetadata(packageName, baseURL)
        else:
            pass
        deps = metadata['dependencies']
        if not hasNewerVer(packageName, metadata):
            pront(f"Package {packageName} is already up to date.", GREEN)
            if deps !="":
                depUpdate = input("However, dependencies were found. Do you want to update dependencies? (Y/N): ").lower()
                if depUpdate == "y":
                    installDeps(deps, packages, packageName, baseURL)
        elif deps != "":
            installDeps(deps, packages, packageName, baseURL)
            installp2(metadata, packageName, baseURL)
            installp3(metadata, packageName)
        else:
            installp2(metadata, packageName, baseURL)
            installp3(metadata, packageName)
    except Exception as e:
        match e:
            case json.decoder.JSONDecodeError:
                pront("Not found or some other JSON ded", RED)
                pront("Abort", RED)
            case _:
                pront(e, RED)

def locate(packageName: str, packages):
    try:
        packages2 = checkCache(packageListDir2, secondaryListURL).removeprefix("b").replace("'", "").split(", ")
    except TypeError:
        packages2 = ['uwu']
    if packageName.startswith("-"):
        pass
    elif packageName in packages:
        install(packageName, packages)
    elif packageName in packages2:
        install(packageName, packages, metadata=None, baseURL=secondaryBaseURL)
    else:
        pront(f"Package {packageName} not found in wspm repositories.", RED)
        if os.name == "nt":
            from handlers import windowspkgs
            windowspkgs.install(packageName)
        elif platform.uname().system == "Linux":
            from handlers import linuxpkgs
            linuxpkgs.install(packageName)
        elif platform.uname().system == "Darwin":
            if input("Do you want to use homebrew? y/n ").lower() == "y":
                pront("Using brew")
                os.system("brew install "+ packageName)

def update(packageName):
    pront("Downloading " + packageName)
    try:
        metadata = getMetadata(packageName)
        if not hasNewerVer(packageName, metadata):
            pront(f"Package {packageName} is already up to date.", GREEN)
        else:
            installp2(metadata, packageName)
    except Exception as e:
         match e:
            case json.decoder.JSONDecodeError:
                pront("Not found or some other JSON ded", RED)
                pront("Abort", RED)
            case _:
                pront(e, RED)

def deletePackage(packageName):
    pront("Removing " + packageName)
    try:
        shutil.rmtree(os.path.join(packagedir, packageName))
        pront("Remove success!", GREEN)
    except Exception as e:
        pront("Failed", RED)
        pront(e, RED)

def remove(packageName):
    if packageName in os.listdir(packagedir):
        if yestoall:
            deletePackage(packageName)
        else:
            selection = checka(input(f"Are you sure you want to remove {packageName}? ((y)es/(n)o)/(a)ll): ").lower())
            if selection:
                deletePackage(packageName)
            else:
                pront("Abort", RED)
    else:
        if os.name == "nt":
            from handlers import windowspkgs
            windowspkgs.remove(packageName)
        elif platform.uname().system == 'Linux':
            from handlers import linuxpkgs
            linuxpkgs.remove(packageName)
        elif platform.uname().system == "Darwin":
            print("homebrew remove not implemented")


def checkCache(file_path, isSecondary=False, force=False):
    if isSecondary:
        fileURL = secondaryListURL
        packageListDirectory = packageListDir2
    else:
        fileURL = listURL
        packageListDirectory = packageListDir
    try:
        if os.path.exists(file_path):
            last_modified = os.path.getmtime(file_path)
            current_time = time.time()
            time_difference = current_time - last_modified
            if not time_difference < 3600 or force:
                data = download_file(f"{fileURL}")
                try:
                    saveFile(file_path, data)
                except TypeError:
                    data = download_file(f"{fileURL}")
                    saveFile(file_path, data)
        else:
            data = download_file(f"{fileURL}")
            saveFile(file_path, data)
    except:
        data = download_file(f"{fileURL}")
        saveFile(file_path, data)

    with open(packageListDirectory, "rb") as f:
        return f.read()

def processCMD():
    try:
        return sys.argv[1]
    except IndexError:
        return input("Type a command\n")

def processPKG():
    if sys.argv[2:] != []:
        return sys.argv[2:]
    else:
        return input("Type a package/packages\n").split(" ")

def wspmhelp():
    pront("Welcome to wspm help.")
    pront("List of commands:")
    pront("    install:", GREEN)
    pront("        syntax: 'wspm install <package/packages>'\n        desc: installs specified packages", BLUE2)
    pront("    remove:", GREEN)
    pront("        syntax: 'wspm remove <package/packages>'\n        desc: removes specified packages", BLUE2)
    pront("    update:", GREEN)
    pront("        syntax 'wspm update'\n        desc: updates all packages", BLUE2)
    pront("    test:", GREEN)
    pront("        syntax 'wspm test'\n        desc: installs and uninstalls allwords and test_dependency", BLUE2)

def cmdselector(packages: str, cmd):
    match cmd:
        case "install":
            packageNames = processPKG()
            for packageName in packageNames:
                locate(packageName, packages)
        case "remove":
            packageNames = processPKG()
            for packageName in packageNames:
                remove(packageName)
        case "list":
            pront("Listing...")
            packageNames = os.listdir(packagedir)
            pront("Done!", GREEN)
            for hahaStrGoBrrr in packageNames:
                pront(hahaStrGoBrrr)
        case "update":
            packageNames = os.listdir(packagedir)
            for packageName in packageNames:
                update(packageName)
        case "test":
            install("allwords", packages)
            remove("allwords")
            remove("test_dependency")
        case "help":
            wspmhelp()
        case _:
            print("no command")


def main():
    cmd = processCMD()
    cmdselector(packages, cmd)
    
if "--force-pkglist-upd" in sys.argv:
    plainPackageStr = checkCache(packageListDir, listURL, True)
    plainPackageStr2 = checkCache(packageListDir2, secondaryListURL, True)
else:
    plainPackageStr = checkCache(packageListDir)
    plainPackageStr2 = checkCache(packageListDir2, secondaryListURL, True)
packages = str(plainPackageStr).removeprefix("b").replace("'", "").split(", ")
packages2 = str(plainPackageStr2).removeprefix("b").replace("'", "").split(", ")

if __name__ == "__main__":
    main()

import requests
import json
import os
import sys
import shutil
import zipfile
import time

#Define variables
listURL = "https://wspm.pages.dev/package-list"
baseURL = "https://wspm.pages.dev/packages/"

GREEN = '\033[38;5;120m'
RED = '\033[38;5;203m'
BLUE = '\033[38;5;117m' #dark-aqua sort of colour

if os.name == "nt":
    installdir = os.getenv('LOCALAPPDATA') + "\\wspm"
else:
    installdir = os.path.expanduser('~') + "/wspm"

#Check that the packages dir exists, if not create it and inform the user
if os.path.isdir(os.path.join(installdir, "packages")):
    pass
else:
    print("No packagedir found. Making "+os.path.join(installdir, "packages"))
    os.mkdir(installdir)
    os.mkdir(os.path.join(installdir, "packages"))

packagedir = os.path.join(installdir, "packages")
packageListDir = os.path.join(installdir, "package-list")

def producesyntaxed(text, color='\033[38;5;120m'):
    try:
        sys.stdout.write(color + text + '\033[0m')
    except:
        print(text)

def pront(stufftoprint, colour=BLUE):
    stufftoprint = str(stufftoprint) + "\n"
    if __name__ == "__main__":
        producesyntaxed(stufftoprint, colour)
    else:
        producesyntaxed(f"{__name__}: {stufftoprint}", BLUE)

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

def readCurrentVersion(packageName: str) -> dict:
    try:
        with open(os.path.join(packagedir, packageName, "metadata"), "r") as f:
            data = f.read()
            return json.loads(data)["version"]
    except FileNotFoundError:
        return 0

def download_file(url: str):
    pront("Retrieving " + url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            pront("Failed to download file.", RED)
    except requests.exceptions.ConnectionError:
        print("Failed to connect. Maybe check your internet connection?")
        return None

def getMetadata(name: str) -> list:
    return json.loads(download_file(f"{baseURL}{name}/metadata"))

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


def installp2(metadata, packageName):
    files = metadata['files'].split(", ")
    oses = metadata['oses'].split(", ")
    if os.name not in oses and "universal" not in oses:
        raise OSError("Unsupported os for this package.")
    try:
        metaSave(os.path.join(packagedir, packageName), metadata)
        for file in files:
            dl = download_file(f"{baseURL}{packageName}/{file}")
            saveFile(os.path.join(packagedir, packageName), dl, file)
        extract(packageName)
    except Exception as e:
        pront("Installation failed.\n " + str(e), RED)

def installDeps(deps):
    pront("Found dependencies!", GREEN)
    pront(f"Dependencies: {deps}", BLUE)
    deps = deps.split(", ")
    for dep in deps:
        pront("Downloading " + dep)
        metadata = getMetadata(dep)
        if float(metadata["version"]) > float(readCurrentVersion(dep)):
            installp2(metadata, dep)
        else:
            pront(f"Dependency {dep} is already up to date", GREEN)

def install(packageName, packages):
    if packageName in packages:
        pront("Downloading " + packageName)
        try:
            metadata = getMetadata(packageName)
            deps = metadata['dependencies']
            if not float(metadata["version"]) > float(readCurrentVersion(packageName)):
                pront(f"Package {packageName} is already up to date.", GREEN)
                if deps !="":
                    depUpdate = input("However, dependencies were found. Do you want to update dependencies? (Y/N): ").lower()
                    if depUpdate == "y":
                        installDeps(deps)
            elif deps != "":
                installDeps(deps)
                installp2(metadata, packageName)
            else:
                installp2(metadata, packageName)
            pront(f"Installation of package {packageName} success!", GREEN)
        except Exception as e:
            match e:
                case json.decoder.JSONDecodeError:
                    pront("Not found or some other JSON ded", RED)
                    pront("Abort", RED)
                case _:
                    pront(e, RED)
    else:
        pront(f"Package {packageName} does not exist", RED)

def deletePackage(packageName):
    pront("Removing " + packageName)
    try:
        shutil.rmtree(os.path.join(packagedir, packageName))
        pront("Remove success!", GREEN)
    except Exception as e:
        pront("Failed", RED)
        pront(e, RED)

def remove(packageName):
    if input(f"Are you sure you want to remove {packageName}? (Y/N) ").lower() == "y":
        deletePackage(packageName)
    else:
        pront("Abort", RED)


def checkCache(file_path, fileURL=listURL):
    if os.path.exists(file_path):
        # Get the last modification time of the file
        last_modified = os.path.getmtime(file_path)
        # Get the current time
        current_time = time.time()
        # Calculate the difference in seconds
        time_difference = current_time - last_modified
        # Check if the file has been updated in the last hour (3600 seconds)
        if time_difference > 3600:
            data = download_file(f"{fileURL}")
            try:
                saveFile(file_path, data)
            except TypeError:
                data = download_file(f"{fileURL}")
                saveFile(file_path, data)
    else:
        data = download_file(f"{fileURL}")
        saveFile(file_path, data)
    
    with open(packageListDir, "rb") as f:
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


def main():
    plainPackageStr = checkCache(packageListDir)
    packages = str(plainPackageStr).removeprefix("b").replace("'", "").split(", ")
    match processCMD():
        case "install":
            packageNames = processPKG()
            for packageName in packageNames:
                install(packageName, packages)
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
        case _:
            print("no command")

if __name__ == "__main__":
    main()
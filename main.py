import requests
import json
import os
import shutil
import zipfile
from socket import gaierror

#Define variables
listURL = "https://wspm.pages.dev/package-list"
baseURL = "https://wspm.pages.dev/packages/"

if os.name == "nt":
    installdir = os.getenv('LOCALAPPDATA') + "\\wspm"
else:
    installdir = os.path.expanduser('~') + "/wspm"

#Check that the packages dir exists, if not create it and inform the user
if os.path.isdir(os.path.join(installdir, "packages")):
    pass
else:
    print("No packagedir found. Making "+os.path.join(installdir, "packages"))
    os.mkdir(os.path.join(installdir, "packages"))

packagedir = os.path.join(installdir, "packages")

def pront(stufftoprint):
    if __name__ == "__main__":
        print(stufftoprint)
    else:
        print(f"{__name__}: {stufftoprint}")

def metaSave(path, data):
    data = str(data).replace("'", '"')
    try:
        with open(os.path.join(path, "metadata"), 'w') as f:
            f.write(data)
    except OSError:
        os.mkdir(path)
        with open(os.path.join(path, "metadata"), 'w') as f:
            f.write(data)

def saveFile(path, name, data):
    try:
        with open(os.path.join(path, name), 'wb') as f:
            f.write(data)
    except OSError:
        os.mkdir(path)
        with open(os.path.join(path, name), 'wb') as f:
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
    except gaierror:
        response.status_code == 404
    if response.status_code == 200:
        return response.content
    else:
        pront("Failed to download file.")

def getMetadata(name: str) -> list:
    return json.loads(download_file(f"{baseURL}{name}/metadata"))

def extract(packageName):
    print("Extracting " + packageName)
    path = os.path.join(packagedir, packageName)
    files = os.listdir(path)
    for file in files:
        if file.endswith('.zip'):
            file_path = os.path.join(path, file)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(path)
                print("Extracted "+ file_path)
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
            saveFile(os.path.join(packagedir, packageName), file, dl)
        extract(packageName)
        pront("Installation success!")
    except Exception as e:
        pront("Installation failed.\n " + str(e))

def installDeps(deps):
    pront("Found dependencies!")
    pront(deps)
    deps = deps.split(", ")
    for dep in deps:
        pront("Downloading " + dep)
        metadata = getMetadata(dep)
        if float(metadata["version"]) > float(readCurrentVersion(dep)):
            installp2(metadata, dep)
        else:
            pront(f"Dependency {dep} is already up to date")

def install(packageName, packages):
    if packageName in packages:
        pront("Downloading " + packageName)
        try:
            metadata = getMetadata(packageName)
            deps = metadata['dependencies']
            if not float(metadata["version"]) > float(readCurrentVersion(packageName)):
                pront(f"Package {packageName} is already up to date.")
                if deps !="":
                    depUpdate = input("However, dependencies were found. Do you want to update dependencies? (Y/N): ").lower()
                    if depUpdate == "y":
                        installDeps(deps)
            elif deps != "":
                installDeps(deps)
                installp2(metadata, packageName)
            else:
                installp2(metadata, packageName)
        except Exception as e:
            match e:
                case json.decoder.JSONDecodeError:
                    pront("Not found or some other JSON ded")
                    pront("Abort")
                case _:
                    pront(e)
    else:
        print(packages)
        pront(f"Package {packageName} does not exist")

def deletePackage(packageName):
    pront("Removing " + packageName)
    try:
        shutil.rmtree(os.path.join(packagedir, packageName))
        pront("Remove success!")
    except Exception as e:
        pront("Failed")
        pront(e)

def remove(packageName):
    if input(f"Are you sure you want to remove {packageName}? (Y/N) ").lower() == "y":
        deletePackage(packageName)
    else:
        pront("Abort")

    
command = input("Type a command\n")
packageNames = input("Type a package/packages\n").split(" ")
match command:
    case "install":
        packages = str(download_file(listURL)).removeprefix("b").replace("'", "").split(", ")
        for packageName in packageNames:
            install(packageName, packages)
    case "remove":
        for packageName in packageNames:
            remove(packageName)
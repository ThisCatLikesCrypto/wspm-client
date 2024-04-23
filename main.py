import requests
import json
import os
import shutil

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

def readCurrentVersion(packageName):
    try:
        with open(os.path.join(os.getcwd(), "packages", packageName, "metadata"), "r") as f:
            data = f.read()
            return json.loads(data)["version"]
    except FileNotFoundError:
        return 0

def download_file(url):
    print("Retrieving " + url)
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to download file.")

def getMetadata(name) -> list:
    return json.loads(download_file(f"https://wspm.pages.dev/{name}/metadata"))

def installp2(metadata, packageName):
    files = metadata['files'].split(",")
    oses = metadata['oses'].split(",")
    if os.name not in oses and "universal" not in oses:
        raise OSError("Unsupported os for this package.")
    if float(metadata["version"]) > float(readCurrentVersion(packageName)):
        try:
            metaSave(os.path.join(os.getcwd(), "packages", packageName), metadata)
            for file in files:
                dl = download_file(f"https://wspm.pages.dev/{packageName}/{file}")
                saveFile(os.path.join(os.getcwd(), "packages", packageName), file, dl)
            print("Installation success!")
        except Exception as e:
            print("Installation failed.\n " + str(e))
    else:
        print(f"Package {packageName} is already up to date")

def install(packageName):
    print("Installing " + packageName)
    try:
        metadata = getMetadata(packageName)
        installp2(metadata, packageName)
    except Exception as e:
        match e:
            case json.decoder.JSONDecodeError:
                print("Not found or some other JSON ded")
                print("Abort")
            case OSError:
                print("Unsupported OS.")

def deletePackage(packageName):
    print("Removing " + packageName)
    try:
        shutil.rmtree(os.path.join(os.getcwd(), "packages", packageName))
        print("Remove success!")
    except Exception as e:
        print("Failed")
        print(e)

def remove(packageName):
    if input("Are you sure you want to do this? (Y/N) ").lower() == "y":
        deletePackage(packageName)
    else:
        print("Abort")

    
command = input("type a command\n")
packageName = input("type a package\n")
match command:
    case "install":
        install(packageName)
    case "remove":
        remove(packageName) 
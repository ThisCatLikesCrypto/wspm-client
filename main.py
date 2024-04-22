import requests
import json
import os

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
    with open(os.path.join(os.getcwd(), "packages", packageName, "metadata"), "r") as f:
        data = f.read()
        return json.loads(data)["version"]

def download_file(url):
    print("Retrieving " + url)
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to download file.")

def getMetadata(name) -> list:
    return json.loads(download_file("https://wspm.pages.dev/" + name + "/metadata"))

def install(packageName):
    print("Installing " + packageName)
    metadata = getMetadata(packageName)
    files = metadata['files'].split(",")
    if metadata["version"] > readCurrentVersion(packageName):
        try:
            metaSave(os.path.join(os.getcwd(), "packages", packageName), metadata)
            for file in files:
                dl = download_file(f"https://wspm.pages.dev/{packageName}/{file}")
                saveFile(os.path.join(os.getcwd(), "packages", packageName), file, dl)
            print("Installation success!")
        except Exception as e:
            print("Installation failed. " + str(e))
    else:
        print(f"Package {packageName} is already up to date.")
    

install(input("type a package\n"))